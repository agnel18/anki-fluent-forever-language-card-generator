# Error Recovery and Resilience Module
"""
Comprehensive error recovery mechanisms for API calls and external services.
Provides retry logic, fallback mechanisms, and graceful degradation.
"""

import time
import logging
import requests
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from functools import wraps
import random

logger = logging.getLogger(__name__)

T = TypeVar('T')

class APIError(Exception):
    """Base exception for API-related errors."""
    pass

class NetworkError(APIError):
    """Network connectivity or timeout errors."""
    pass

class APIQuotaError(APIError):
    """API quota or rate limit exceeded."""
    pass

class APIAuthError(APIError):
    """API authentication or authorization errors."""
    pass

class APIServerError(APIError):
    """API server-side errors (5xx)."""
    pass

def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_on: tuple = (NetworkError, requests.exceptions.RequestException, requests.exceptions.Timeout)
) -> Callable:
    """
    Decorator that implements exponential backoff retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Factor by which delay increases each retry
        jitter: Add random jitter to prevent thundering herd
        retry_on: Exception types to retry on
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
                        raise last_exception

                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)  # 50-100% of calculated delay

                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)

            # This should never be reached, but just in case
            raise last_exception

        return wrapper
    return decorator

def handle_api_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle and classify API errors appropriately.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout as e:
            logger.error(f"API timeout in {func.__name__}: {e}")
            raise NetworkError(f"API request timed out: {e}") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"API connection error in {func.__name__}: {e}")
            raise NetworkError(f"API connection failed: {e}") from e
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None

            if status_code == 401:
                logger.error(f"API authentication error in {func.__name__}: {e}")
                raise APIAuthError(f"API authentication failed: {e}") from e
            elif status_code == 429:
                # Extract rate limit reset information from headers
                reset_info = ""
                if e.response:
                    # Try common rate limit headers
                    reset_time = (e.response.headers.get('x-ratelimit-reset') or
                                e.response.headers.get('retry-after') or
                                e.response.headers.get('x-rate-limit-reset'))
                    if reset_time:
                        try:
                            # Convert to readable format if it's a timestamp
                            import datetime
                            if reset_time.isdigit():
                                reset_dt = datetime.datetime.fromtimestamp(int(reset_time))
                                reset_info = f" (resets at {reset_dt.strftime('%H:%M:%S')})"
                            else:
                                reset_info = f" (resets in {reset_time} seconds)"
                        except:
                            reset_info = f" (reset info: {reset_time})"
                
                upgrade_suggestion = " Consider upgrading your API plan for higher limits or wait for the reset."
                error_msg = f"API rate limit exceeded{reset_info}.{upgrade_suggestion}"
                logger.error(f"API rate limit exceeded in {func.__name__}: {error_msg}")
                raise APIQuotaError(error_msg) from e
            elif status_code and status_code >= 500:
                logger.error(f"API server error in {func.__name__} (status {status_code}): {e}")
                raise APIServerError(f"API server error: {e}") from e
            else:
                logger.error(f"API HTTP error in {func.__name__} (status {status_code}): {e}")
                raise APIError(f"API request failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise APIError(f"Unexpected API error: {e}") from e

    return wrapper

def with_fallback(
    fallback_value: Any = None,
    fallback_func: Optional[Callable[..., T]] = None,
    log_errors: bool = True
) -> Callable:
    """
    Decorator that provides fallback behavior when the main function fails.

    Args:
        fallback_value: Value to return on failure (if fallback_func not provided)
        fallback_func: Function to call for fallback (receives same args as main function)
        log_errors: Whether to log errors
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.warning(f"Falling back for {func.__name__}: {e}")

                if fallback_func:
                    try:
                        return fallback_func(*args, **kwargs)
                    except Exception as fallback_e:
                        if log_errors:
                            logger.error(f"Fallback also failed for {func.__name__}: {fallback_e}")
                        return fallback_value

                return fallback_value

        return wrapper
    return decorator

def graceful_degradation(
    component_name: str,
    continue_on_failure: bool = True,
    log_level: str = "warning"
) -> Callable:
    """
    Decorator for graceful degradation - logs failures but allows execution to continue.

    Args:
        component_name: Name of the component for logging
        continue_on_failure: Whether to continue execution or re-raise
        log_level: Logging level ('debug', 'info', 'warning', 'error')
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_func = getattr(logger, log_level, logger.warning)
                log_func(f"Graceful degradation: {component_name} failed: {e}")

                if not continue_on_failure:
                    raise

                return None

        return wrapper
    return decorator

# Specific error recovery decorators for different API types

def resilient_gemini_call(max_retries: int = 3):
    """Decorator for Google Gemini API calls with retry logic and error handling."""
    return lambda func: retry_with_exponential_backoff(
        max_retries=max_retries,
        retry_on=(NetworkError, APIServerError, APIQuotaError)
    )(handle_api_errors(func))

def resilient_google_search_call(max_retries: int = 2):
    """Decorator for Google Custom Search API calls with retry logic and error handling."""
    return lambda func: retry_with_exponential_backoff(
        max_retries=max_retries,
        retry_on=(NetworkError, APIServerError)
    )(handle_api_errors(func))

def resilient_audio_generation(max_retries: int = 1):
    """Decorator for audio generation with minimal retries (expensive operations)."""
    return lambda func: retry_with_exponential_backoff(
        max_retries=max_retries,
        retry_on=(NetworkError,)
    )(handle_api_errors(func))

# Utility functions for error recovery

def safe_api_call(
    api_func: Callable[..., T],
    *args,
    fallback_value: Any = None,
    max_retries: int = 3,
    **kwargs
) -> T:
    """
    Safely call an API function with automatic retry and fallback.

    Args:
        api_func: The API function to call
        *args: Positional arguments for the API function
        fallback_value: Value to return if all retries fail
        max_retries: Maximum number of retry attempts
        **kwargs: Keyword arguments for the API function

    Returns:
        API response or fallback value
    """
    decorated_func = retry_with_exponential_backoff(max_retries=max_retries)(
        handle_api_errors(api_func)
    )

    try:
        return decorated_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Safe API call failed for {api_func.__name__}: {e}")
        return fallback_value

def create_error_summary(errors: List[Dict[str, Any]]) -> str:
    """
    Create a user-friendly error summary from a list of errors.

    Args:
        errors: List of error dictionaries with 'component', 'error', 'critical' keys

    Returns:
        Formatted error summary string
    """
    if not errors:
        return "No errors encountered."

    critical_errors = [e for e in errors if e.get('critical', False)]
    non_critical_errors = [e for e in errors if not e.get('critical', False)]

    summary = []

    if critical_errors:
        summary.append(f"🚨 Critical Errors ({len(critical_errors)}):")
        for error in critical_errors:
            summary.append(f"  • {error['component']}: {error['error']}")

    if non_critical_errors:
        summary.append(f"⚠️ Non-Critical Issues ({len(non_critical_errors)}):")
        for error in non_critical_errors:
            summary.append(f"  • {error['component']}: {error['error']}")

    return "\n".join(summary)