import openai
from openai import AsyncOpenAI
import os
from typing import Dict, Any, List, Optional, Callable
import asyncio
import time
import logging
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class TimeoutConfig:
    """Configuration for timeout settings."""
    default_timeout: float = 30.0  # seconds
    analyze_code_timeout: float = 60.0
    generate_code_timeout: float = 90.0
    explain_code_timeout: float = 45.0
    optimize_code_timeout: float = 75.0
    generate_tests_timeout: float = 120.0
    test_connection_timeout: float = 10.0

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker settings."""
    failure_threshold: int = 5  # number of failures before opening
    recovery_timeout: float = 60.0  # seconds to wait before half-open
    success_threshold: int = 3  # successes needed to close from half-open
    timeout: float = 30.0  # request timeout for circuit breaker

class TimeoutManager:
    """Manages timeout configurations for OpenAI operations."""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> TimeoutConfig:
        """Load timeout configuration from environment variables."""
        return TimeoutConfig(
            default_timeout=float(os.getenv("OPENAI_DEFAULT_TIMEOUT", "30.0")),
            analyze_code_timeout=float(os.getenv("OPENAI_ANALYZE_CODE_TIMEOUT", "60.0")),
            generate_code_timeout=float(os.getenv("OPENAI_GENERATE_CODE_TIMEOUT", "90.0")),
            explain_code_timeout=float(os.getenv("OPENAI_EXPLAIN_CODE_TIMEOUT", "45.0")),
            optimize_code_timeout=float(os.getenv("OPENAI_OPTIMIZE_CODE_TIMEOUT", "75.0")),
            generate_tests_timeout=float(os.getenv("OPENAI_GENERATE_TESTS_TIMEOUT", "120.0")),
            test_connection_timeout=float(os.getenv("OPENAI_TEST_CONNECTION_TIMEOUT", "10.0"))
        )

    def get_timeout(self, operation: str) -> float:
        """Get timeout for specific operation."""
        timeout_map = {
            "analyze_code": self.config.analyze_code_timeout,
            "generate_code": self.config.generate_code_timeout,
            "explain_code": self.config.explain_code_timeout,
            "optimize_code": self.config.optimize_code_timeout,
            "generate_tests": self.config.generate_tests_timeout,
            "test_connection": self.config.test_connection_timeout
        }
        return timeout_map.get(operation, self.config.default_timeout)

class CircuitBreaker:
    """Circuit breaker implementation for OpenAI API protection."""

    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.logger = logging.getLogger(f"{__name__}.CircuitBreaker")

    def _should_attempt_request(self) -> bool:
        """Determine if request should be attempted based on circuit breaker state."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        return False

    def _record_success(self):
        """Record successful request."""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.logger.info("Circuit breaker transitioning to CLOSED")

    def _record_failure(self):
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count = 0

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning("Circuit breaker transitioning to OPEN (from HALF_OPEN)")
        elif self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(f"Circuit breaker transitioning to OPEN (failure threshold {self.config.failure_threshold} reached)")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if not self._should_attempt_request():
            raise Exception("Circuit breaker is OPEN - service temporarily unavailable")

        try:
            result = await func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            # Record timeout event in health service if available
            try:
                from services.health import health_service
                health_service.record_timeout_event(
                    service_name="openai",
                    operation="circuit_breaker_call",
                    timeout_seconds=self.config.timeout,
                    error=str(e)
                )
            except ImportError:
                pass  # Health service not available
            self._record_failure()
            raise e

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state information."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "time_since_last_failure": time.time() - self.last_failure_time if self.last_failure_time else None
        }

