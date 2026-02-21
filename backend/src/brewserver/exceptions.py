"""
Custom exception classes for the cold brewer application.

Provides structured exceptions for different error categories to enable
better error handling, logging, and recovery mechanisms.
"""
from typing import Optional
from enum import Enum


class ErrorSeverity(str, Enum):
    """Severity level for errors."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Category of error for better frontend handling."""
    SCALE = "scale"
    VALVE = "valve"
    TIMESERIES = "timeseries"
    BREW = "brew"
    NETWORK = "network"
    HARDWARE = "hardware"
    CONFIGURATION = "configuration"


class TransientError(Exception):
    """Base class for transient errors that can be retried.
    
    Transient errors are typically temporary conditions that may resolve
    themselves, such as network timeouts or temporary disconnections.
    """
    
    def __init__(
        self, 
        message: str, 
        retry_after: float = 1.0, 
        max_retries: int = 3,
        category: ErrorCategory = ErrorCategory.BREW
    ):
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after
        self.max_retries = max_retries
        self.retry_count = 0
        self.category = category


class PermanentError(Exception):
    """Base class for permanent errors that cannot be retried.
    
    Permanent errors indicate conditions that won't resolve with retries,
    such as invalid configuration or hardware failures.
    """
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.BREW):
        super().__init__(message)
        self.message = message
        self.category = category


# ==================== Scale-specific errors ====================

class ScaleNotFoundError(PermanentError):
    """Raised when scale cannot be found or connected.
    
    This is typically a permanent error indicating the scale MAC address
    is incorrect or the scale is not in pairing range.
    """
    
    def __init__(self, mac_address: str, message: str = None):
        msg = message or f"Scale not found at MAC address: {mac_address}"
        super().__init__(msg, ErrorCategory.SCALE)
        self.mac_address = mac_address


class ScaleConnectionError(TransientError):
    """Raised when scale connection fails.
    
    This is typically a transient error that may succeed on retry
    if the scale is temporarily unavailable.
    """
    
    def __init__(
        self, 
        message: str = "Failed to connect to scale", 
        retry_after: float = 2.0,
        mac_address: str = None
    ):
        super().__init__(message, retry_after, category=ErrorCategory.SCALE)
        self.mac_address = mac_address


class ScaleReadError(TransientError):
    """Raised when scale fails to read weight.
    
    This can happen if the scale is unstable or there's interference.
    Usually transient and may succeed on retry.
    """
    
    def __init__(
        self, 
        message: str = "Failed to read weight from scale", 
        retry_after: float = 1.0
    ):
        super().__init__(message, retry_after, category=ErrorCategory.SCALE)


class ScaleBatteryLowError(PermanentError):
    """Raised when scale battery is critically low.
    
    This is a warning that the scale may stop working soon.
    """
    
    def __init__(self, battery_percentage: int):
        msg = f"Scale battery is low: {battery_percentage}%"
        super().__init__(msg, ErrorCategory.SCALE)
        self.battery_percentage = battery_percentage


# ==================== Valve-specific errors ====================

class ValveOperationError(PermanentError):
    """Raised when valve operation fails.
    
    This is typically a permanent error indicating hardware issues
    with the motor or motor kit.
    """
    
    def __init__(self, operation: str, message: str = None):
        msg = message or f"Valve operation '{operation}' failed"
        super().__init__(msg, ErrorCategory.VALVE)
        self.operation = operation


class ValveTimeoutError(TransientError):
    """Raised when valve operation times out.
    
    This can happen if the motor is stuck or there's excessive load.
    May resolve on retry after the motor has a chance to reset.
    """
    
    def __init__(self, operation: str, timeout: float = 5.0):
        msg = f"Valve operation '{operation}' timed out after {timeout}s"
        super().__init__(msg, retry_after=1.0, category=ErrorCategory.VALVE)
        self.operation = operation
        self.timeout = timeout


class ValveNotAcquiredError(PermanentError):
    """Raised when attempting to operate valve without acquiring it first."""
    
    def __init__(self, operation: str):
        msg = f"Cannot perform '{operation}' - valve not acquired"
        super().__init__(msg, ErrorCategory.VALVE)
        self.operation = operation


# ==================== Time series / InfluxDB errors ====================

class TimeSeriesError(PermanentError):
    """Raised when time series operations fail permanently."""
    
    def __init__(self, message: str):
        super().__init__(message, ErrorCategory.TIMESERIES)


class TimeSeriesConnectionError(TransientError):
    """Raised when InfluxDB connection fails.
    
    This is typically transient as InfluxDB may be temporarily unavailable.
    """
    
    def __init__(
        self, 
        message: str = "Failed to connect to InfluxDB", 
        retry_after: float = 5.0
    ):
        super().__init__(message, retry_after, category=ErrorCategory.TIMESERIES)


class TimeSeriesWriteError(TransientError):
    """Raised when writing to InfluxDB fails.
    
    May be transient if InfluxDB is under load or has temporary issues.
    """
    
    def __init__(
        self, 
        message: str = "Failed to write data to InfluxDB", 
        retry_after: float = 2.0
    ):
        super().__init__(message, retry_after, category=ErrorCategory.TIMESERIES)


# ==================== Brew-specific errors ====================

class BrewConflictError(PermanentError):
    """Raised when attempting to start a brew while one is already in progress."""
    
    def __init__(self, current_brew_id: str):
        msg = f"A brew is already in progress with ID: {current_brew_id}"
        super().__init__(msg, ErrorCategory.BREW)
        self.current_brew_id = current_brew_id


class BrewNotFoundError(PermanentError):
    """Raised when brew ID is not found."""
    
    def __init__(self, brew_id: str):
        msg = f"Brew with ID '{brew_id}' not found"
        super().__init__(msg, ErrorCategory.BREW)
        self.brew_id = brew_id


class InvalidBrewStateError(PermanentError):
    """Raised when operation is not valid for current brew state."""
    
    def __init__(self, current_state: str, operation: str):
        msg = f"Cannot perform '{operation}' when brew is in state: {current_state}"
        super().__init__(msg, ErrorCategory.BREW)
        self.current_state = current_state
        self.operation = operation


class BrewAbortedError(PermanentError):
    """Raised when a brew is aborted or killed."""
    
    def __init__(self, brew_id: str, reason: str = None):
        msg = f"Brew '{brew_id}' was aborted"
        if reason:
            msg += f": {reason}"
        super().__init__(msg, ErrorCategory.BREW)
        self.brew_id = brew_id
        self.reason = reason


# ==================== Strategy-specific errors ====================

class StrategyError(PermanentError):
    """Raised when strategy execution fails."""
    
    def __init__(self, strategy_name: str, message: str):
        msg = f"Strategy '{strategy_name}' error: {message}"
        super().__init__(msg, ErrorCategory.BREW)
        self.strategy_name = strategy_name


class StrategyCreationError(PermanentError):
    """Raised when strategy cannot be created (invalid params, etc.)."""
    
    def __init__(self, strategy_name: str, reason: str):
        msg = f"Cannot create strategy '{strategy_name}': {reason}"
        super().__init__(msg, ErrorCategory.BREW)
        self.strategy_name = strategy_name
        self.reason = reason


# ==================== Configuration errors ====================

class ConfigurationError(PermanentError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, parameter: str, message: str = None):
        msg = message or f"Invalid configuration for parameter: {parameter}"
        super().__init__(msg, ErrorCategory.CONFIGURATION)
        self.parameter = parameter
