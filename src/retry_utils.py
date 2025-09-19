"""
Retry utilities with exponential backoff and circuit breaker patterns
Provides resilient handling of transient failures in network calls, database operations, and API requests.
"""
import asyncio
import aiohttp
import psycopg2
import random
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Union, Dict, List, Type, TypeVar
from datetime import datetime, timedelta

from src.config import config
from src.logging_config import logger, log_operation_start, log_operation_end

# Type variable for retry results
T = TypeVar('T')

class RetryStrategy(Enum):
    """Available retry strategies."""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing fast, not allowing calls
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 30.0  # seconds
    backoff_multiplier: float = 2.0
    jitter_range: float = 0.1
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retryable_exceptions: List[Type[Exception]] = None

    def __post_init__(self):
        """Set default retryable exceptions."""
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [
                ConnectionError, TimeoutError, OSError,
                asyncio.TimeoutError, aiohttp.ClientError,
                psycopg2.OperationalError, psycopg2.DatabaseError
            ]

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # consecutive failures before opening
    recovery_timeout: float = 60.0  # seconds to wait before half-open
    success_threshold: int = 3  # successes needed before closing
    expected_exception: Type[Exception] = Exception

class RetryAttempt:
    """Information about a retry attempt."""
    def __init__(self, attempt_number: int, delay: float, exception: Optional[Exception] = None):
        self.attempt_number = attempt_number
        self.delay = delay
        self.exception = exception
        self.timestamp = datetime.now()