def timeout_wrapper(timeout_seconds: float):
    """Decorator to add timeout to async functions."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                    logger.warning(f"Operation {func.__name__} timed out after {timeout_seconds} seconds")
                    # Record timeout event in health service
                    try:
                        from services.health import health_service
                        health_service.record_timeout_event(
                            service_name="openai",
                            operation=func.__name__,
                            timeout_seconds=timeout_seconds,
                            error=f"Operation timed out after {timeout_seconds} seconds"
                        )
                    except ImportError:
                        pass  # Health service not available
                    raise Exception(f"Operation timed out after {timeout_seconds} seconds")
        return wrapper
    return decorator

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.organization = os.getenv("OPENAI_ORG_ID")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

        # Initialize timeout and circuit breaker components
        self.timeout_manager = TimeoutManager()
        self.circuit_breaker = CircuitBreaker()

        if not self.api_key:
            # Don't raise error, allow it to be initialized without API key for development
            self.client = None
        else:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                organization=self.organization if self.organization else None
            )

    async def initialize(self):
        """Initialize the OpenAI client."""
        try:
            if self.client:
                # Test the connection
                response = await self.test_connection()
                if response.get("success"):
                    print("OpenAI client initialized successfully")
                else:
                    print(f"OpenAI client initialization failed: {response.get('error')}")
            else:
                print("OpenAI client initialized without API key (mock mode)")
        except Exception as e:
            print(f"OpenAI client initialization error: {e}")

    async def analyze_code(self, prompt: str) -> Dict[str, Any]:
        """Analyze code using OpenAI with timeout and circuit breaker protection."""
        if not self.client:
            # Return mock response if no API key
            return {
                "success": True,
                "analysis": "Mock analysis: Code quality assessment would appear here with API key configured.",
                "usage": {}
            }

        timeout = self.timeout_manager.get_timeout("analyze_code")

        @timeout_wrapper(timeout)
        async def _analyze_code():
            return await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code analyst. Provide detailed analysis of code quality, performance, and suggestions for improvement."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

        try:
            response = await self.circuit_breaker.call(_analyze_code)

            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else {}
            }

        except Exception as e:
            logger.error(f"analyze_code failed: {str(e)}")
            return self._fallback_response("analyze_code", str(e))

    async def explain_code(self, prompt: str) -> Dict[str, Any]:
        """Explain code using OpenAI with timeout and circuit breaker protection."""
        if not self.client:
            return {
                "success": True,
                "explanation": "Mock explanation: Detailed code explanation would appear here with API key configured.",
                "usage": {}
            }

        timeout = self.timeout_manager.get_timeout("explain_code")

        @timeout_wrapper(timeout)
        async def _explain_code():
            return await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code explainer. Provide clear, detailed explanations of code functionality, structure, and purpose."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

        try:
            response = await self.circuit_breaker.call(_explain_code)

            return {
                "success": True,
                "explanation": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else {}
            }

        except Exception as e:
            logger.error(f"explain_code failed: {str(e)}")
            return self._fallback_response("explain_code", str(e))

    async def generate_tests(self, prompt: str) -> Dict[str, Any]:
        """Generate tests using OpenAI with timeout and circuit breaker protection."""
        if not self.client:
            return {
                "success": True,
                "tests": "Mock tests: Test cases would be generated here with API key configured.",
                "usage": {}
            }

        timeout = self.timeout_manager.get_timeout("generate_tests")

        @timeout_wrapper(timeout)
        async def _generate_tests():
            return await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert test generator. Create comprehensive, well-structured tests that cover functionality, edge cases, and error conditions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

        try:
            response = await self.circuit_breaker.call(_generate_tests)

            return {
                "success": True,
                "tests": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else {}
            }

        except Exception as e:
            logger.error(f"generate_tests failed: {str(e)}")
            return self._fallback_response("generate_tests", str(e))

    async def generate_code(self, prompt: str) -> Dict[str, Any]:
        """Generate code using OpenAI with timeout and circuit breaker protection."""
        if not self.client:
            return {
                "success": True,
                "code": "# Mock code: Generated code would appear here with API key configured.\ndef example():\n    pass",
                "usage": {}
            }

        timeout = self.timeout_manager.get_timeout("generate_code")

        @timeout_wrapper(timeout)
        async def _generate_code():
            return await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code generator. Generate clean, efficient, and well-documented code that follows best practices."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

        try:
            response = await self.circuit_breaker.call(_generate_code)

            return {
                "success": True,
                "code": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else {}
            }

        except Exception as e:
            logger.error(f"generate_code failed: {str(e)}")
            return self._fallback_response("generate_code", str(e))

    async def optimize_code(self, prompt: str) -> Dict[str, Any]:
        """Optimize code using OpenAI with timeout and circuit breaker protection."""
        if not self.client:
            return {
                "success": True,
                "optimized_code": "# Mock optimized code: Optimized version would appear here with API key configured.\ndef optimized_example():\n    pass",
                "usage": {}
            }

        timeout = self.timeout_manager.get_timeout("optimize_code")

        @timeout_wrapper(timeout)
        async def _optimize_code():
            return await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code optimizer. Provide optimized versions of code with improved performance, readability, and maintainability."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

        try:
            response = await self.circuit_breaker.call(_optimize_code)

            return {
                "success": True,
                "optimized_code": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else {}
            }

        except Exception as e:
            logger.error(f"optimize_code failed: {str(e)}")
            return self._fallback_response("optimize_code", str(e))

    async def test_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection with timeout and circuit breaker protection."""
        if not self.client:
            return {
                "success": False,
                "error": "No OpenAI API key configured"
            }

        timeout = self.timeout_manager.get_timeout("test_connection")

        @timeout_wrapper(timeout)
        async def _test_connection():
            return await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )

        try:
            response = await self.circuit_breaker.call(_test_connection)

            return {
                "success": True,
                "message": "OpenAI API connection successful"
            }

        except Exception as e:
            logger.error(f"test_connection failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        # In production, you'd track this in a database
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }

    def _fallback_response(self, operation: str, error: str) -> Dict[str, Any]:
        """Generate fallback response for failed operations."""
        fallbacks = {
            "analyze_code": {
                "success": False,
                "analysis": f"Analysis temporarily unavailable due to service issues: {error}",
                "usage": {},
                "error": error
            },
            "explain_code": {
                "success": False,
                "explanation": f"Code explanation temporarily unavailable due to service issues: {error}",
                "usage": {},
                "error": error
            },
            "generate_tests": {
                "success": False,
                "tests": f"# Test generation temporarily unavailable due to service issues: {error}",
                "usage": {},
                "error": error
            },
            "generate_code": {
                "success": False,
                "code": f"# Code generation temporarily unavailable due to service issues: {error}",
                "usage": {},
                "error": error
            },
            "optimize_code": {
                "success": False,
                "optimized_code": f"# Code optimization temporarily unavailable due to service issues: {error}",
                "usage": {},
                "error": error
            }
        }
        return fallbacks.get(operation, {
            "success": False,
            "error": f"Operation '{operation}' failed: {error}"
        })

    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for monitoring."""
        return self.circuit_breaker.get_state()

    def get_timeout_config(self) -> Dict[str, Any]:
        """Get current timeout configuration."""
        return {
            "default_timeout": self.timeout_manager.config.default_timeout,
            "analyze_code_timeout": self.timeout_manager.config.analyze_code_timeout,
            "generate_code_timeout": self.timeout_manager.config.generate_code_timeout,
            "explain_code_timeout": self.timeout_manager.config.explain_code_timeout,
            "optimize_code_timeout": self.timeout_manager.config.optimize_code_timeout,
            "generate_tests_timeout": self.timeout_manager.config.generate_tests_timeout,
            "test_connection_timeout": self.timeout_manager.config.test_connection_timeout
        }