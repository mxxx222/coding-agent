"""
Workflow API routes for Unified DevOS
Flow Board, Work Items, Action Bus integration
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from services.action_bus import action_bus, EventType, ActionStatus
from services.integrations.github_extended import GitHubExtendedIntegration
from api.middleware.exceptions import (
    ServiceUnavailableException,
    ValidationException,
    TimeoutException
)

logger = logging.getLogger(__name__)

router = APIRouter()

class WorkItem(BaseModel):
    id: str
    type: str  # spec, issue, pr, commit, test, deployment, doc
    title: str
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: dict = {}

class FlowStatus(BaseModel):
    repo: str
    issues_open: int
    prs_open: int
    releases_total: int
    recent_prs: List[dict]
    timestamp: datetime

class ActionRequest(BaseModel):
    action_type: str
    payload: dict
    idempotency_key: Optional[str] = None

# Initialize GitHub integration
github = GitHubExtendedIntegration()

@router.get("/workitems", response_model=List[WorkItem])
async def list_work_items(
    type: Optional[str] = Query(None, description="Filter by type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000)
):
    """List work items with optional filters."""
    # Placeholder - would query from database
    return [
        WorkItem(
            id="wi_1",
            type="spec",
            title="Add user authentication",
            status="approved",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"owner": "team", "priority": "high"}
        )
    ]

@router.get("/flow/{owner}/{repo}", response_model=FlowStatus)
async def get_flow_status(owner: str, repo: str):
    """Get unified flow status for a repository."""
    try:
        # Validate input
        if not owner or not owner.strip():
            raise ValidationException(
                message="Repository owner cannot be empty",
                details={"field": "owner"}
            )

        if not repo or not repo.strip():
            raise ValidationException(
                message="Repository name cannot be empty",
                details={"field": "repo"}
            )

        # Get flow status with timeout protection
        try:
            status = await asyncio.wait_for(
                github.get_flow_status(owner, repo),
                timeout=30.0  # 30 second timeout for GitHub API
            )
        except asyncio.TimeoutError:
            logger.error(f"GitHub flow status request timed out for {owner}/{repo}")
            raise TimeoutException(
                message="Repository status request timed out",
                details={"operation": "get_flow_status", "repo": f"{owner}/{repo}"}
            )

        if "error" in status:
            raise ServiceUnavailableException(
                message="Failed to retrieve repository status",
                details={"repo": f"{owner}/{repo}", "error": status["error"]}
            )

        return FlowStatus(**status)

    except ValidationException:
        raise  # Re-raise validation errors
    except TimeoutException:
        raise  # Re-raise timeout errors
    except ServiceUnavailableException:
        raise  # Re-raise service unavailable errors
    except Exception as e:
        logger.critical(f"Unexpected error getting flow status for {owner}/{repo}: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while retrieving repository status",
            details={"error_type": type(e).__name__, "repo": f"{owner}/{repo}"}
        )

@router.get("/actions")
async def list_actions(status: Optional[str] = None, limit: int = 100):
    """List recent actions."""
    actions = action_bus.list_actions(
        status=ActionStatus[status.upper()] if status else None,
        limit=limit
    )
    return [action.__dict__ for action in actions]

@router.post("/actions")
async def execute_action(request: ActionRequest):
    """Execute an action via Action Bus."""
    try:
        # Validate input
        if not request.action_type or not request.action_type.strip():
            raise ValidationException(
                message="Action type cannot be empty",
                details={"field": "action_type"}
            )

        if not request.payload:
            raise ValidationException(
                message="Action payload cannot be empty",
                details={"field": "payload"}
            )

        # Execute action with timeout protection
        try:
            action = await asyncio.wait_for(
                action_bus.execute_action(
                    request.action_type,
                    request.payload,
                    request.idempotency_key
                ),
                timeout=60.0  # 60 second timeout for action execution
            )
        except asyncio.TimeoutError:
            logger.error(f"Action execution timed out: {request.action_type}")
            raise TimeoutException(
                message="Action execution timed out",
                details={"operation": "execute_action", "action_type": request.action_type}
            )

        return {
            "success": True,
            "action": action.__dict__
        }

    except ValidationException:
        raise  # Re-raise validation errors
    except TimeoutException:
        raise  # Re-raise timeout errors
    except Exception as e:
        logger.critical(f"Unexpected error executing action {request.action_type}: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while executing the action",
            details={"error_type": type(e).__name__, "action_type": request.action_type}
        )

@router.get("/actions/{action_id}")
async def get_action(action_id: str):
    """Get a specific action by ID."""
    action = action_bus.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action.__dict__

@router.get("/events")
async def list_events(limit: int = 100):
    """List recent events."""
    events = action_bus.get_events(limit=limit)
    return [event.__dict__ for event in events]

@router.post("/events")
async def emit_event(event_type: str, source: str, payload: dict):
    """Emit a new event."""
    try:
        # Validate input
        if not event_type or not event_type.strip():
            raise ValidationException(
                message="Event type cannot be empty",
                details={"field": "event_type"}
            )

        if not source or not source.strip():
            raise ValidationException(
                message="Event source cannot be empty",
                details={"field": "source"}
            )

        if not payload:
            raise ValidationException(
                message="Event payload cannot be empty",
                details={"field": "payload"}
            )

        # Validate event type
        try:
            event_type_enum = EventType[event_type.lower()]
        except KeyError:
            valid_event_types = [e.value for e in EventType]
            raise ValidationException(
                message=f"Unknown event type: {event_type}",
                details={"valid_types": valid_event_types, "provided": event_type}
            )

        # Emit event with timeout protection
        try:
            event_id = await asyncio.wait_for(
                action_bus.emit_event(event_type_enum, source, payload),
                timeout=30.0  # 30 second timeout for event emission
            )
        except asyncio.TimeoutError:
            logger.error(f"Event emission timed out: {event_type}")
            raise TimeoutException(
                message="Event emission timed out",
                details={"operation": "emit_event", "event_type": event_type}
            )

        return {
            "success": True,
            "event_id": event_id
        }

    except ValidationException:
        raise  # Re-raise validation errors
    except TimeoutException:
        raise  # Re-raise timeout errors
    except Exception as e:
        logger.critical(f"Unexpected error emitting event {event_type}: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while emitting the event",
            details={"error_type": type(e).__name__, "event_type": event_type}
        )

@router.get("/specs")
async def list_specs():
    """List all specs."""
    # Placeholder
    return []

@router.post("/specs")
async def create_spec(title: str, description: str):
    """Create a new spec."""
    try:
        # Validate input
        if not title or not title.strip():
            raise ValidationException(
                message="Spec title cannot be empty",
                details={"field": "title"}
            )

        if not description or not description.strip():
            raise ValidationException(
                message="Spec description cannot be empty",
                details={"field": "description"}
            )

        # Validate title length
        if len(title) > 200:
            raise ValidationException(
                message="Spec title exceeds maximum length",
                details={"max_length": 200, "actual_length": len(title)}
            )

        if len(description) > 5000:
            raise ValidationException(
                message="Spec description exceeds maximum length",
                details={"max_length": 5000, "actual_length": len(description)}
            )

        # Execute action with timeout protection
        try:
            action = await asyncio.wait_for(
                action_bus.execute_action(
                    "create_spec",
                    {"title": title, "description": description},
                    f"spec_{title}_{datetime.now().timestamp()}"
                ),
                timeout=30.0  # 30 second timeout for spec creation
            )
        except asyncio.TimeoutError:
            logger.error(f"Spec creation timed out: {title}")
            raise TimeoutException(
                message="Spec creation timed out",
                details={"operation": "create_spec", "title": title}
            )

        return {
            "success": True,
            "action": action.__dict__
        }

    except ValidationException:
        raise  # Re-raise validation errors
    except TimeoutException:
        raise  # Re-raise timeout errors
    except Exception as e:
        logger.critical(f"Unexpected error creating spec '{title}': {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred while creating the spec",
            details={"error_type": type(e).__name__, "title": title}
        )

