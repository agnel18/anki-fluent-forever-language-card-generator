# infrastructure/{language}/{lang_code}_circuit_breaker.py
"""
{Language} Circuit Breaker - Infrastructure Component

GOLD STANDARD CIRCUIT BREAKER IMPLEMENTATION:
This component prevents cascade failures in AI service calls.
It implements the circuit breaker pattern for fault tolerance.

RESPONSIBILITIES:
1. Monitor AI service call success/failure
2. Open circuit when failure threshold exceeded
3. Allow limited requests in half-open state for testing
4. Automatically reset to closed state on success
5. Provide configurable failure thresholds and timeouts

CIRCUIT BREAKER FEATURES:
- Three states: Closed, Open, Half-Open
- Configurable failure thresholds
- Automatic recovery testing
- State transition logging
- Exception type filtering

INTEGRATION:
- Used by AI service for resilient API calls
- Configurable per language requirements
- Reports state changes to monitoring
- Handles various exception types
"""
# type: ignore  # Template file with placeholders - ignore type checking

import time
from enum import Enum
from typing import Tuple, Any, Dict


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class LanguageCircuitBreaker:
    """
    Circuit breaker for {Language} AI service protection.

    GOLD STANDARD IMPLEMENTATION:
    - Three-state pattern (Closed/Open/Half-Open)
    - Configurable thresholds and timeouts
    - Exception type filtering
    - State transition callbacks
    - Performance monitoring integration
    """

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: Tuple = (Exception,),
                 success_threshold: int = 3):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception types to count as failures
            success_threshold: Number of successes needed in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

        # State management
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

        # Monitoring
        self._state_change_callbacks = []
        self._performance_monitor = None

    def call(self, func, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenException: When circuit breaker is open
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self._transition_to(CircuitBreakerState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenException("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True

        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._transition_to(CircuitBreakerState.CLOSED)
                self.success_count = 0
        else:
            # Reset failure count on success in closed state
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self._transition_to(CircuitBreakerState.OPEN)

    def _transition_to(self, new_state: CircuitBreakerState):
        """Transition to new state and notify callbacks"""
        old_state = self.state
        self.state = new_state

        # Reset counters on state changes
        if new_state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
        elif new_state == CircuitBreakerState.HALF_OPEN:
            self.success_count = 0

        # Notify callbacks
        for callback in self._state_change_callbacks:
            try:
                callback(old_state, new_state)
            except Exception:
                # Don't let callback errors break the circuit breaker
                pass

        # Notify performance monitor
        if self._performance_monitor:
            self._performance_monitor.record_circuit_breaker_state_change(
                old_state.value, new_state.value
            )

    def get_state(self) -> str:
        """Get current circuit breaker state"""
        return self.state.value

    def reset(self):
        """Manually reset circuit breaker to closed state"""
        self._transition_to(CircuitBreakerState.CLOSED)

    def add_state_change_callback(self, callback):
        """Add callback for state changes"""
        self._state_change_callbacks.append(callback)

    def remove_state_change_callback(self, callback):
        """Remove state change callback"""
        if callback in self._state_change_callbacks:
            self._state_change_callbacks.remove(callback)

    def set_performance_monitor(self, monitor):
        """Set performance monitoring instance"""
        self._performance_monitor = monitor

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time,
            'time_since_last_failure': time.time() - (self.last_failure_time or time.time()),
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout,
            'success_threshold': self.success_threshold
        }