class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(self, config: CircuitBreakerConfig, name: str = "default"):
        self.config = config
        self.name = name
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._last_attempt_time = None

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        # Check if we should transition from OPEN to HALF_OPEN
        if (self._state == CircuitBreakerState.OPEN and
            self._last_failure_time and
            (datetime.now() - self._last_failure_time).total_seconds() > self.config.recovery_timeout):
            self._state = CircuitBreakerState.HALF_OPEN
            self._success_count = 0
            logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN", extra={
                "event": "circuit_breaker_state_change",
                "breaker_name": self.name,
                "state": "half_open"
            })

        return self._state

    def _call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker logic."""
        self._last_attempt_time = datetime.now()

        if self.state == CircuitBreakerState.OPEN:
            raise CircuitBreakerOpenException(f"Circuit breaker '{self.name}' is OPEN")

        try:
            result = func(*args, **kwargs)

            if self.state == CircuitBreakerState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._close_circuit()

            return result

        except self.config.expected_exception as e:
            self._record_failure(e)
            raise

    def _record_failure(self, exception: Exception):
        """Record a failure and potentially open the circuit."""
        self._failure_count += 1
        self._last_failure_time = datetime.now()

        if (self.state == CircuitBreakerState.CLOSED and
            self._failure_count >= self.config.failure_threshold):
            self._open_circuit()

        logger.warning(f"Circuit breaker '{self.name}' recorded failure", extra={
            "event": "circuit_breaker_failure",
            "breaker_name": self.name,
            "failure_count": self._failure_count,
            "state": self._state.value
        })

    def _open_circuit(self):
        """Open the circuit breaker."""
        self._state = CircuitBreakerState.OPEN
        logger.error(f"Circuit breaker '{self.name}' OPENED after {self._failure_count} failures", extra={
            "event": "circuit_breaker_open",
            "breaker_name": self.name,
            "failure_count": self._failure_count
        })

    def _close_circuit(self):
        """Close the circuit breaker."""
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        logger.info(f"Circuit breaker '{self.name}' CLOSED", extra={
            "event": "circuit_breaker_closed",
            "breaker_name": self.name
        })

    @asynccontextmanager
    async def __call__(self, func: Callable, *args, **kwargs):
        """Async context manager for circuit breaker."""
        async def async_wrapper():
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

        try:
            yield self._call(async_wrapper)
        except Exception as e:
            self._record_failure(e)
            raise

class RetryManager:
    """Manages retry logic with different strategies."""

    def __init__(self, config: RetryConfig, name: str = "default"):
        self.config = config
        self.name = name

    def _calculate_delay(self, attempt: int, last_delay: float) -> float:
        """Calculate delay for the given attempt using configured strategy."""
        base_delay = self.config.base_delay

        if self.config.strategy == RetryStrategy.FIXED:
            delay = base_delay
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = base_delay * attempt
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = base_delay * (self.config.backoff_multiplier ** (attempt - 1))
        elif self.config.strategy == RetryStrategy.FIBONACCI:
            # Fibonacci sequence approximation
            if attempt <= 2:
                delay = base_delay
            else:
                delay = last_delay * 1.618  # Golden ratio approximation

        # Apply maximum delay and jitter
        delay = min(delay, self.config.max_delay)
        jitter = random.uniform(-self.config.jitter_range, self.config.jitter_range) * delay
        delay = max(0, delay + jitter)

        return delay

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if we should retry based on exception type and attempt count."""
        if attempt >= self.config.max_attempts:
            return False

        for retryable_type in self.config.retryable_exceptions:
            if isinstance(exception, retryable_type):
                return True

        return False

    async def _attempt_async(self, func: Callable, *args, **kwargs) -> T:
        """Execute a single retry attempt asynchronously."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)

    async def execute_async(self, func: Callable, *args, **kwargs) -> T:
        """Execute function with retry logic asynchronously."""
        last_exception = None
        last_delay = 0.0
        attempt_info = []

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                result = await self._attempt_async(func, *args, **kwargs)

                if attempt > 1:
                    logger.info(f"Retry successful on attempt {attempt}", extra={
                        "event": "retry_success",
                        "operation": self.name,
                        "attempt_number": attempt,
                        "total_attempts": len(attempt_info)
                    })

                return result

            except Exception as e:
                last_exception = e
                delay = self._calculate_delay(attempt, last_delay)

                attempt_info.append(RetryAttempt(attempt, delay, e))

                if not self._should_retry(e, attempt):
                    logger.debug(f"Not retrying after attempt {attempt}: {type(e).__name__}", extra={
                        "event": "retry_aborted",
                        "operation": self.name,
                        "attempt_number": attempt,
                        "exception_type": type(e).__name__,
                        "reason": "not_retryable" if attempt < self.config.max_attempts else "max_attempts_reached"
                    })
                    break

                if attempt < self.config.max_attempts:
                    logger.warning(f"Operation failed, retrying in {delay:.2f}s", extra={
                        "event": "retry_attempt",
                        "operation": self.name,
                        "attempt_number": attempt,
                        "delay_seconds": delay,
                        "exception_type": type(e).__name__
                    })

                    await asyncio.sleep(delay)

                last_delay = delay

        # All retries exhausted
        logger.error(f"All {self.config.max_attempts} retry attempts failed", extra={
            "event": "retry_exhausted",
            "operation": self.name,
            "total_attempts": len(attempt_info),
            "final_exception": type(last_exception).__name__ if last_exception else None
        })

        raise last_exception or Exception("Maximum retry attempts exceeded")

    def execute_sync(self, func: Callable, *args, **kwargs) -> T:
        """Execute function with retry logic synchronously."""
        last_exception = None
        last_delay = 0.0
        attempt_info = []

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                result = func(*args, **kwargs)

                if attempt > 1:
                    logger.info(f"Retry successful on attempt {attempt}", extra={
                        "event": "retry_success",
                        "operation": self.name,
                        "attempt_number": attempt,
                        "total_attempts": len(attempt_info)
                    })

                return result

            except Exception as e:
                last_exception = e
                delay = self._calculate_delay(attempt, last_delay)

                attempt_info.append(RetryAttempt(attempt, delay, e))

                if not self._should_retry(e, attempt):
                    logger.debug(f"Not retrying after attempt {attempt}: {type(e).__name__}", extra={
                        "event": "retry_aborted",
                        "operation": self.name,
                        "attempt_number": attempt,
                        "exception_type": type(e).__name__,
                        "reason": "not_retryable" if attempt < self.config.max_attempts else "max_attempts_reached"
                    })
                    break

                if attempt < self.config.max_attempts:
                    logger.warning(f"Operation failed, retrying in {delay:.2f}s", extra={
                        "event": "retry_attempt",
                        "operation": self.name,
                        "attempt_number": attempt,
                        "delay_seconds": delay,
                        "exception_type": type(e).__name__
                    })

                    time.sleep(delay)

                last_delay = delay

        # All retries exhausted
        logger.error(f"All {self.config.max_attempts} retry attempts failed", extra={
            "event": "retry_exhausted",
            "operation": self.name,
            "total_attempts": len(attempt_info),
            "final_exception": type(last_exception).__name__ if last_exception else None
        })

        raise last_exception or Exception("Maximum retry attempts exceeded")


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Global instances for common use cases
default_retry_config = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL
)

database_retry_config = RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    max_delay=60.0,
    strategy=RetryStrategy.EXPONENTIAL,
    retryable_exceptions=[
        ConnectionError, TimeoutError, OSError,
        asyncio.TimeoutError, psycopg2.OperationalError,
        psycopg2.DatabaseError, psycopg2.InterfaceError
    ]
)

api_retry_config = RetryConfig(
    max_attempts=4,
    base_delay=1.5,
    max_delay=45.0,
    strategy=RetryStrategy.EXPONENTIAL,
    retryable_exceptions=[
        ConnectionError, TimeoutError, OSError,
        asyncio.TimeoutError, aiohttp.ClientError,
        aiohttp.ClientConnectorError, aiohttp.ServerTimeoutError
    ]
)

playwright_retry_config = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=15.0,
    strategy=RetryStrategy.LINEAR,
    retryable_exceptions=[
        ConnectionError, TimeoutError, OSError,
        asyncio.TimeoutError, Exception  # Playwright can throw various exceptions
    ]
)

# Global retry managers
default_retry_manager = RetryManager(default_retry_config, "default")
database_retry_manager = RetryManager(database_retry_config, "database")
api_retry_manager = RetryManager(api_retry_config, "api")
playwright_retry_manager = RetryManager(playwright_retry_config, "playwright")

# Global circuit breakers
default_circuit_breaker = CircuitBreaker(CircuitBreakerConfig(), "default")
database_circuit_breaker = CircuitBreaker(
    CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30.0),
    "database"
)
api_circuit_breaker = CircuitBreaker(
    CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60.0),
    "api"
)


# Convenience functions
async def retry_async(func: Callable, *args, manager: Optional[RetryManager] = None, **kwargs) -> Any:
    """Convenience function for async retry execution."""
    if manager is None:
        manager = default_retry_manager
    return await manager.execute_async(func, *args, **kwargs)

def retry_sync(func: Callable, *args, manager: Optional[RetryManager] = None, **kwargs) -> Any:
    """Convenience function for sync retry execution."""
    if manager is None:
        manager = default_retry_manager
    return manager.execute_sync(func, *args, **kwargs)


# Import dependencies here to avoid circular imports
try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import psycopg2
except ImportError:
    psycopg2 = None

# Legacy import compatibility
from src.logging_config import get_logger, CorrelationContext
logger = get_logger("retry_utils")