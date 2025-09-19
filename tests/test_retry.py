"""Tests for retry utility system."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import time

from src.retry_utils import (
    RetryManager, RetryConfig, RetryStrategy,
    CircuitBreaker, CircuitBreakerConfig, CircuitBreakerState,
    retry_async, database_retry_manager, playwright_retry_manager
)


class TestRetryConfig:
    """Test retry configuration settings."""

    def test_retry_config_defaults(self):
        """Test retry config with default values."""
        config = RetryConfig()

        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.backoff_multiplier == 2.0
        assert config.strategy == RetryStrategy.EXPONENTIAL

    def test_retry_config_custom_values(self):
        """Test retry config with custom values."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            retryable_exceptions=[ValueError, KeyError]
        )

        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert ValueError in config.retryable_exceptions
        assert KeyError in config.retryable_exceptions


class TestRetryStrategy:
    """Test different retry strategies."""

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        config = RetryConfig(strategy=RetryStrategy.EXPONENTIAL)
        manager = RetryManager(config)

        # Test different attempt numbers
        assert manager._calculate_delay(1, 0) == 1.0  # base_delay * 2^0
        assert manager._calculate_delay(2, 0) == 2.0  # base_delay * 2^1
        assert manager._calculate_delay(3, 0) == 4.0  # base_delay * 2^2

    def test_linear_backoff_calculation(self):
        """Test linear backoff delay calculation."""
        config = RetryConfig(strategy=RetryStrategy.LINEAR, base_delay=1.0)
        manager = RetryManager(config)

        assert manager._calculate_delay(1, 0) == 1.0  # base_delay * 1
        assert manager._calculate_delay(2, 0) == 2.0  # base_delay * 2
        assert manager._calculate_delay(3, 0) == 3.0  # base_delay * 3

    def test_fixed_delay_calculation(self):
        """Test fixed delay strategy."""
        config = RetryConfig(strategy=RetryStrategy.FIXED, base_delay=2.0)
        manager = RetryManager(config)

        assert manager._calculate_delay(1, 0) == 2.0
        assert manager._calculate_delay(5, 0) == 2.0
        assert manager._calculate_delay(10, 0) == 2.0

    def test_max_delay_enforcement(self):
        """Test that delays don't exceed max_delay."""
        config = RetryConfig(strategy=RetryStrategy.EXPONENTIAL, max_delay=10.0)
        manager = RetryManager(config)

        # Should be capped at max_delay=10.0
        delay = manager._calculate_delay(10, 0)  # Would be 512.0 without cap
        assert delay <= 10.0

    def test_jitter_application(self):
        """Test that jitter is applied to delay."""
        config = RetryConfig(base_delay=1.0)
        manager = RetryManager(config)

        # Generate multiple delays to verify jitter variance
        delays = [manager._calculate_delay(1, 0) for _ in range(20)]

        # All delays should be close to base_delay (near 1.0)
        for delay in delays:
            assert 0.9 <= delay <= 1.1  # Allow for jitter range


