"""
Extended GitHub Integration for Unified DevOS
Handles: Repos, Issues, PRs, Checks, Releases, Webhooks
"""

from typing import Dict, Any, List, Optional
import asyncio
import os
import httpx
from datetime import datetime
import logging
from dataclasses import dataclass
import time

# Import from LLM service
from ..llm.openai_client import TimeoutManager, CircuitBreaker, CircuitBreakerConfig, CircuitBreakerState

logger = logging.getLogger(__name__)

@dataclass
class GitHubExtendedTimeoutConfig:
    """Configuration for GitHub Extended timeout settings."""
    default_timeout: float = 30.0  # seconds
    list_repos_timeout: float = 15.0
    get_repo_timeout: float = 10.0
    list_issues_timeout: float = 20.0
    create_issue_timeout: float = 15.0
    list_prs_timeout: float = 20.0
    create_pr_timeout: float = 15.0
    get_checks_timeout: float = 10.0
    list_releases_timeout: float = 15.0
    create_release_timeout: float = 20.0
    list_webhooks_timeout: float = 10.0
    create_webhook_timeout: float = 15.0
    get_flow_status_timeout: float = 30.0

class GitHubExtendedTimeoutManager(TimeoutManager):
    """Manages timeout configurations for GitHub Extended operations."""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> GitHubExtendedTimeoutConfig:
        """Load timeout configuration from environment variables."""
        return GitHubExtendedTimeoutConfig(
            default_timeout=float(os.getenv("GITHUB_EXTENDED_DEFAULT_TIMEOUT", "30.0")),
            list_repos_timeout=float(os.getenv("GITHUB_EXTENDED_LIST_REPOS_TIMEOUT", "15.0")),
            get_repo_timeout=float(os.getenv("GITHUB_EXTENDED_GET_REPO_TIMEOUT", "10.0")),
            list_issues_timeout=float(os.getenv("GITHUB_EXTENDED_LIST_ISSUES_TIMEOUT", "20.0")),
            create_issue_timeout=float(os.getenv("GITHUB_EXTENDED_CREATE_ISSUE_TIMEOUT", "15.0")),
            list_prs_timeout=float(os.getenv("GITHUB_EXTENDED_LIST_PRS_TIMEOUT", "20.0")),
            create_pr_timeout=float(os.getenv("GITHUB_EXTENDED_CREATE_PR_TIMEOUT", "15.0")),
            get_checks_timeout=float(os.getenv("GITHUB_EXTENDED_GET_CHECKS_TIMEOUT", "10.0")),
            list_releases_timeout=float(os.getenv("GITHUB_EXTENDED_LIST_RELEASES_TIMEOUT", "15.0")),
            create_release_timeout=float(os.getenv("GITHUB_EXTENDED_CREATE_RELEASE_TIMEOUT", "20.0")),
            list_webhooks_timeout=float(os.getenv("GITHUB_EXTENDED_LIST_WEBHOOKS_TIMEOUT", "10.0")),
            create_webhook_timeout=float(os.getenv("GITHUB_EXTENDED_CREATE_WEBHOOK_TIMEOUT", "15.0")),
            get_flow_status_timeout=float(os.getenv("GITHUB_EXTENDED_GET_FLOW_STATUS_TIMEOUT", "30.0"))
        )

    def get_timeout(self, operation: str) -> float:
        """Get timeout for specific operation."""
        timeout_map = {
            "list_repos": self.config.list_repos_timeout,
            "get_repo": self.config.get_repo_timeout,
            "list_issues": self.config.list_issues_timeout,
            "create_issue": self.config.create_issue_timeout,
            "list_prs": self.config.list_prs_timeout,
            "create_pr": self.config.create_pr_timeout,
            "get_checks": self.config.get_checks_timeout,
            "list_releases": self.config.list_releases_timeout,
            "create_release": self.config.create_release_timeout,
            "list_webhooks": self.config.list_webhooks_timeout,
            "create_webhook": self.config.create_webhook_timeout,
            "get_flow_status": self.config.get_flow_status_timeout
        }
        return timeout_map.get(operation, self.config.default_timeout)

