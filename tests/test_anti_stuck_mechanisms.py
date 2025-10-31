"""
Comprehensive tests for anti-stuck mechanisms in Unified DevOS
Tests timeout functionality, circuit breaker patterns, and integration scenarios.
"""

import asyncio
import time
import pytest
import logging
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Import the anti-stuck components
from server.api.middleware.timeout import TimeoutMiddleware, create_timeout_middleware
from server.api.middleware.exceptions import TimeoutException, CircuitBreakerException
from server.services.llm.openai_client import (
    CircuitBreaker, CircuitBreakerConfig, TimeoutManager,
    timeout_wrapper, CircuitBreakerState
)
from server.services.health import health_service, HealthCheckService
from server.api.middleware.error_handlers import (
    timeout_exception_handler, circuit_breaker_exception_handler
)


class TestTimeoutFunctionality:
    """Test timeout functionality across different components."""

    def test_timeout_middleware_creation(self):
        """Test timeout middleware can be created with different configurations."""
        # Test default configuration
        middleware = create_timeout_middleware()
        assert middleware.default_timeout == 30.0
        assert middleware.route_timeouts == {}

        # Test custom configuration
        route_timeouts = {"POST:/api/test": 10.0, "GET:/api/health": 5.0}
        middleware = create_timeout_middleware(
            default_timeout=20.0,
            route_timeouts=route_timeouts
        )
        assert middleware.default_timeout == 20.0
        assert middleware.route_timeouts == route_timeouts

    def test_timeout_middleware_route_timeout_selection(self):
        """Test that middleware selects correct timeout for different routes."""
        route_timeouts = {"POST:/api/test": 10.0, "GET:/api/health": 5.0}
        middleware = create_timeout_middleware(route_timeouts=route_timeouts)

        # Test route-specific timeout
        timeout = middleware._get_timeout_for_route("/api/test", "POST")
        assert timeout == 10.0

        # Test default timeout for unknown route
        timeout = middleware._get_timeout_for_route("/api/unknown", "GET")
        assert timeout == 30.0

    @pytest.mark.asyncio
    async def test_timeout_middleware_timeout_exception(self):
        """Test that timeout middleware raises TimeoutException on timeout."""
        middleware = create_timeout_middleware(default_timeout=0.1)  # Very short timeout

        # Mock request and response
        mock_request = Mock()
        mock_request.url.path = "/test"
        mock_request.method = "GET"

        async def slow_call_next(request):
            await asyncio.sleep(1.0)  # Longer than timeout
            return Mock()

        with pytest.raises(TimeoutException) as exc_info:
            await middleware.dispatch(mock_request, slow_call_next)

        assert exc_info.value.error_code == "TIMEOUT_ERROR"
        assert exc_info.value.status_code == 408
        assert "timed out after 0.1" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_timeout_middleware_successful_request(self):
        """Test that timeout middleware allows successful requests through."""
        middleware = create_timeout_middleware(default_timeout=1.0)

        mock_request = Mock()
        mock_request.url.path = "/test"
        mock_request.method = "GET"

        async def fast_call_next(request):
            return Mock()

        start_time = time.time()
        response = await middleware.dispatch(mock_request, fast_call_next)
        end_time = time.time()

        assert response is not None
        assert end_time - start_time < 0.5  # Should complete quickly

    def test_timeout_manager_configuration(self):
        """Test timeout manager loads configuration correctly."""
        with patch.dict('os.environ', {
            'OPENAI_DEFAULT_TIMEOUT': '45.0',
            'OPENAI_ANALYZE_CODE_TIMEOUT': '120.0'
        }):
            manager = TimeoutManager()
            assert manager.config.default_timeout == 45.0
            assert manager.config.analyze_code_timeout == 120.0

    def test_timeout_manager_get_timeout(self):
        """Test timeout manager returns correct timeouts for operations."""
        manager = TimeoutManager()

        assert manager.get_timeout("analyze_code") == 60.0  # Default value
        assert manager.get_timeout("unknown_operation") == 30.0  # Default fallback

    @pytest.mark.asyncio
    async def test_timeout_wrapper_functionality(self):
        """Test timeout wrapper decorator works correctly."""
        @timeout_wrapper(0.1)
        async def slow_function():
            await asyncio.sleep(1.0)
            return "success"

        with pytest.raises(Exception) as exc_info:
            await slow_function()

        assert "timed out after 0.1 seconds" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_wrapper_success(self):
        """Test timeout wrapper allows successful operations."""
        @timeout_wrapper(1.0)
        async def fast_function():
            await asyncio.sleep(0.1)
            return "success"

        result = await fast_function()
        assert result == "success"