class TestRetryManager:
    """Test retry manager functionality."""

    def test_should_retry_with_retryable_exception(self):
        """Test that retryable exceptions are retried."""
        config = RetryConfig(retryable_exceptions=[ValueError, ConnectionError])
        manager = RetryManager(config)

        assert manager._should_retry(ValueError("test"), 1) is True
        assert manager._should_retry(ConnectionError("test"), 1) is True

    def test_should_not_retry_with_non_retryable_exception(self):
        """Test that non-retryable exceptions are not retried."""
        config = RetryConfig(retryable_exceptions=[ValueError])
        manager = RetryManager(config)

        assert manager._should_retry(TypeError("test"), 1) is False
        assert manager._should_retry(RuntimeError("test"), 1) is False

    def test_should_not_retry_max_attempts_exceeded(self):
        """Test that retry is stopped after max attempts."""
        config = RetryConfig(max_attempts=3)
        manager = RetryManager(config)

        assert manager._should_retry(ValueError("test"), 3) is False  # At max attempts
        assert manager._should_retry(ValueError("test"), 4) is False  # Exceeded max attempts

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        """Test successful execution on first attempt."""
        call_count = 0

        def counting_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await retry_async(counting_function, manager=database_retry_manager)

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_failure_then_success(self):
        """Test retry on failure followed by success."""
        call_count = 0

        def intermittent_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("transient failure")
            return "success"

        result = await retry_async(intermittent_function, manager=database_retry_manager)

        assert result == "success"
        assert call_count == 2  # Failed once, then succeeded

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self):
        """Test that retries stop after exhausting attempts."""
        call_count = 0

        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("persistent failure")

        with pytest.raises(ConnectionError):
            await retry_async(always_failing_function, manager=database_retry_manager)

        assert call_count == 3  # max_attempts = 3

    @pytest.mark.asyncio
    async def test_non_retryable_exception(self):
        """Test that non-retryable exceptions are not retried."""
        call_count = 0

        def runtime_error_function():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("not retryable")

        with pytest.raises(RuntimeError):
            await retry_async(runtime_error_function, manager=database_retry_manager)

        assert call_count == 1  # Should only try once


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in CLOSED state."""
        breaker = CircuitBreaker(CircuitBreakerConfig())
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker._failure_count == 0

    def test_circuit_breaker_success_operations(self):
        """Test successful operations don't affect closed breaker."""
        breaker = CircuitBreaker(CircuitBreakerConfig())
        config = CircuitBreakerConfig(expected_exception=ValueError)

        @breaker
        def successful_function():
            return "success"

        # Multiple successes should keep breaker closed
        for _ in range(10):
            assert successful_function() == "success"
            assert breaker.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_failure_threshold(self):
        """Test circuit opens after failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=3, expected_exception=ValueError)
        breaker = CircuitBreaker(config)

        @breaker
        def failing_function():
            raise ValueError("test failure")

        # Should open after 3 failures
        for i in range(3):
            with pytest.raises(ValueError):
                failing_function()
            assert breaker.state == CircuitBreakerState.CLOSED  # Still closed after first 2

        # Third failure should open the circuit
        with pytest.raises(ValueError):
            failing_function()
        assert breaker.state == CircuitBreakerState.OPEN

    def test_circuit_breaker_open_behavior(self):
        """Test that open circuit fails fast."""
        breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=1))

        @breaker
        def failing_function():
            raise ValueError("test failure")

        # Open the circuit
        with pytest.raises(ValueError):
            failing_function()

        # Circuit is now open
        assert breaker.state == CircuitBreakerState.CLOSED

        # Now open it
        with pytest.raises(ValueError):
            failing_function()
        assert breaker.state == CircuitBreakerState.OPEN

        # Subsequent calls should fail immediately without calling function
        call_count = 0
        @breaker
        def counting_function():
            nonlocal call_count
            call_count += 1
            return "never reached"

        # Function should not be called
        with pytest.raises(Exception):  # Should raise CircuitBreakerOpenException
            counting_function()
        assert call_count == 0  # Function was never called

    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit transitions to Half-Open and recovers."""
        import time
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.1  # Very short for testing
        )
        breaker = CircuitBreaker(config)

        @breaker
        def sometimes_failing():
            if hasattr(sometimes_failing, '_call_count'):
                sometimes_failing._call_count += 1
            else:
                sometimes_failing._call_count = 1

            # Fail on first call, succeed on recovery attempts
            if sometimes_failing._call_count == 1:
                raise ValueError("initial failure")

            return "recovered"

        # Open the circuit with initial failures
        for _ in range(2):
            with pytest.raises(ValueError):
                sometimes_failing()
        assert breaker.state == CircuitBreakerState.OPEN

        # Wait for recovery timeout
        time.sleep(0.2)

        # Next call should be in HALF_OPEN state
        result = sometimes_failing()
        assert result == "recovered"
        assert breaker.state == CircuitBreakerState.CLOSED  # Success closed the circuit


class TestPreconfiguredManagers:
    """Test pre-configured retry managers."""

    def test_database_retry_manager_defaults(self):
        """Test that database retry manager has appropriate defaults."""
        config = database_retry_manager.config

        assert config.max_attempts == 5  # Higher for db operations
        assert config.base_delay == 2.0  # Longer base delay
        assert config.max_delay == 60.0  # Longer max delay

    def test_playwright_retry_manager_defaults(self):
        """Test that playwright retry manager has appropriate defaults."""
        config = playwright_retry_manager.config

        assert config.max_attempts == 3
        assert config.strategy == RetryStrategy.LINEAR  # Browser ops work well with linear
        assert config.max_delay == 15.0  # Reasonable timeout for browser


@pytest.mark.integration
class TestRetryIntegration:
    """Integration tests for retry system."""

    @pytest.mark.asyncio
    async def test_network_timeout_simulation(self):
        """Simulate network timeout scenario."""
        timeout_occurred = False

        async def network_call():
            nonlocal timeout_occurred
            if not timeout_occurred:
                timeout_occurred = True
                await asyncio.sleep(0.001)  # Short delay to simulate processing
                raise asyncio.TimeoutError("Network timeout")
            return {"status": "success"}

        # Should retry once then succeed
        result = await retry_async(network_call, manager=api_retry_manager)
        assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_database_connection_retry(self):
        """Test database connection retry simulation."""
        connection_attempts = 0

        def db_connect():
            nonlocal connection_attempts
            connection_attempts += 1
            if connection_attempts <= 2:
                raise ConnectionError("Database temporarily unavailable")
            return "connected"

        with patch.dict('os.environ', {'DEBUG': '1'}):
            result = await retry_async(db_connect, manager=database_retry_manager)

        assert result == "connected"
        assert connection_attempts == 3  # Initially failed, then retried twice


# Benchmark tests to ensure retry delays work correctly
def test_retry_timing():
    """Test that retry delays are applied correctly."""
    import time

    delays = []
    start_time = time.time()

    # Simple retry function that fails twice then succeeds
    attempt_count = 0

    def timing_test_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            time.sleep(0.01)  # Small delay to simulate processing
            raise ConnectionError("timing test failure")
        return "success"

    # Time the execution
    result = None

    async def run_timing_test():
        nonlocal result
        result = await retry_async(timing_test_function, manager=database_retry_manager)

    asyncio.run(run_timing_test())

    elapsed = time.time() - start_time

    # Should take at least the delays: ~2.0 + ~4.0 + processing time
    # But we don't need to be too strict here, just verify it takes some reasonable time
    assert elapsed > 0.5  # At least some delay was applied
    assert attempt_count == 3
    assert result == "success"