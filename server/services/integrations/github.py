from typing import Dict, Any, List
import asyncio
import os
import requests
from urllib.parse import urlparse
import logging
from dataclasses import dataclass
from enum import Enum
import time

# Import from LLM service
from ..llm.openai_client import TimeoutManager, CircuitBreaker, CircuitBreakerConfig, CircuitBreakerState

logger = logging.getLogger(__name__)

@dataclass
class GitHubTimeoutConfig:
    """Configuration for GitHub timeout settings."""
    default_timeout: float = 30.0  # seconds
    test_connection_timeout: float = 10.0
    get_status_timeout: float = 15.0
    setup_timeout: float = 60.0

class GitHubTimeoutManager(TimeoutManager):
    """Manages timeout configurations for GitHub operations."""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> GitHubTimeoutConfig:
        """Load timeout configuration from environment variables."""
        return GitHubTimeoutConfig(
            default_timeout=float(os.getenv("GITHUB_DEFAULT_TIMEOUT", "30.0")),
            test_connection_timeout=float(os.getenv("GITHUB_TEST_CONNECTION_TIMEOUT", "10.0")),
            get_status_timeout=float(os.getenv("GITHUB_GET_STATUS_TIMEOUT", "15.0")),
            setup_timeout=float(os.getenv("GITHUB_SETUP_TIMEOUT", "60.0"))
        )

    def get_timeout(self, operation: str) -> float:
        """Get timeout for specific operation."""
        timeout_map = {
            "test_connection": self.config.test_connection_timeout,
            "get_status": self.config.get_status_timeout,
            "setup": self.config.setup_timeout
        }
        return timeout_map.get(operation, self.config.default_timeout)