class TestCircuitBreakerFunctionality:
    """Test circuit breaker functionality and state transitions."""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initializes in closed state."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=2
        )
        cb = CircuitBreaker(config)

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.last_failure_time is None

    def test_circuit_breaker_closed_state_behavior(self):
        """Test circuit breaker behavior when in closed state."""
        cb = CircuitBreaker()

        # Should allow requests when closed
        assert cb._should_attempt_request() == True

        # Record failures
        cb._record_failure()
        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED

        # Record enough failures to open
        for _ in range(4):  # Total of 5 failures (threshold)
            cb._record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 5

    def test_circuit_breaker_open_state_behavior(self):
        """Test circuit breaker behavior when in open state."""
        cb = CircuitBreaker()

        # Force open state
        cb.state = CircuitBreakerState.OPEN
        cb.last_failure_time = time.time()

        # Should not allow requests when open and within recovery timeout
        assert cb._should_attempt_request() == False

        # Simulate recovery timeout passing
        cb.last_failure_time = time.time() - 70.0  # Past recovery timeout
        assert cb._should_attempt_request() == True
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_circuit_breaker_half_open_state_behavior(self):
        """Test circuit breaker behavior in half-open state."""
        cb = CircuitBreaker()

        # Force half-open state
        cb.state = CircuitBreakerState.HALF_OPEN
        cb.success_count = 0

        # Should allow requests in half-open
        assert cb._should_attempt_request() == True

        # Record success
        cb._record_success()
        assert cb.success_count == 1
        assert cb.state == CircuitBreakerState.HALF_OPEN  # Not enough successes yet

        # Record enough successes to close (need 2 more for threshold of 3)
        cb._record_success()  # Total of 2 successes
        assert cb.success_count == 2
        assert cb.state == CircuitBreakerState.HALF_OPEN

        cb._record_success()  # Total of 3 successes (threshold)
        assert cb.success_count == 3
        assert cb.state == CircuitBreakerState.CLOSED

        # Record failure in half-open (should go back to open)
        cb.state = CircuitBreakerState.HALF_OPEN
        cb._record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    @pytest.mark.asyncio
    async def test_circuit_breaker_call_success(self):
        """Test circuit breaker call with successful operation."""
        cb = CircuitBreaker()

        async def success_func():
            return "success"

        result = await cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_call_failure(self):
        """Test circuit breaker call with failing operation."""
        cb = CircuitBreaker()

        async def failure_func():
            raise Exception("Test failure")

        with pytest.raises(Exception):
            await cb.call(failure_func)

        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED  # Not enough failures yet

    @pytest.mark.asyncio
    async def test_circuit_breaker_open_blocks_requests(self):
        """Test that open circuit breaker blocks requests."""
        cb = CircuitBreaker()

        # Force open state with last_failure_time set
        cb.state = CircuitBreakerState.OPEN
        cb.last_failure_time = time.time()

        async def dummy_func():
            return "should not execute"

        with pytest.raises(Exception) as exc_info:
            await cb.call(dummy_func)

        assert "Circuit breaker is OPEN" in str(exc_info.value)

    def test_circuit_breaker_get_state(self):
        """Test circuit breaker state reporting."""
        cb = CircuitBreaker()

        state = cb.get_state()
        assert state["state"] == "closed"
        assert state["failure_count"] == 0
        assert state["success_count"] == 0

        # Record some activity - put in half-open state first
        cb.state = CircuitBreakerState.HALF_OPEN
        cb._record_success()

        state = cb.get_state()
        assert state["failure_count"] == 0  # _record_success resets failure_count
        assert state["success_count"] == 1


class TestIntegrationTesting:
    """Test integration between timeout and circuit breaker mechanisms."""

    @pytest.mark.asyncio
    async def test_timeout_and_circuit_breaker_integration(self):
        """Test combined timeout and circuit breaker protection."""
        # Create circuit breaker with short timeout
        config = CircuitBreakerConfig(timeout=0.1)
        cb = CircuitBreaker(config)

        @timeout_wrapper(0.1)
        async def slow_operation():
            await asyncio.sleep(1.0)  # Will timeout
            return "success"

        # First call should timeout and record failure
        with pytest.raises(Exception):
            await cb.call(slow_operation)

        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED

        # Multiple failures should eventually open circuit breaker
        for _ in range(4):
            with pytest.raises(Exception):
                await cb.call(slow_operation)

        assert cb.state == CircuitBreakerState.OPEN

    @pytest.mark.asyncio
    async def test_fallback_mechanisms(self):
        """Test fallback mechanisms when services fail."""
        from server.services.llm.openai_client import OpenAIClient

        # Mock client without API key (should use fallbacks)
        with patch.dict('os.environ', {}, clear=True):
            client = OpenAIClient()

            # Test fallback responses - these return success=True with mock data
            result = await client.analyze_code("test code")
            assert result["success"] == True  # Mock responses return success=True
            assert "Mock analysis" in result["analysis"]

            result = await client.generate_code("test prompt")
            assert result["success"] == True  # Mock responses return success=True
            assert "Mock code" in result["code"]


