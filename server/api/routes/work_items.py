"""
Work Items API routes for managing work items and their relationships
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging
import uuid

from api.middleware.auth import get_current_user
from api.middleware.exceptions import (
    ServiceUnavailableException,
    ValidationException,
    TimeoutException
)
from database.schema import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class WorkItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    type: str = Field(..., regex=r'^(task|bug|feature|epic|story|issue|pr|commit|test|deployment)$')
    status: str = Field('open', regex=r'^(open|in_progress|blocked|closed|cancelled)$')
    priority: str = Field('medium', regex=r'^(low|medium|high|critical)$')
    assignee_id: Optional[uuid.UUID] = None
    parent_id: Optional[uuid.UUID] = None
    estimated_hours: Optional[float] = Field(None, ge=0, le=9999.99)
    actual_hours: Optional[float] = Field(None, ge=0, le=9999.99)
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkItemCreate(WorkItemBase):
    project_id: uuid.UUID

class WorkItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    type: Optional[str] = Field(None, regex=r'^(task|bug|feature|epic|story|issue|pr|commit|test|deployment)$')
    status: Optional[str] = Field(None, regex=r'^(open|in_progress|blocked|closed|cancelled)$')
    priority: Optional[str] = Field(None, regex=r'^(low|medium|high|critical)$')
    assignee_id: Optional[uuid.UUID] = None
    parent_id: Optional[uuid.UUID] = None
    estimated_hours: Optional[float] = Field(None, ge=0, le=9999.99)
    actual_hours: Optional[float] = Field(None, ge=0, le=9999.99)
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class WorkItemResponse(WorkItemBase):
    id: uuid.UUID
    project_id: uuid.UUID
    reporter_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

class WorkItemRelationshipBase(BaseModel):
    target_item_id: uuid.UUID
    relationship_type: str = Field(..., regex=r'^(depends_on|blocks|relates_to|duplicates|parent_of|child_of)$')
    description: Optional[str] = None

class WorkItemRelationshipCreate(WorkItemRelationshipBase):
    pass

class WorkItemRelationshipResponse(WorkItemRelationshipBase):
    id: uuid.UUID
    source_item_id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

class WorkItemCommentBase(BaseModel):
    content: str = Field(..., min_length=1)
    is_internal: bool = False

class WorkItemCommentCreate(WorkItemCommentBase):
    pass

class WorkItemCommentResponse(WorkItemCommentBase):
    id: uuid.UUID
    work_item_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# Database helper functions
async def get_work_item_by_id(item_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get a work item by ID with user access check."""
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow("""
            SELECT wi.*, p.user_id as project_owner_id
            FROM work_items wi
            JOIN projects p ON wi.project_id = p.id
            WHERE wi.id = $1 AND p.user_id = $2
        """, item_id, user_id)
        return dict(row) if row else None
    finally:
        await conn.close()

async def create_work_item(data: Dict[str, Any], user_id: uuid.UUID) -> Dict[str, Any]:
    """Create a new work item."""
    conn = await get_db_connection()
    try:
        # Verify project ownership
        project_owner = await conn.fetchval(
            "SELECT user_id FROM projects WHERE id = $1",
            data['project_id']
        )
        if not project_owner or str(project_owner) != str(user_id):
            raise HTTPException(status_code=403, detail="Access denied to project")

        # Create work item
        row = await conn.fetchrow("""
            INSERT INTO work_items (
                project_id, title, description, type, status, priority,
                assignee_id, reporter_id, parent_id, estimated_hours,
                actual_hours, due_date, tags, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            RETURNING *
        """, data['project_id'], data['title'], data['description'], data['type'],
             data['status'], data['priority'], data['assignee_id'], user_id,
             data['parent_id'], data['estimated_hours'], data['actual_hours'],
             data['due_date'], data['tags'], data['metadata'])

        return dict(row)
    finally:
        await conn.close()

