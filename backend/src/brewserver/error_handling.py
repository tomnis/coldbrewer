"""
Error handling utilities for the cold brewer application.

Provides consistent error handling, logging, and recovery mechanisms.
"""
import traceback
import asyncio
from typing import Callable, TypeVar, Optional, Any
from datetime import datetime, timezone

from log import logger
from model import BrewErrorResponse, ErrorSeverity, ErrorCategory
from brewserver.exceptions import (
    TransientError, 
    PermanentError,
    ScaleConnectionError,
    ScaleReadError,
    ScaleNotFoundError,
    ScaleBatteryLowError,
    ValveOperationError,
    ValveTimeoutError,
    ValveNotAcquiredError,
    TimeSeriesConnectionError,
    TimeSeriesWriteError,
    BrewConflictError,
    BrewNotFoundError,
    InvalidBrewStateError,
    BrewAbortedError,
    StrategyError,
    ConfigurationError,
)


T = TypeVar('T')


def create_error_response(
    message: str,
    category: ErrorCategory,
    severity: ErrorSeverity,
    retryable: bool,
    brew_id: Optional[str] = None,
    detailed: Optional[str] = None,
    suggestion: Optional[str] = None,
    exception_type: Optional[str] = None,
) -> dict:
    """Create a standardized error response dict."""
    return BrewErrorResponse(
        error=message,
        error_detailed=detailed,
        category=category,
        severity=severity,
        timestamp=datetime.now(timezone.utc),
        retryable=retryable,
        brew_id=brew_id,
        recovery_suggestion=suggestion,
        exception_type=exception_type,
    ).model_dump(mode='json')


def handle_scale_error(
    error: Exception,
    brew_id: Optional[str] = None,
    retry_count: int = 0,
) -> dict:
    """Handle scale-related errors with specific messages."""
    if isinstance(error, ScaleNotFoundError):
        return create_error_response(
            message="Scale not found",
            category=ErrorCategory.SCALE,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Check the scale MAC address in configuration and ensure the scale is powered on and in range.",
            exception_type=type(error).__name__,
        )
    elif isinstance(error, ScaleConnectionError):
        return create_error_response(
            message="Scale connection failed",
            category=ErrorCategory.SCALE,
            severity=ErrorSeverity.ERROR,
            retryable=True,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Check that the scale is powered on and in range. Try power cycling the scale.",
            exception_type=type(error).__name__,
        )
    elif isinstance(error, ScaleReadError):
        return create_error_response(
            message="Failed to read from scale",
            category=ErrorCategory.SCALE,
            severity=ErrorSeverity.ERROR,
            retryable=True,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Ensure scale is stable and nothing is touching it.",
            exception_type=type(error).__name__,
        )
    elif isinstance(error, ScaleBatteryLowError):
        return create_error_response(
            message="Scale battery is low",
            category=ErrorCategory.SCALE,
            severity=ErrorSeverity.WARNING,
            retryable=True,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Replace the scale battery soon to avoid interruption.",
            exception_type=type(error).__name__,
        )
    else:
        # Unknown scale error
        logger.error(f"Unknown scale error: {error}\n{traceback.format_exc()}")
        return create_error_response(
            message="Unknown scale error",
            category=ErrorCategory.SCALE,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Check scale connection and restart the application.",
            exception_type=type(error).__name__,
        )