class TestHealthCheckValidation:
    """Test health check endpoints and circuit breaker reporting."""

    @pytest.mark.asyncio
    async def test_health_service_circuit_breaker_reporting(self):
        """Test that health service correctly reports circuit breaker states."""
        # Create a health service instance
        health = HealthCheckService()

        # Mock services with circuit breakers
        mock_service = Mock()
        mock_cb = CircuitBreaker()
        mock_cb._record_failure()  # Add some failure state
        mock_service.circuit_breaker = mock_cb
        mock_service.get_circuit_breaker_status = mock_cb.get_state

        health.services = {"test_service": mock_service}

        # Check circuit breaker health
        cb_health = await health.check_circuit_breakers_health()

        assert "circuit_breakers" in cb_health
        assert "test_service" in cb_health["circuit_breakers"]
        assert cb_health["circuit_breakers"]["test_service"]["failure_count"] == 1

    @pytest.mark.asyncio
    async def test_health_service_timeout_tracking(self):
        """Test that health service tracks timeout events."""
        health = HealthCheckService()

        # Record some timeout events
        health.record_timeout_event("test_service", "test_op", 30.0, "timeout error")
        health.record_timeout_event("another_service", "another_op", 15.0, "another error")

        assert len(health.timeout_events) == 2

        # Check timeout health
        timeout_health = await health.check_timeout_health()
        assert timeout_health["total_recent_timeouts"] == 2
        assert len(timeout_health["recent_timeout_events"]) == 2


class TestErrorHandlingValidation:
    """Test error handling and structured error responses."""

    @pytest.mark.asyncio
    async def test_timeout_exception_handler(self):
        """Test timeout exception handler creates proper response."""
        from fastapi import Request
        from fastapi.responses import JSONResponse

        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.url = Mock()
        mock_request.url.path = "/test"
        mock_request.method = "GET"
        mock_request.state = Mock()
        mock_request.state.request_id = "test-request-id"

        # Create timeout exception
        exc = TimeoutException(
            message="Request timed out",
            details={"timeout_limit": 30.0, "actual_duration": 35.0}
        )

        response = await timeout_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 408

        response_data = response.body
        assert b"TIMEOUT_ERROR" in response_data
        assert b"Request timed out" in response_data

    @pytest.mark.asyncio
    async def test_circuit_breaker_exception_handler(self):
        """Test circuit breaker exception handler creates proper response."""
        from fastapi import Request
        from fastapi.responses import JSONResponse

        mock_request = Mock(spec=Request)
        mock_request.url = Mock()
        mock_request.url.path = "/api/test"
        mock_request.method = "POST"
        mock_request.state = Mock()
        mock_request.state.request_id = "test-request-id"

        exc = CircuitBreakerException(
            message="Service temporarily unavailable",
            details={"failure_count": 5}
        )

        response = await circuit_breaker_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 503

        response_data = response.body
        assert b"CIRCUIT_BREAKER_OPEN" in response_data
        assert b"Service temporarily unavailable" in response_data


class TestEndToEndTesting:
    """End-to-end tests simulating real-world failure scenarios."""

    @pytest.mark.asyncio
    async def test_simulated_network_failures(self):
        """Test system behavior under simulated network failures."""
        cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=2))

        # Simulate network failures
        async def failing_operation():
            raise Exception("Network timeout")

        # First failure
        with pytest.raises(Exception):
            await cb.call(failing_operation)
        assert cb.state == CircuitBreakerState.CLOSED

        # Second failure - should open circuit breaker
        with pytest.raises(Exception):
            await cb.call(failing_operation)
        assert cb.state == CircuitBreakerState.OPEN

        # Subsequent calls should be blocked
        with pytest.raises(Exception) as exc_info:
            await cb.call(lambda: asyncio.sleep(0))
        assert "Circuit breaker is OPEN" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_simulation(self):
        """Test system behavior under simulated load."""
        cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3))

        async def sometimes_failing_operation(should_fail=False):
            if should_fail:
                raise Exception("Load-induced failure")
            await asyncio.sleep(0.01)  # Simulate some work
            return "success"

        # Mix of successes and failures - need exactly 3 consecutive failures
        operations = [
            (True, "failure"),   # Failure 1
            (True, "failure"),   # Failure 2
            (True, "failure"),   # Failure 3 - should open circuit
        ]

        for should_fail, expected_type in operations:
            with pytest.raises(Exception):
                await cb.call(lambda: sometimes_failing_operation(should_fail))

        # Circuit should be open after 3 failures
        assert cb.state == CircuitBreakerState.OPEN

    @pytest.mark.asyncio
    async def test_recovery_behavior(self):
        """Test circuit breaker recovery after failures."""
        cb = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.1,  # Short recovery time for testing
            success_threshold=2
        ))

        async def operation(should_fail=False):
            if should_fail:
                raise Exception("Failure")
            return "success"

        # Cause failures to open circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(lambda: operation(True))
        assert cb.state == CircuitBreakerState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(0.2)

        # Next call should attempt (half-open)
        result = await cb.call(lambda: operation(False))
        assert result == "success"
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Another success should close the circuit
        result = await cb.call(lambda: operation(False))
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])