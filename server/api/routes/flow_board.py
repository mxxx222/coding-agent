"""
Flow Board API routes for workflow visualization
Provides data for flow board visualization similar to Kanban boards but with flow-based progression
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, date
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

# Pydantic models for Flow Board API
class FlowBoardItem(BaseModel):
    """Represents a work item in the flow board"""
    id: uuid.UUID
    title: str
    description: Optional[str]
    type: str
    status: str
    priority: str
    assignee_id: Optional[uuid.UUID]
    assignee_name: Optional[str]
    reporter_id: uuid.UUID
    reporter_name: str
    project_id: uuid.UUID
    project_name: str
    parent_id: Optional[uuid.UUID]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    due_date: Optional[date]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    metadata: Dict[str, Any]

class FlowBoardColumn(BaseModel):
    """Represents a column (stage) in the flow board"""
    id: str
    title: str
    status: str
    color: Optional[str]
    order: int
    item_count: int
    items: List[FlowBoardItem]

class FlowBoardRelationship(BaseModel):
    """Represents relationships between work items"""
    source_id: uuid.UUID
    target_id: uuid.UUID
    relationship_type: str
    description: Optional[str]

class FlowBoardResponse(BaseModel):
    """Complete flow board data structure"""
    columns: List[FlowBoardColumn]
    relationships: List[FlowBoardRelationship]
    total_items: int
    filters_applied: Dict[str, Any]
    generated_at: datetime

# Default flow board columns (stages) - can be customized per project
DEFAULT_COLUMNS = [
    {"id": "backlog", "title": "Backlog", "status": "open", "color": "#6b7280", "order": 1},
    {"id": "todo", "title": "To Do", "status": "open", "color": "#3b82f6", "order": 2},
    {"id": "in_progress", "title": "In Progress", "status": "in_progress", "color": "#f59e0b", "order": 3},
    {"id": "review", "title": "Review", "status": "in_progress", "color": "#8b5cf6", "order": 4},
    {"id": "done", "title": "Done", "status": "closed", "color": "#10b981", "order": 5},
]

async def get_flow_board_data(
    user_id: uuid.UUID,
    project_id: Optional[uuid.UUID] = None,
    assignee_id: Optional[uuid.UUID] = None,
    type_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    tags_filter: Optional[List[str]] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = 1000
) -> FlowBoardResponse:
    """Get flow board data with optional filters"""
    conn = await get_db_connection()
    try:
        # Build base query for work items
        query = """
            SELECT
                wi.*,
                p.name as project_name,
                u_assignee.name as assignee_name,
                u_reporter.name as reporter_name
            FROM work_items wi
            JOIN projects p ON wi.project_id = p.id
            LEFT JOIN users u_assignee ON wi.assignee_id = u_assignee.id
            JOIN users u_reporter ON wi.reporter_id = u_reporter.id
            WHERE p.user_id = $1
        """
        values = [user_id]
        param_count = 2

        # Apply filters
        if project_id:
            query += f" AND wi.project_id = ${param_count}"
            values.append(project_id)
            param_count += 1

        if assignee_id:
            query += f" AND wi.assignee_id = ${param_count}"
            values.append(assignee_id)
            param_count += 1

        if type_filter:
            query += f" AND wi.type = ${param_count}"
            values.append(type_filter)
            param_count += 1

        if priority_filter:
            query += f" AND wi.priority = ${param_count}"
            values.append(priority_filter)
            param_count += 1

        if tags_filter:
            query += f" AND wi.tags && ${param_count}"
            values.append(tags_filter)
            param_count += 1

        if date_from:
            query += f" AND wi.created_at >= ${param_count}"
            values.append(datetime.combine(date_from, datetime.min.time()))
            param_count += 1

        if date_to:
            query += f" AND wi.created_at <= ${param_count}"
            values.append(datetime.combine(date_to, datetime.max.time()))
            param_count += 1

        query += f" ORDER BY wi.created_at DESC LIMIT ${param_count}"
        values.append(limit)

        # Execute work items query
        work_item_rows = await conn.fetch(query, *values)
        work_items = [dict(row) for row in work_item_rows]

        # Get relationships
        if work_items:
            item_ids = [str(wi['id']) for wi in work_items]
            placeholders = ','.join([f'${i+1}' for i in range(len(item_ids))])

            relationships_query = f"""
                SELECT wir.*
                FROM work_item_relationships wir
                WHERE wir.source_item_id IN ({placeholders})
                   OR wir.target_item_id IN ({placeholders})
            """
            rel_values = item_ids + item_ids
            relationship_rows = await conn.fetch(relationships_query, *rel_values)
            relationships = [dict(row) for row in relationship_rows]
        else:
            relationships = []

        # Organize items by status/column
        columns_data = {}
        for col in DEFAULT_COLUMNS:
            columns_data[col['status']] = {
                'id': col['id'],
                'title': col['title'],
                'status': col['status'],
                'color': col['color'],
                'order': col['order'],
                'items': []
            }

        # Group work items by status
        for item in work_items:
            status = item['status']
            if status in columns_data:
                columns_data[status]['items'].append(FlowBoardItem(**item))

        # Convert to list and sort by order
        columns = []
        for col_data in sorted(columns_data.values(), key=lambda x: x['order']):
            col_data['item_count'] = len(col_data['items'])
            columns.append(FlowBoardColumn(**col_data))

        # Convert relationships to response format
        flow_relationships = [
            FlowBoardRelationship(
                source_id=rel['source_item_id'],
                target_id=rel['target_item_id'],
                relationship_type=rel['relationship_type'],
                description=rel.get('description')
            )
            for rel in relationships
        ]

        # Build filters applied summary
        filters_applied = {
            "project_id": str(project_id) if project_id else None,
            "assignee_id": str(assignee_id) if assignee_id else None,
            "type": type_filter,
            "priority": priority_filter,
            "tags": tags_filter,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "limit": limit
        }

        return FlowBoardResponse(
            columns=columns,
            relationships=flow_relationships,
            total_items=len(work_items),
            filters_applied=filters_applied,
            generated_at=datetime.utcnow()
        )

    finally:
        await conn.close()

@router.get("/flowboard", response_model=FlowBoardResponse)
async def get_flow_board(
    project_id: Optional[uuid.UUID] = Query(None, description="Filter by project ID"),
    assignee_id: Optional[uuid.UUID] = Query(None, description="Filter by assignee ID"),
    type: Optional[str] = Query(None, regex=r'^(task|bug|feature|epic|story|issue|pr|commit|test|deployment)$', description="Filter by work item type"),
    priority: Optional[str] = Query(None, regex=r'^(low|medium|high|critical)$', description="Filter by priority"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    date_from: Optional[date] = Query(None, description="Filter items created from this date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter items created until this date (YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of items to return"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get flow board data for workflow visualization.

    Returns structured data with columns (stages) and work items organized by status,
    along with relationships between items. Supports filtering by project, user, type,
    priority, tags, and date ranges.

    The response is designed to be compatible with frontend visualization libraries
    like React Flow, D3.js, or custom Kanban board implementations.
    """
    try:
        # Validate date range
        if date_from and date_to and date_from > date_to:
            raise ValidationException(
                message="Date from cannot be after date to",
                details={"date_from": str(date_from), "date_to": str(date_to)}
            )

        # Get flow board data
        result = await get_flow_board_data(
            user_id=uuid.UUID(current_user['id']),
            project_id=project_id,
            assignee_id=assignee_id,
            type_filter=type,
            priority_filter=priority,
            tags_filter=tags,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )

        return result

    except ValidationException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error getting flow board data: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while retrieving flow board data"
        )