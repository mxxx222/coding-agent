"""
Health Check Service for Unified DevOS
Monitors system health, circuit breakers, timeouts, and service availability.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Import existing services
from .llm.openai_client import OpenAIClient
from .integrations.github import GitHubIntegration
from .integrations.github_extended import GitHubExtendedIntegration
from .action_bus import ActionBus

logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class ServiceHealth:
    """Individual service health information."""
    name: str
    status: str
    response_time: Optional[float] = None
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class SystemHealth:
    """Overall system health information."""
    status: str
    timestamp: datetime
    uptime: float
    services: List[ServiceHealth]
    system_resources: Dict[str, Any]
    circuit_breakers: Dict[str, Any]
    timeout_events: List[Dict[str, Any]]

class HealthCheckService:
    """Central health monitoring service."""

    def __init__(self):
        self.start_time = time.time()
        self.services = {
            "openai": OpenAIClient(),
            "github": GitHubIntegration(),
            "github_extended": GitHubExtendedIntegration(),
            "action_bus": ActionBus()
        }
        self.timeout_events: List[Dict[str, Any]] = []
        self.last_health_check = None
        self.health_check_interval = 30  # seconds

    async def check_overall_health(self) -> SystemHealth:
        """Perform comprehensive health check of all system components."""
        start_time = time.time()
        timestamp = datetime.now()

        try:
            # Check individual services
            service_healths = []
            for service_name, service in self.services.items():
                service_health = await self._check_service_health(service_name, service)
                service_healths.append(service_health)

            # Get circuit breaker states
            circuit_breakers = await self._get_circuit_breaker_states()

            # Get system resources
            system_resources = self._get_system_resources()

            # Determine overall status
            overall_status = self._determine_overall_status(service_healths)

            # Calculate uptime
            uptime = time.time() - self.start_time

            # Update last check time
            self.last_health_check = timestamp

            health = SystemHealth(
                status=overall_status,
                timestamp=timestamp,
                uptime=uptime,
                services=service_healths,
                system_resources=system_resources,
                circuit_breakers=circuit_breakers,
                timeout_events=self.timeout_events[-10:]  # Last 10 timeout events
            )

            # Log health check results
            response_time = time.time() - start_time
            logger.info(f"Health check completed in {response_time:.2f}s - Status: {overall_status}")

            return health

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return SystemHealth(
                status=HealthStatus.UNHEALTHY,
                timestamp=timestamp,
                uptime=time.time() - self.start_time,
                services=[],
                system_resources={},
                circuit_breakers={},
                timeout_events=[]
            )

    async def check_timeout_health(self) -> Dict[str, Any]:
        """Check timeout system health and recent events."""
        timeout_configs = {}

        # Collect timeout configurations from all services
        for service_name, service in self.services.items():
            if hasattr(service, 'timeout_manager') and hasattr(service.timeout_manager, 'get_timeout_config'):
                timeout_configs[service_name] = service.timeout_manager.get_timeout_config()
            elif hasattr(service, 'get_timeout_config'):
                timeout_configs[service_name] = service.get_timeout_config()

        # Get recent timeout events (last 24 hours)
        recent_timeouts = [
            event for event in self.timeout_events
            if datetime.now() - event.get('timestamp', datetime.min) < timedelta(hours=24)
        ]

        return {
            "status": "healthy" if len(recent_timeouts) < 10 else "degraded",  # More than 10 timeouts in 24h is degraded
            "timeout_configs": timeout_configs,
            "recent_timeout_events": recent_timeouts,
            "total_recent_timeouts": len(recent_timeouts),
            "timestamp": datetime.now().isoformat()
        }

    async def check_services_health(self) -> Dict[str, Any]:
        """Check individual service health."""
        service_statuses = {}

        for service_name, service in self.services.items():
            health = await self._check_service_health(service_name, service)
            service_statuses[service_name] = {
                "status": health.status,
                "response_time": health.response_time,
                "last_check": health.last_check.isoformat() if health.last_check else None,
                "error_message": health.error_message,
                "details": health.details
            }

        return {
            "services": service_statuses,
            "timestamp": datetime.now().isoformat()
        }

    async def check_circuit_breakers_health(self) -> Dict[str, Any]:
        """Check circuit breaker states for all services."""
        circuit_breakers = await self._get_circuit_breaker_states()

        # Determine overall circuit breaker health
        unhealthy_breakers = [
            name for name, state in circuit_breakers.items()
            if state.get('state') == 'open'
        ]

        status = "healthy" if not unhealthy_breakers else "degraded"

        return {
            "status": status,
            "circuit_breakers": circuit_breakers,
            "unhealthy_breakers": unhealthy_breakers,
            "timestamp": datetime.now().isoformat()
        }

    async def _check_service_health(self, service_name: str, service) -> ServiceHealth:
        """Check health of individual service."""
        start_time = time.time()
        timestamp = datetime.now()

        try:
            if service_name == "openai":
                # Test OpenAI connection
                result = await service.test_connection()
                status = "healthy" if result.get("success") else "unhealthy"
                error_message = result.get("error") if not result.get("success") else None
                details = result

            elif service_name in ["github", "github_extended"]:
                # Test GitHub connection
                result = await service.test_connection()
                status = "healthy" if result.get("success") else "unhealthy"
                error_message = result.get("message") if not result.get("success") else None
                details = result

            elif service_name == "action_bus":
                # Action bus is always healthy if initialized
                status = "healthy"
                error_message = None
                details = {"message": "Action bus operational"}

            else:
                status = "unknown"
                error_message = "Unknown service type"
                details = {}

            response_time = time.time() - start_time

            return ServiceHealth(
                name=service_name,
                status=status,
                response_time=response_time,
                last_check=timestamp,
                error_message=error_message,
                details=details
            )

        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Service health check failed for {service_name}: {str(e)}")

            return ServiceHealth(
                name=service_name,
                status="unhealthy",
                response_time=response_time,
                last_check=timestamp,
                error_message=str(e),
                details={"exception": str(e)}
            )

    async def _get_circuit_breaker_states(self) -> Dict[str, Any]:
        """Collect circuit breaker states from all services."""
        circuit_breakers = {}

        for service_name, service in self.services.items():
            if hasattr(service, 'circuit_breaker') and hasattr(service.circuit_breaker, 'get_state'):
                circuit_breakers[service_name] = service.circuit_breaker.get_state()
            elif hasattr(service, 'get_circuit_breaker_status'):
                circuit_breakers[service_name] = service.get_circuit_breaker_status()

        return circuit_breakers

    def _get_system_resources(self) -> Dict[str, Any]:
        """Get system resource usage."""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available - system resources monitoring disabled"}

        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            logger.warning(f"Failed to get system resources: {str(e)}")
            return {"error": "Unable to retrieve system resources"}

    def _determine_overall_status(self, service_healths: List[ServiceHealth]) -> str:
        """Determine overall system health status."""
        unhealthy_count = sum(1 for health in service_healths if health.status == "unhealthy")
        degraded_count = sum(1 for health in service_healths if health.status == "degraded")

        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        elif degraded_count > 0 or unhealthy_count > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

    def record_timeout_event(self, service_name: str, operation: str, timeout_seconds: float, error: str):
        """Record a timeout event for monitoring."""
        event = {
            "service": service_name,
            "operation": operation,
            "timeout_seconds": timeout_seconds,
            "error": error,
            "timestamp": datetime.now()
        }

        self.timeout_events.append(event)

        # Keep only last 100 events
        if len(self.timeout_events) > 100:
            self.timeout_events = self.timeout_events[-100:]

        logger.warning(f"Timeout event recorded: {service_name}.{operation} - {error}")

# Global health check service instance
health_service = HealthCheckService()