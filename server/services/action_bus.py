"""
Action Bus - Event and action orchestration for Unified DevOS
Handles: Event routing, action execution, state updates
"""

from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from enum import Enum
import asyncio
from dataclasses import dataclass, asdict

class ActionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EventType(Enum):
    SPEC_CREATED = "spec_created"
    SPEC_APPROVED = "spec_approved"
    PR_CREATED = "pr_created"
    PR_MERGED = "pr_merged"
    PR_CHECK_FAILED = "pr_check_failed"
    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    DEPLOYMENT_FAILED = "deployment_failed"
    TEST_PASSED = "test_passed"
    TEST_FAILED = "test_failed"

@dataclass
class Action:
    id: str
    type: str
    status: ActionStatus
    payload: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0

@dataclass
class Event:
    id: str
    type: EventType
    source: str
    payload: Dict[str, Any]
    timestamp: datetime
    action_ids: List[str] = None

class ActionBus:
    """Central event and action orchestration bus."""
    
    def __init__(self):
        self.actions: Dict[str, Action] = {}
        self.events: List[Event] = []
        self.handlers: Dict[EventType, List[Callable]] = {}
        self.idempotency_keys: Dict[str, str] = {}
        
    async def emit_event(self, event_type: EventType, source: str, payload: Dict[str, Any]) -> str:
        """Emit an event and trigger registered handlers."""
        event_id = f"evt_{datetime.now().timestamp()}"
        event = Event(
            id=event_id,
            type=event_type,
            source=source,
            payload=payload,
            timestamp=datetime.now()
        )
        
        self.events.append(event)
        
        # Trigger handlers
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
        
        return event_id
    
    async def register_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def execute_action(self, action_type: str, payload: Dict[str, Any], idempotency_key: str = None) -> Action:
        """Execute an action with optional idempotency."""
        # Check idempotency
        if idempotency_key:
            if idempotency_key in self.idempotency_keys:
                existing_id = self.idempotency_keys[idempotency_key]
                return self.actions[existing_id]
        
        action_id = f"act_{datetime.now().timestamp()}"
        action = Action(
            id=action_id,
            type=action_type,
            status=ActionStatus.PENDING,
            payload=payload,
            created_at=datetime.now()
        )
        
        self.actions[action_id] = action
        
        if idempotency_key:
            self.idempotency_keys[idempotency_key] = action_id
        
        # Mark as running
        action.status = ActionStatus.RUNNING
        action.started_at = datetime.now()
        
        try:
            # Execute action based on type
            result = await self._execute_action_internal(action_type, payload)
            
            action.status = ActionStatus.SUCCESS
            action.completed_at = datetime.now()
            action.payload["result"] = result
            
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.completed_at = datetime.now()
            action.error = str(e)
        
        return action
    
    async def _execute_action_internal(self, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Internal action execution router."""
        if action_type == "create_spec":
            return await self._create_spec(payload)
        elif action_type == "create_branch":
            return await self._create_branch(payload)
        elif action_type == "create_pr":
            return await self._create_pr(payload)
        elif action_type == "run_check":
            return await self._run_check(payload)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def _create_spec(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new spec document."""
        # Placeholder - would integrate with spec service
        return {
            "spec_id": f"spec_{datetime.now().timestamp()}",
            "title": payload.get("title", "Untitled Spec"),
            "status": "draft"
        }
    
    async def _create_branch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new branch."""
        # Placeholder - would integrate with GitHub
        return {
            "branch": payload.get("name", "feature/branch"),
            "ref": "refs/heads/feature/branch"
        }
    
    async def _create_pr(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pull request."""
        # Placeholder - would integrate with GitHub
        return {
            "pr_number": 123,
            "url": f"https://github.com/{payload.get('owner')}/{payload.get('repo')}/pull/123"
        }
    
    async def _run_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run a policy check."""
        # Placeholder - would integrate with policy engine
        return {
            "passed": True,
            "checks": ["syntax", "security", "cost"]
        }
    
    def get_action(self, action_id: str) -> Optional[Action]:
        """Get an action by ID."""
        return self.actions.get(action_id)
    
    def list_actions(self, status: Optional[ActionStatus] = None, limit: int = 100) -> List[Action]:
        """List actions, optionally filtered by status."""
        actions = list(self.actions.values())
        if status:
            actions = [a for a in actions if a.status == status]
        return sorted(actions, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def get_events(self, limit: int = 100) -> List[Event]:
        """Get recent events."""
        return sorted(self.events, key=lambda x: x.timestamp, reverse=True)[:limit]

# Global action bus instance
action_bus = ActionBus()