class GitHubExtendedIntegration:
    """Extended GitHub integration for Unified DevOS MVP."""

    def __init__(self):
        self.service_name = "github_extended"
        self.api_base = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        } if self.token else {}

        # Initialize timeout and circuit breaker components
        self.timeout_manager = GitHubExtendedTimeoutManager()
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=int(os.getenv("GITHUB_EXTENDED_CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")),
            recovery_timeout=float(os.getenv("GITHUB_EXTENDED_CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "60.0")),
            success_threshold=int(os.getenv("GITHUB_EXTENDED_CIRCUIT_BREAKER_SUCCESS_THRESHOLD", "3")),
            timeout=float(os.getenv("GITHUB_EXTENDED_CIRCUIT_BREAKER_TIMEOUT", "30.0"))
        ))

        # Configure httpx client with timeout
        timeout_config = httpx.Timeout(
            timeout=self.timeout_manager.config.default_timeout
        )
        self.client = httpx.AsyncClient(timeout=timeout_config)

    async def list_repos(self) -> List[Dict[str, Any]]:
        """List all repositories with timeout and circuit breaker protection."""
        if not self.token:
            return []

        async def _list_repos():
            response = await self.client.get(
                f"{self.api_base}/user/repos",
                headers=self.headers,
                params={"type": "all", "per_page": 100}
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_list_repos)
        except Exception as e:
            logger.error(f"list_repos failed: {str(e)}")
            # Record timeout event in health service if it was a timeout
            if "timeout" in str(e).lower():
                try:
                    from services.health import health_service
                    health_service.record_timeout_event(
                        service_name="github_extended",
                        operation="list_repos",
                        timeout_seconds=self.timeout_manager.config.default_timeout,
                        error=str(e)
                    )
                except ImportError:
                    pass  # Health service not available
            return []

    async def get_repo(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get repository details with timeout and circuit breaker protection."""
        if not self.token:
            return None

        async def _get_repo():
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_get_repo)
        except Exception as e:
            logger.error(f"get_repo failed for {owner}/{repo}: {str(e)}")
            return None

    async def list_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """List issues for a repository with timeout and circuit breaker protection."""
        if not self.token:
            return []

        async def _list_issues():
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                params={"state": state, "per_page": 100}
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_list_issues)
        except Exception as e:
            logger.error(f"list_issues failed for {owner}/{repo}: {str(e)}")
            return []

    async def create_issue(self, owner: str, repo: str, title: str, body: str = "", labels: List[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new issue with timeout and circuit breaker protection."""
        if not self.token:
            return None

        async def _create_issue():
            payload = {"title": title, "body": body}
            if labels:
                payload["labels"] = labels

            response = await self.client.post(
                f"{self.api_base}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_create_issue)
        except Exception as e:
            logger.error(f"create_issue failed for {owner}/{repo}: {str(e)}")
            return None

    async def list_prs(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """List pull requests with timeout and circuit breaker protection."""
        if not self.token:
            return []

        async def _list_prs():
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/pulls",
                headers=self.headers,
                params={"state": state, "per_page": 100}
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_list_prs)
        except Exception as e:
            logger.error(f"list_prs failed for {owner}/{repo}: {str(e)}")
            return []

    async def create_pr(self, owner: str, repo: str, title: str, head: str, base: str, body: str = "") -> Optional[Dict[str, Any]]:
        """Create a pull request with timeout and circuit breaker protection."""
        if not self.token:
            return None

        async def _create_pr():
            response = await self.client.post(
                f"{self.api_base}/repos/{owner}/{repo}/pulls",
                headers=self.headers,
                json={
                    "title": title,
                    "head": head,
                    "base": base,
                    "body": body
                }
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_create_pr)
        except Exception as e:
            logger.error(f"create_pr failed for {owner}/{repo}: {str(e)}")
            return None

    async def get_checks(self, owner: str, repo: str, ref: str) -> List[Dict[str, Any]]:
        """Get check runs for a specific ref with timeout and circuit breaker protection."""
        if not self.token:
            return []

        async def _get_checks():
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/commits/{ref}/check-runs",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("check_runs", [])

        try:
            return await self.circuit_breaker.call(_get_checks)
        except Exception as e:
            logger.error(f"get_checks failed for {owner}/{repo}/{ref}: {str(e)}")
            return []

    async def list_releases(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List releases with timeout and circuit breaker protection."""
        if not self.token:
            return []

        async def _list_releases():
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/releases",
                headers=self.headers,
                params={"per_page": 100}
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_list_releases)
        except Exception as e:
            logger.error(f"list_releases failed for {owner}/{repo}: {str(e)}")
            return []

    async def create_release(self, owner: str, repo: str, tag: str, name: str, body: str = "", draft: bool = False) -> Optional[Dict[str, Any]]:
        """Create a release with timeout and circuit breaker protection."""
        if not self.token:
            return None

        async def _create_release():
            response = await self.client.post(
                f"{self.api_base}/repos/{owner}/{repo}/releases",
                headers=self.headers,
                json={
                    "tag_name": tag,
                    "name": name,
                    "body": body,
                    "draft": draft
                }
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_create_release)
        except Exception as e:
            logger.error(f"create_release failed for {owner}/{repo}: {str(e)}")
            return None

    async def list_webhooks(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List webhooks for a repository with timeout and circuit breaker protection."""
        if not self.token:
            return []

        async def _list_webhooks():
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/hooks",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_list_webhooks)
        except Exception as e:
            logger.error(f"list_webhooks failed for {owner}/{repo}: {str(e)}")
            return []

    async def create_webhook(self, owner: str, repo: str, url: str, events: List[str] = None) -> Optional[Dict[str, Any]]:
        """Create a webhook with timeout and circuit breaker protection."""
        if not self.token:
            return None

        async def _create_webhook():
            payload = {
                "name": "web",
                "active": True,
                "events": events or ["push", "pull_request"],
                "config": {
                    "url": url,
                    "content_type": "json"
                }
            }

            response = await self.client.post(
                f"{self.api_base}/repos/{owner}/{repo}/hooks",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

        try:
            return await self.circuit_breaker.call(_create_webhook)
        except Exception as e:
            logger.error(f"create_webhook failed for {owner}/{repo}: {str(e)}")
            return None

    async def get_flow_status(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get unified flow status for a repo (Issues → PRs → Checks → Releases) with timeout and circuit breaker protection."""
        if not self.token:
            return {"error": "Not configured"}

        async def _get_flow_status():
            issues = await self.list_issues(owner, repo, state="open")
            prs = await self.list_prs(owner, repo, state="open")
            releases = await self.list_releases(owner, repo)

            # Get PR status
            pr_details = []
            for pr in prs[:5]:  # Limit to recent PRs
                checks = await self.get_checks(owner, repo, pr["head"]["sha"])
                pr_details.append({
                    "number": pr["number"],
                    "title": pr["title"],
                    "state": pr["state"],
                    "checks": {
                        "total": len(checks),
                        "passed": sum(1 for c in checks if c["conclusion"] == "success"),
                        "pending": sum(1 for c in checks if c["status"] == "in_progress"),
                    }
                })

            return {
                "repo": f"{owner}/{repo}",
                "issues_open": len(issues),
                "prs_open": len(prs),
                "releases_total": len(releases),
                "recent_prs": pr_details,
                "timestamp": datetime.now().isoformat()
            }

        try:
            return await self.circuit_breaker.call(_get_flow_status)
        except Exception as e:
            logger.error(f"get_flow_status failed for {owner}/{repo}: {str(e)}")
            # Fallback response
            return {
                "error": str(e),
                "repo": f"{owner}/{repo}",
                "issues_open": 0,
                "prs_open": 0,
                "releases_total": 0,
                "recent_prs": [],
                "timestamp": datetime.now().isoformat(),
                "fallback": True
            }

    async def test_connection(self) -> Dict[str, Any]:
        """Test the GitHub connection with timeout and circuit breaker protection."""
        if not self.token:
            return {
                "success": False,
                "message": "GitHub token not configured",
                "details": {"error": "Missing GITHUB_TOKEN environment variable"}
            }

        async def _test_connection():
            response = await self.client.get(
                f"{self.api_base}/user",
                headers=self.headers
            )
            response.raise_for_status()
            user_data = response.json()
            return {
                "success": True,
                "message": f"Successfully connected to GitHub as {user_data.get('login')}",
                "details": {
                    "user": user_data.get("login"),
                    "name": user_data.get("name"),
                    "public_repos": user_data.get("public_repos")
                }
            }

        try:
            result = await self.circuit_breaker.call(_test_connection)
            return result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {
                    "success": False,
                    "message": "Invalid GitHub token",
                    "details": {"error": "Authentication failed"}
                }
            else:
                return {
                    "success": False,
                    "message": f"GitHub API error: {e.response.status_code}",
                    "details": {"error": str(e)}
                }
        except Exception as e:
            logger.error(f"test_connection failed: {str(e)}")
            return {
                "success": False,
                "message": "Failed to connect to GitHub API",
                "details": {"error": str(e), "fallback": True}
            }

    async def close(self):
        """Clean up HTTP client."""
        await self.client.aclose()

    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for monitoring."""
        return self.circuit_breaker.get_state()

    def get_timeout_config(self) -> Dict[str, Any]:
        """Get current timeout configuration."""
        return {
            "default_timeout": self.timeout_manager.config.default_timeout,
            "list_repos_timeout": self.timeout_manager.config.list_repos_timeout,
            "get_repo_timeout": self.timeout_manager.config.get_repo_timeout,
            "list_issues_timeout": self.timeout_manager.config.list_issues_timeout,
            "create_issue_timeout": self.timeout_manager.config.create_issue_timeout,
            "list_prs_timeout": self.timeout_manager.config.list_prs_timeout,
            "create_pr_timeout": self.timeout_manager.config.create_pr_timeout,
            "get_checks_timeout": self.timeout_manager.config.get_checks_timeout,
            "list_releases_timeout": self.timeout_manager.config.list_releases_timeout,
            "create_release_timeout": self.timeout_manager.config.create_release_timeout,
            "list_webhooks_timeout": self.timeout_manager.config.list_webhooks_timeout,
            "create_webhook_timeout": self.timeout_manager.config.create_webhook_timeout,
            "get_flow_status_timeout": self.timeout_manager.config.get_flow_status_timeout
        }