class GitHubIntegration:
    """Integration service for GitHub."""

    def __init__(self):
        self.service_name = "github"
        self.enabled = False
        self.api_base = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")

        # Initialize timeout and circuit breaker components
        self.timeout_manager = GitHubTimeoutManager()
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=int(os.getenv("GITHUB_CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")),
            recovery_timeout=float(os.getenv("GITHUB_CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "60.0")),
            success_threshold=int(os.getenv("GITHUB_CIRCUIT_BREAKER_SUCCESS_THRESHOLD", "3")),
            timeout=float(os.getenv("GITHUB_CIRCUIT_BREAKER_TIMEOUT", "30.0"))
        ))

    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the GitHub integration with timeout and circuit breaker protection."""
        configured = bool(self.token)
        enabled = configured and self.enabled

        timeout = self.timeout_manager.get_timeout("get_status")

        async def _get_status():
            # Simulate status check - in real implementation might check token validity
            return {
                "enabled": enabled,
                "configured": configured,
                "last_used": None,
                "circuit_breaker_state": self.circuit_breaker.get_state()["state"]
            }

        try:
            return await asyncio.wait_for(_get_status(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"get_status timed out after {timeout} seconds")
            # Record timeout event in health service
            try:
                from services.health import health_service
                health_service.record_timeout_event(
                    service_name="github",
                    operation="get_status",
                    timeout_seconds=timeout,
                    error=f"Status check timed out after {timeout} seconds"
                )
            except ImportError:
                pass  # Health service not available
            return {
                "enabled": False,
                "configured": configured,
                "last_used": None,
                "error": f"Status check timed out after {timeout} seconds",
                "circuit_breaker_state": self.circuit_breaker.get_state()["state"]
            }
        except Exception as e:
            logger.error(f"get_status failed: {str(e)}")
            return {
                "enabled": False,
                "configured": configured,
                "last_used": None,
                "error": str(e),
                "circuit_breaker_state": self.circuit_breaker.get_state()["state"]
            }

    async def setup(self, config: Dict[str, Any], project_path: str = None) -> Dict[str, Any]:
        """Setup the GitHub integration with timeout protection."""
        timeout = self.timeout_manager.get_timeout("setup")

        async def _setup():
            files_created = []
            dependencies = []
            config_updated = False
            next_steps = []

            # Validate configuration
            if not config.get("token"):
                next_steps.append("Obtain a GitHub Personal Access Token from https://github.com/settings/tokens")
                next_steps.append("Set GITHUB_TOKEN environment variable")

            if config.get("repository"):
                repo_url = config["repository"]
                parsed = urlparse(repo_url)
                if parsed.hostname == "github.com":
                    next_steps.append(f"Configure repository: {repo_url}")
                    next_steps.append("Set up GitHub Actions workflows if needed")
                    next_steps.append("Configure webhooks for CI/CD integration")

            if config.get("webhooks", False):
                next_steps.append("Set up webhooks for automated deployments")
                next_steps.append("Configure webhook secrets")

            if config.get("actions", False):
                next_steps.append("Create GitHub Actions workflow files")
                next_steps.append("Configure deployment pipelines")

            return {
                "success": True,
                "files_created": files_created,
                "dependencies": dependencies,
                "config_updated": config_updated,
                "next_steps": next_steps
            }

        try:
            return await asyncio.wait_for(_setup(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"setup timed out after {timeout} seconds")
            # Record timeout event in health service
            try:
                from services.health import health_service
                health_service.record_timeout_event(
                    service_name="github",
                    operation="setup",
                    timeout_seconds=timeout,
                    error=f"Setup timed out after {timeout} seconds"
                )
            except ImportError:
                pass  # Health service not available
            return {
                "success": False,
                "error": f"Setup timed out after {timeout} seconds",
                "files_created": [],
                "dependencies": [],
                "config_updated": False,
                "next_steps": ["Retry setup operation"]
            }
        except Exception as e:
            logger.error(f"setup failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "files_created": [],
                "dependencies": [],
                "config_updated": False,
                "next_steps": ["Check configuration and retry"]
            }

    async def test_connection(self) -> Dict[str, Any]:
        """Test the GitHub connection with timeout and circuit breaker protection."""
        if not self.token:
            return {
                "success": False,
                "message": "GitHub token not configured",
                "details": {"error": "Missing GITHUB_TOKEN environment variable"}
            }

        timeout = self.timeout_manager.get_timeout("test_connection")

        async def _test_connection():
            import aiohttp

            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(f"{self.api_base}/user", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        return {
                            "success": True,
                            "message": f"Successfully connected to GitHub as {user_data.get('login')}",
                            "details": {
                                "user": user_data.get("login"),
                                "name": user_data.get("name"),
                                "public_repos": user_data.get("public_repos")
                            }
                        }
                    elif response.status == 401:
                        return {
                            "success": False,
                            "message": "Invalid GitHub token",
                            "details": {"error": "Authentication failed"}
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"GitHub API error: {response.status}",
                            "details": {"error": error_text}
                        }

        try:
            result = await self.circuit_breaker.call(_test_connection)
            return result
        except Exception as e:
            logger.error(f"test_connection failed: {str(e)}")
            # Fallback response
            return {
                "success": False,
                "message": "Failed to connect to GitHub API",
                "details": {"error": str(e), "fallback": True}
            }

    async def remove(self) -> Dict[str, Any]:
        """Remove the GitHub integration."""
        self.enabled = False
        return {
            "success": True,
            "message": "GitHub integration disabled"
        }

    async def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return {
            "token_configured": bool(self.token),
            "enabled": self.enabled,
            "api_base": self.api_base,
            "timeout_config": {
                "default_timeout": self.timeout_manager.config.default_timeout,
                "test_connection_timeout": self.timeout_manager.config.test_connection_timeout,
                "get_status_timeout": self.timeout_manager.config.get_status_timeout,
                "setup_timeout": self.timeout_manager.config.setup_timeout
            },
            "circuit_breaker_config": {
                "failure_threshold": self.circuit_breaker.config.failure_threshold,
                "recovery_timeout": self.circuit_breaker.config.recovery_timeout,
                "success_threshold": self.circuit_breaker.config.success_threshold,
                "timeout": self.circuit_breaker.config.timeout
            }
        }

    async def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update the configuration."""
        if "enabled" in config:
            self.enabled = config["enabled"]

        return {
            "success": True,
            "message": "GitHub configuration updated"
        }

    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for monitoring."""
        return self.circuit_breaker.get_state()

    def get_timeout_config(self) -> Dict[str, Any]:
        """Get current timeout configuration."""
        return {
            "default_timeout": self.timeout_manager.config.default_timeout,
            "test_connection_timeout": self.timeout_manager.config.test_connection_timeout,
            "get_status_timeout": self.timeout_manager.config.get_status_timeout,
            "setup_timeout": self.timeout_manager.config.setup_timeout
        }