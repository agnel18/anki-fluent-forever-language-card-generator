# Circuit Breaker Pattern for API Resilience
# Implements circuit breaker pattern to handle API failures gracefully

import time
import threading
from enum import Enum
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker implementation for API resilience.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is failing, requests are rejected immediately
    - HALF_OPEN: Testing if service has recovered, limited requests allowed
    """

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: Exception = Exception,
                 success_threshold: int = 3,
                 name: str = "CircuitBreaker"):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying half-open state
            expected_exception: Exception type to catch as failures
            success_threshold: Number of successes needed to close circuit from half-open
            name: Name for logging purposes
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold
        self.name = name

        # State management
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None

        # Thread safety
        self._lock = threading.RLock()

    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply circuit breaker to a function."""
        def wrapper(*args, **kwargs) -> Any:
            return self.call(func, *args, **kwargs)
        return wrapper

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result or raises CircuitBreakerOpenException

        Raises:
            CircuitBreakerOpenException: When circuit is open
        """
        with self._lock:
            if self._state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitBreakerState.HALF_OPEN
                    self._success_count = 0
                    logger.info(f"CircuitBreaker '{self.name}': Half-open, testing recovery")
                else:
                    raise CircuitBreakerOpenException(
                        f"CircuitBreaker '{self.name}' is OPEN. "
                        f"Next retry in {self._time_until_reset()} seconds"
                    )

            try:
                result = func(*args, **kwargs)

                # Success handling
                self._on_success()
                return result

            except self.expected_exception as e:
                # Failure handling
                self._on_failure()
                raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._last_failure_time is None:
            return True
        return time.time() - self._last_failure_time >= self.recovery_timeout

    def _time_until_reset(self) -> float:
        """Calculate time until next reset attempt."""
        if self._last_failure_time is None:
            return 0.0
        elapsed = time.time() - self._last_failure_time
        return max(0.0, self.recovery_timeout - elapsed)

    def _on_success(self):
        """Handle successful operation."""
        self._failure_count = 0

        if self._state == CircuitBreakerState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = CircuitBreakerState.CLOSED
                self._success_count = 0
                logger.info(f"CircuitBreaker '{self.name}': Closed, service recovered")

    def _on_failure(self):
        """Handle failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitBreakerState.HALF_OPEN:
            # Failed during recovery test, go back to open
            self._state = CircuitBreakerState.OPEN
            logger.warning(f"CircuitBreaker '{self.name}': Recovery failed, back to open")
        elif self._failure_count >= self.failure_threshold:
            # Enough failures, open the circuit
            self._state = CircuitBreakerState.OPEN
            logger.warning(f"CircuitBreaker '{self.name}': Open after {self._failure_count} failures")

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    def reset(self):
        """Manually reset the circuit breaker to closed state."""
        with self._lock:
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            logger.info(f"CircuitBreaker '{self.name}': Manually reset to closed")

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass

# Global circuit breakers for different services
WIKTIONARY_BREAKER = CircuitBreaker(
    failure_threshold=10,  # Increased from 3
    recovery_timeout=60.0,  # Increased from 30
    name="WiktionaryAPI"
)

GOOGLE_TRANSLATE_BREAKER = CircuitBreaker(
    failure_threshold=10,  # Increased from 5
    recovery_timeout=120.0,  # Increased from 60
    name="GoogleTranslate"
)

# Convenience functions for common API calls
def call_with_circuit_breaker(breaker: CircuitBreaker, func: Callable, *args, **kwargs) -> Any:
    """
    Call a function with circuit breaker protection.

    Args:
        breaker: Circuit breaker instance
        func: Function to call
        *args: Arguments for function
        **kwargs: Keyword arguments for function

    Returns:
        Function result

    Raises:
        CircuitBreakerOpenException: If circuit is open
        Original exception: If function fails
    """
    return breaker.call(func, *args, **kwargs)