async def update_work_item(item_id: uuid.UUID, data: Dict[str, Any], user_id: uuid.UUID) -> Dict[str, Any]:
    """Update a work item."""
    conn = await get_db_connection()
    try:
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1

        for field, value in data.items():
            if value is not None:
                update_fields.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1

        if not update_fields:
            raise ValidationException(message="No fields to update")

        update_fields.append(f"updated_at = ${param_count}")
        values.append(datetime.utcnow())
        param_count += 1

        query = f"""
            UPDATE work_items
            SET {', '.join(update_fields)}
            WHERE id = ${param_count} AND project_id IN (
                SELECT id FROM projects WHERE user_id = ${param_count + 1}
            )
            RETURNING *
        """
        values.extend([item_id, user_id])

        row = await conn.fetchrow(query, *values)
        if not row:
            raise HTTPException(status_code=404, detail="Work item not found or access denied")

        return dict(row)
    finally:
        await conn.close()

async def delete_work_item(item_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Delete a work item."""
    conn = await get_db_connection()
    try:
        result = await conn.execute("""
            DELETE FROM work_items
            WHERE id = $1 AND project_id IN (
                SELECT id FROM projects WHERE user_id = $2
            )
        """, item_id, user_id)
        return result.split()[-1] != '0'
    finally:
        await conn.close()

async def get_work_item_relationships(item_id: uuid.UUID, user_id: uuid.UUID) -> List[Dict[str, Any]]:
    """Get relationships for a work item."""
    conn = await get_db_connection()
    try:
        rows = await conn.fetch("""
            SELECT wir.*, wi.title as target_title, wi.type as target_type
            FROM work_item_relationships wir
            JOIN work_items wi ON wir.target_item_id = wi.id
            JOIN work_items source_wi ON wir.source_item_id = source_wi.id
            JOIN projects p ON source_wi.project_id = p.id
            WHERE wir.source_item_id = $1 AND p.user_id = $2
        """, item_id, user_id)
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def create_work_item_relationship(source_id: uuid.UUID, data: Dict[str, Any], user_id: uuid.UUID) -> Dict[str, Any]:
    """Create a relationship between work items."""
    conn = await get_db_connection()
    try:
        # Verify both items belong to user's projects
        items_valid = await conn.fetchval("""
            SELECT COUNT(*) FROM work_items wi1
            JOIN work_items wi2 ON wi2.id = $2
            JOIN projects p1 ON wi1.project_id = p1.id
            JOIN projects p2 ON wi2.project_id = p2.id
            WHERE wi1.id = $1 AND p1.user_id = $3 AND p2.user_id = $3
        """, source_id, data['target_item_id'], user_id)

        if not items_valid:
            raise HTTPException(status_code=403, detail="Access denied to work items")

        # Create relationship
        row = await conn.fetchrow("""
            INSERT INTO work_item_relationships (
                source_item_id, target_item_id, relationship_type, description, created_by
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING *
        """, source_id, data['target_item_id'], data['relationship_type'],
             data['description'], user_id)

        return dict(row)
    finally:
        await conn.close()

# API Routes
@router.post("/workitems", response_model=WorkItemResponse)
async def create_work_item_endpoint(
    item: WorkItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new work item."""
    try:
        # Validate input
        if not item.title or not item.title.strip():
            raise ValidationException(message="Title cannot be empty")

        if len(item.title) > 500:
            raise ValidationException(message="Title exceeds maximum length")

        if item.description and len(item.description) > 10000:
            raise ValidationException(message="Description exceeds maximum length")

        # Create work item
        data = item.dict()
        result = await create_work_item(data, uuid.UUID(current_user['id']))

        return WorkItemResponse(**result)

    except ValidationException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error creating work item: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while creating the work item"
        )

@router.get("/workitems", response_model=List[WorkItemResponse])
async def list_work_items(
    project_id: Optional[uuid.UUID] = None,
    type: Optional[str] = Query(None, regex=r'^(task|bug|feature|epic|story|issue|pr|commit|test|deployment)$'),
    status: Optional[str] = Query(None, regex=r'^(open|in_progress|blocked|closed|cancelled)$'),
    priority: Optional[str] = Query(None, regex=r'^(low|medium|high|critical)$'),
    assignee_id: Optional[uuid.UUID] = None,
    parent_id: Optional[uuid.UUID] = None,
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List work items with optional filters."""
    conn = await get_db_connection()
    try:
        # Build query with filters
        query = """
            SELECT wi.* FROM work_items wi
            JOIN projects p ON wi.project_id = p.id
            WHERE p.user_id = $1
        """
        values = [current_user['id']]
        param_count = 2

        if project_id:
            query += f" AND wi.project_id = ${param_count}"
            values.append(project_id)
            param_count += 1

        if type:
            query += f" AND wi.type = ${param_count}"
            values.append(type)
            param_count += 1

        if status:
            query += f" AND wi.status = ${param_count}"
            values.append(status)
            param_count += 1

        if priority:
            query += f" AND wi.priority = ${param_count}"
            values.append(priority)
            param_count += 1

        if assignee_id:
            query += f" AND wi.assignee_id = ${param_count}"
            values.append(assignee_id)
            param_count += 1

        if parent_id:
            query += f" AND wi.parent_id = ${param_count}"
            values.append(parent_id)
            param_count += 1

        if tags:
            query += f" AND wi.tags && ${param_count}"
            values.append(tags)
            param_count += 1

        query += f" ORDER BY wi.created_at DESC LIMIT ${param_count} OFFSET ${param_count + 1}"
        values.extend([limit, offset])

        rows = await conn.fetch(query, *values)
        return [WorkItemResponse(**dict(row)) for row in rows]

    finally:
        await conn.close()

@router.get("/workitems/{item_id}", response_model=WorkItemResponse)
async def get_work_item(
    item_id: uuid.UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific work item."""
    item = await get_work_item_by_id(item_id, uuid.UUID(current_user['id']))
    if not item:
        raise HTTPException(status_code=404, detail="Work item not found")
    return WorkItemResponse(**item)

@router.put("/workitems/{item_id}", response_model=WorkItemResponse)
async def update_work_item_endpoint(
    item_id: uuid.UUID,
    item: WorkItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a work item."""
    try:
        # Validate input
        update_data = item.dict(exclude_unset=True)
        if not update_data:
            raise ValidationException(message="No fields to update")

        if 'title' in update_data and (not update_data['title'] or len(update_data['title']) > 500):
            raise ValidationException(message="Invalid title")

        if 'description' in update_data and update_data['description'] and len(update_data['description']) > 10000:
            raise ValidationException(message="Description exceeds maximum length")

        # Update work item
        result = await update_work_item(item_id, update_data, uuid.UUID(current_user['id']))
        return WorkItemResponse(**result)

    except ValidationException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error updating work item {item_id}: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while updating the work item"
        )

@router.delete("/workitems/{item_id}")
async def delete_work_item_endpoint(
    item_id: uuid.UUID,
    current_user: dict = Depends(get_current_user)
):
    """Delete a work item."""
    try:
        deleted = await delete_work_item(item_id, uuid.UUID(current_user['id']))
        if not deleted:
            raise HTTPException(status_code=404, detail="Work item not found")
        return {"success": True, "message": "Work item deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error deleting work item {item_id}: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while deleting the work item"
        )

@router.get("/workitems/{item_id}/relationships", response_model=List[WorkItemRelationshipResponse])
async def get_work_item_relationships_endpoint(
    item_id: uuid.UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get relationships for a work item."""
    # Verify work item exists and user has access
    item = await get_work_item_by_id(item_id, uuid.UUID(current_user['id']))
    if not item:
        raise HTTPException(status_code=404, detail="Work item not found")

    relationships = await get_work_item_relationships(item_id, uuid.UUID(current_user['id']))
    return [WorkItemRelationshipResponse(**rel) for rel in relationships]

@router.post("/workitems/{item_id}/relationships", response_model=WorkItemRelationshipResponse)
async def create_work_item_relationship_endpoint(
    item_id: uuid.UUID,
    relationship: WorkItemRelationshipCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a relationship for a work item."""
    try:
        # Verify source work item exists and user has access
        item = await get_work_item_by_id(item_id, uuid.UUID(current_user['id']))
        if not item:
            raise HTTPException(status_code=404, detail="Work item not found")

        # Verify target work item exists and user has access
        target_item = await get_work_item_by_id(relationship.target_item_id, uuid.UUID(current_user['id']))
        if not target_item:
            raise HTTPException(status_code=404, detail="Target work item not found")

        # Prevent self-references
        if item_id == relationship.target_item_id:
            raise ValidationException(message="Cannot create relationship to self")

        # Create relationship
        data = relationship.dict()
        result = await create_work_item_relationship(item_id, data, uuid.UUID(current_user['id']))
        return WorkItemRelationshipResponse(**result)

    except ValidationException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error creating relationship for work item {item_id}: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while creating the relationship"
        )

@router.get("/workitems/{item_id}/dependencies")
async def get_work_item_dependencies(
    item_id: uuid.UUID,
    direction: str = Query("both", regex=r'^(incoming|outgoing|both)$'),
    current_user: dict = Depends(get_current_user)
):
    """Get dependency graph for a work item."""
    conn = await get_db_connection()
    try:
        # Verify work item exists and user has access
        item = await get_work_item_by_id(item_id, uuid.UUID(current_user['id']))
        if not item:
            raise HTTPException(status_code=404, detail="Work item not found")

        # Build dependency query based on direction
        if direction == "outgoing":
            # Items this work item depends on (blocks)
            query = """
                SELECT wi.*, wir.relationship_type, wir.description
                FROM work_items wi
                JOIN work_item_relationships wir ON wi.id = wir.target_item_id
                JOIN projects p ON wi.project_id = p.id
                WHERE wir.source_item_id = $1 AND wir.relationship_type IN ('depends_on', 'blocks')
                AND p.user_id = $2
            """
        elif direction == "incoming":
            # Items that depend on this work item
            query = """
                SELECT wi.*, wir.relationship_type, wir.description
                FROM work_items wi
                JOIN work_item_relationships wir ON wi.id = wir.source_item_id
                JOIN projects p ON wi.project_id = p.id
                WHERE wir.target_item_id = $1 AND wir.relationship_type IN ('depends_on', 'blocks')
                AND p.user_id = $2
            """
        else:  # both
            # Union of both directions
            query = """
                (SELECT wi.*, wir.relationship_type, wir.description, 'outgoing' as direction
                 FROM work_items wi
                 JOIN work_item_relationships wir ON wi.id = wir.target_item_id
                 JOIN projects p ON wi.project_id = p.id
                 WHERE wir.source_item_id = $1 AND wir.relationship_type IN ('depends_on', 'blocks')
                 AND p.user_id = $2)
                UNION
                (SELECT wi.*, wir.relationship_type, wir.description, 'incoming' as direction
                 FROM work_items wi
                 JOIN work_item_relationships wir ON wi.id = wir.source_item_id
                 JOIN projects p ON wi.project_id = p.id
                 WHERE wir.target_item_id = $1 AND wir.relationship_type IN ('depends_on', 'blocks')
                 AND p.user_id = $2)
            """

        rows = await conn.fetch(query, item_id, uuid.UUID(current_user['id']))
        dependencies = [dict(row) for row in rows]

        return {
            "work_item_id": item_id,
            "dependencies": dependencies,
            "total_count": len(dependencies)
        }

    finally:
        await conn.close()

@router.get("/workitems/{item_id}/comments", response_model=List[WorkItemCommentResponse])
async def get_work_item_comments(
    item_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get comments for a work item."""
    conn = await get_db_connection()
    try:
        # Verify work item exists and user has access
        item = await get_work_item_by_id(item_id, uuid.UUID(current_user['id']))
        if not item:
            raise HTTPException(status_code=404, detail="Work item not found")

        rows = await conn.fetch("""
            SELECT * FROM work_item_comments
            WHERE work_item_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """, item_id, limit, offset)

        return [WorkItemCommentResponse(**dict(row)) for row in rows]

    finally:
        await conn.close()

@router.post("/workitems/{item_id}/comments", response_model=WorkItemCommentResponse)
async def create_work_item_comment(
    item_id: uuid.UUID,
    comment: WorkItemCommentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a comment on a work item."""
    conn = await get_db_connection()
    try:
        # Verify work item exists and user has access
        item = await get_work_item_by_id(item_id, uuid.UUID(current_user['id']))
        if not item:
            raise HTTPException(status_code=404, detail="Work item not found")

        # Validate input
        if not comment.content or not comment.content.strip():
            raise ValidationException(message="Comment content cannot be empty")

        if len(comment.content) > 5000:
            raise ValidationException(message="Comment exceeds maximum length")

        # Create comment
        row = await conn.fetchrow("""
            INSERT INTO work_item_comments (work_item_id, author_id, content, is_internal)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """, item_id, uuid.UUID(current_user['id']), comment.content, comment.is_internal)

        return WorkItemCommentResponse(**dict(row))

    except ValidationException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error creating comment for work item {item_id}: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while creating the comment"
        )
    finally:
        await conn.close()