def handle_valve_error(
    error: Exception,
    brew_id: Optional[str] = None,
) -> dict:
    """Handle valve-related errors."""
    if isinstance(error, ValveOperationError):
        return create_error_response(
            message=f"Valve operation failed: {error.operation}",
            category=ErrorCategory.VALVE,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Check that the motor kit is connected and functioning.",
            exception_type=type(error).__name__,
        )
    elif isinstance(error, ValveTimeoutError):
        return create_error_response(
            message=f"Valve operation timed out: {error.operation}",
            category=ErrorCategory.VALVE,
            severity=ErrorSeverity.ERROR,
            retryable=True,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Check that the valve is not stuck or obstructed.",
            exception_type=type(error).__name__,
        )
    elif isinstance(error, ValveNotAcquiredError):
        return create_error_response(
            message="Valve not acquired",
            category=ErrorCategory.VALVE,
            severity=ErrorSeverity.WARNING,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Acquire the valve before performing operations.",
            exception_type=type(error).__name__,
        )
    else:
        logger.error(f"Unknown valve error: {error}\n{traceback.format_exc()}")
        return create_error_response(
            message="Unknown valve error",
            category=ErrorCategory.VALVE,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            exception_type=type(error).__name__,
        )


def handle_brew_error(
    error: Exception,
    brew_id: Optional[str] = None,
) -> dict:
    """Handle brew-related errors."""
    if isinstance(error, BrewConflictError):
        return create_error_response(
            message="A brew is already in progress",
            category=ErrorCategory.BREW,
            severity=ErrorSeverity.WARNING,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Stop the current brew before starting a new one.",
            exception_type=type(error).__name__,
        )
    elif isinstance(error, BrewNotFoundError):
        return create_error_response(
            message="Brew not found",
            category=ErrorCategory.BREW,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            exception_type=type(error).__name__,
        )
    elif isinstance(error, InvalidBrewStateError):
        return create_error_response(
            message=f"Invalid operation for current brew state",
            category=ErrorCategory.BREW,
            severity=ErrorSeverity.WARNING,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            suggestion=f"Wait for brew to be in a valid state before {error.operation}.",
            exception_type=type(error).__name__,
        )
    elif isinstance(error, BrewAbortedError):
        return create_error_response(
            message="Brew was aborted",
            category=ErrorCategory.BREW,
            severity=ErrorSeverity.INFO,
            retryable=True,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="You can start a new brew.",
            exception_type=type(error).__name__,
        )
    elif isinstance(error, StrategyError):
        return create_error_response(
            message=f"Strategy error: {error.strategy_name}",
            category=ErrorCategory.BREW,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Check strategy parameters and try again.",
            exception_type=type(error).__name__,
        )
    else:
        logger.error(f"Unknown brew error: {error}\n{traceback.format_exc()}")
        return create_error_response(
            message="Unknown brew error",
            category=ErrorCategory.BREW,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            exception_type=type(error).__name__,
        )


def handle_timeseries_error(
    error: Exception,
    brew_id: Optional[str] = None,
) -> dict:
    """Handle time series / InfluxDB related errors."""
    if isinstance(error, TimeSeriesConnectionError):
        return create_error_response(
            message="Database connection failed",
            category=ErrorCategory.TIMESERIES,
            severity=ErrorSeverity.ERROR,
            retryable=True,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Check that InfluxDB is running and accessible.",
            exception_type=type(error).__name__,
        )
    elif isinstance(error, TimeSeriesWriteError):
        return create_error_response(
            message="Failed to write data",
            category=ErrorCategory.TIMESERIES,
            severity=ErrorSeverity.ERROR,
            retryable=True,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="Data collection will continue. This may resolve on its own.",
            exception_type=type(error).__name__,
        )
    else:
        logger.error(f"Unknown timeseries error: {error}\n{traceback.format_exc()}")
        return create_error_response(
            message="Unknown database error",
            category=ErrorCategory.TIMESERIES,
            severity=ErrorSeverity.ERROR,
            retryable=True,
            brew_id=brew_id,
            detailed=str(error),
            exception_type=type(error).__name__,
        )


def handle_configuration_error(
    error: Exception,
    brew_id: Optional[str] = None,
) -> dict:
    """Handle configuration-related errors."""
    if isinstance(error, ConfigurationError):
        return create_error_response(
            message="Configuration error",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            suggestion=f"Check the configuration parameter: {error.parameter}",
            exception_type=type(error).__name__,
        )
    else:
        logger.error(f"Unknown configuration error: {error}\n{traceback.format_exc()}")
        return create_error_response(
            message="Unknown configuration error",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            exception_type=type(error).__name__,
        )


def handle_generic_error(
    error: Exception,
    category: ErrorCategory = ErrorCategory.BREW,
    brew_id: Optional[str] = None,
) -> dict:
    """Handle any generic error with a fallback response."""
    logger.error(f"Unhandled error: {error}\n{traceback.format_exc()}")
    return create_error_response(
        message="An unexpected error occurred",
        category=category,
        severity=ErrorSeverity.ERROR,
        retryable=False,
        brew_id=brew_id,
        detailed=str(error),
        suggestion="Please check the logs for more details or restart the application.",
        exception_type=type(error).__name__,
    )


def handle_exception(error: Exception, brew_id: Optional[str] = None) -> dict:
    """Route an exception to the appropriate handler based on its type.
    
    This is the main entry point for handling exceptions from anywhere in the code.
    """
    # Check for known exception types in order of specificity
    
    # Scale errors
    if isinstance(error, (ScaleNotFoundError, ScaleConnectionError, ScaleReadError, ScaleBatteryLowError)):
        return handle_scale_error(error, brew_id)
    
    # Valve errors
    if isinstance(error, (ValveOperationError, ValveTimeoutError, ValveNotAcquiredError)):
        return handle_valve_error(error, brew_id)
    
    # Time series errors
    if isinstance(error, (TimeSeriesConnectionError, TimeSeriesWriteError)):
        return handle_timeseries_error(error, brew_id)
    
    # Brew errors
    if isinstance(error, (BrewConflictError, BrewNotFoundError, InvalidBrewStateError, BrewAbortedError, StrategyError)):
        return handle_brew_error(error, brew_id)
    
    # Configuration errors
    if isinstance(error, ConfigurationError):
        return handle_configuration_error(error, brew_id)
    
    # Transient errors (generic handling)
    if isinstance(error, TransientError):
        category = error.category if hasattr(error, 'category') else ErrorCategory.BREW
        return create_error_response(
            message=error.message,
            category=category,
            severity=ErrorSeverity.ERROR,
            retryable=True,
            brew_id=brew_id,
            detailed=str(error),
            suggestion="This error may resolve on its own. The system will retry automatically.",
            exception_type=type(error).__name__,
        )
    
    # Permanent errors (generic handling)
    if isinstance(error, PermanentError):
        category = error.category if hasattr(error, 'category') else ErrorCategory.BREW
        return create_error_response(
            message=error.message,
            category=category,
            severity=ErrorSeverity.ERROR,
            retryable=False,
            brew_id=brew_id,
            detailed=str(error),
            exception_type=type(error).__name__,
        )
    
    # Unknown errors
    return handle_generic_error(error, ErrorCategory.BREW, brew_id)


class ErrorRecovery:
    """Handles error recovery with retry logic for transient failures."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def retry_async(
        self,
        func: Callable[..., T],
        *args,
        error_message: str = "Operation failed",
        **kwargs,
    ) -> T:
        """Retry an async function with exponential backoff."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except PermanentError:
                # Don't retry permanent errors
                raise
            except Exception as e:
                last_error = e
                delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"{error_message} (attempt {attempt + 1}/{self.max_retries}): {e}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
        
        # All retries exhausted
        raise last_error
    
    def retry_sync(
        self,
        func: Callable[..., T],
        *args,
        error_message: str = "Operation failed",
        **kwargs,
    ) -> T:
        """Retry a sync function with exponential backoff."""
        import time
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except PermanentError:
                # Don't retry permanent errors
                raise
            except Exception as e:
                last_error = e
                delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"{error_message} (attempt {attempt + 1}/{self.max_retries}): {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
        
        # All retries exhausted
        raise last_error


# Global error recovery instance
error_recovery = ErrorRecovery(max_retries=3, base_delay=1.0)
