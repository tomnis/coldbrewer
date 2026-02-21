"""
Unit tests for custom exception classes.
Tests the exception hierarchy and error handling utilities.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest

# Add src to path so we can import brewserver
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brewserver.exceptions import (
    TransientError,
    PermanentError,
    ScaleNotFoundError,
    ScaleConnectionError,
    ScaleReadError,
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
    StrategyCreationError,
    ConfigurationError,
)
from brewserver.model import ErrorSeverity, ErrorCategory
from brewserver.error_handling import (
    handle_exception,
    handle_scale_error,
    handle_valve_error,
    handle_brew_error,
    handle_timeseries_error,
    handle_configuration_error,
    create_error_response,
)


class TestErrorEnums:
    """Tests for error severity and category enums."""

    def test_error_severity_values(self):
        """Test ErrorSeverity enum values."""
        assert ErrorSeverity.INFO.value == "info"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.CRITICAL.value == "critical"

    def test_error_category_values(self):
        """Test ErrorCategory enum values."""
        assert ErrorCategory.SCALE.value == "scale"
        assert ErrorCategory.VALVE.value == "valve"
        assert ErrorCategory.TIMESERIES.value == "timeseries"
        assert ErrorCategory.BREW.value == "brew"
        assert ErrorCategory.NETWORK.value == "network"
        assert ErrorCategory.HARDWARE.value == "hardware"
        assert ErrorCategory.CONFIGURATION.value == "configuration"


class TestTransientError:
    """Tests for TransientError base class."""

    def test_transient_error_defaults(self):
        """Test TransientError default values."""
        err = TransientError("test error")
        assert err.message == "test error"
        assert err.retry_after == 1.0
        assert err.max_retries == 3
        assert err.retry_count == 0
        assert err.category == ErrorCategory.BREW

    def test_transient_error_custom_values(self):
        """Test TransientError with custom values."""
        err = TransientError("test", retry_after=5.0, max_retries=10, category=ErrorCategory.SCALE)
        assert err.retry_after == 5.0
        assert err.max_retries == 10
        assert err.category == ErrorCategory.SCALE

    def test_transient_error_retry_count(self):
        """Test retry count increment."""
        err = TransientError("test")
        err.retry_count += 1
        assert err.retry_count == 1


class TestPermanentError:
    """Tests for PermanentError base class."""

    def test_permanent_error_defaults(self):
        """Test PermanentError default values."""
        err = PermanentError("test error")
        assert err.message == "test error"
        assert err.category == ErrorCategory.BREW

    def test_permanent_error_custom_category(self):
        """Test PermanentError with custom category."""
        err = PermanentError("test", ErrorCategory.SCALE)
        assert err.category == ErrorCategory.SCALE


class TestScaleExceptions:
    """Tests for scale-related exceptions."""

    def test_scale_not_found_error(self):
        """Test ScaleNotFoundError."""
        err = ScaleNotFoundError("AA:BB:CC:DD:EE:FF")
        assert "AA:BB:CC:DD:EE:FF" in str(err)
        assert err.category == ErrorCategory.SCALE
        assert isinstance(err, PermanentError)

    def test_scale_connection_error_is_transient(self):
        """Test ScaleConnectionError is transient."""
        err = ScaleConnectionError()
        assert isinstance(err, TransientError)
        assert err.retry_after == 2.0
        assert err.category == ErrorCategory.SCALE

    def test_scale_connection_error_with_mac(self):
        """Test ScaleConnectionError with MAC address."""
        err = ScaleConnectionError(mac_address="AA:BB:CC:DD:EE:FF")
        assert err.mac_address == "AA:BB:CC:DD:EE:FF"

    def test_scale_read_error_is_transient(self):
        """Test ScaleReadError is transient."""
        err = ScaleReadError()
        assert isinstance(err, TransientError)
        assert err.retry_after == 1.0
        assert err.category == ErrorCategory.SCALE

    def test_scale_battery_low_error(self):
        """Test ScaleBatteryLowError."""
        err = ScaleBatteryLowError(15)
        assert "15" in str(err)
        assert err.battery_percentage == 15
        assert err.category == ErrorCategory.SCALE


class TestValveExceptions:
    """Tests for valve-related exceptions."""

    def test_valve_operation_error_is_permanent(self):
        """Test ValveOperationError is permanent."""
        err = ValveOperationError("step_forward")
        assert isinstance(err, PermanentError)
        assert err.operation == "step_forward"
        assert err.category == ErrorCategory.VALVE

    def test_valve_operation_error_custom_message(self):
        """Test ValveOperationError with custom message."""
        err = ValveOperationError("step_forward", "Motor stalled")
        assert "Motor stalled" in str(err)

    def test_valve_timeout_error_is_transient(self):
        """Test ValveTimeoutError is transient."""
        err = ValveTimeoutError("return_to_start", 10.0)
        assert isinstance(err, TransientError)
        assert err.operation == "return_to_start"
        assert err.timeout == 10.0
        assert err.category == ErrorCategory.VALVE

    def test_valve_not_acquired_error(self):
        """Test ValveNotAcquiredError."""
        err = ValveNotAcquiredError("step_forward")
        assert isinstance(err, PermanentError)
        assert err.operation == "step_forward"


class TestTimeSeriesExceptions:
    """Tests for time series exceptions."""

    def test_time_series_connection_error_is_transient(self):
        """Test TimeSeriesConnectionError is transient."""
        err = TimeSeriesConnectionError()
        assert isinstance(err, TransientError)
        assert err.retry_after == 5.0
        assert err.category == ErrorCategory.TIMESERIES

    def test_time_series_write_error_is_transient(self):
        """Test TimeSeriesWriteError is transient."""
        err = TimeSeriesWriteError()
        assert isinstance(err, TransientError)
        assert err.retry_after == 2.0
        assert err.category == ErrorCategory.TIMESERIES


class TestBrewExceptions:
    """Tests for brew-related exceptions."""

    def test_brew_conflict_error(self):
        """Test BrewConflictError."""
        err = BrewConflictError("brew-123")
        assert "brew-123" in str(err)
        assert err.current_brew_id == "brew-123"
        assert err.category == ErrorCategory.BREW

    def test_brew_not_found_error(self):
        """Test BrewNotFoundError."""
        err = BrewNotFoundError("brew-456")
        assert "brew-456" in str(err)
        assert err.brew_id == "brew-456"

    def test_invalid_brew_state_error(self):
        """Test InvalidBrewStateError."""
        err = InvalidBrewStateError("brewing", "pause")
        assert "brewing" in str(err)
        assert "pause" in str(err)
        assert err.current_state == "brewing"
        assert err.operation == "pause"

    def test_brew_aborted_error(self):
        """Test BrewAbortedError."""
        err = BrewAbortedError("brew-789", "user cancelled")
        assert "brew-789" in str(err)
        assert "user cancelled" in str(err)
        assert err.brew_id == "brew-789"
        assert err.reason == "user cancelled"


class TestStrategyExceptions:
    """Tests for strategy-related exceptions."""

    def test_strategy_error(self):
        """Test StrategyError."""
        err = StrategyError("PID", "Invalid gain values")
        assert "PID" in str(err)
        assert err.strategy_name == "PID"
        assert err.category == ErrorCategory.BREW

    def test_strategy_creation_error(self):
        """Test StrategyCreationError."""
        err = StrategyCreationError("MPC", "Missing required parameter")
        assert "MPC" in str(err)
        assert err.strategy_name == "MPC"
        assert err.reason == "Missing required parameter"


class TestConfigurationError:
    """Tests for configuration exceptions."""

    def test_configuration_error(self):
        """Test ConfigurationError."""
        err = ConfigurationError("COLDBREW_TARGET_FLOW_RATE")
        assert "COLDBREW_TARGET_FLOW_RATE" in str(err)
        assert err.parameter == "COLDBREW_TARGET_FLOW_RATE"
        assert err.category == ErrorCategory.CONFIGURATION

    def test_configuration_error_custom_message(self):
        """Test ConfigurationError with custom message."""
        err = ConfigurationError("param", "must be positive")
        assert "must be positive" in str(err)


class TestHandleScaleError:
    """Tests for scale error handler."""

    def test_handle_scale_not_found_error(self):
        """Test handling ScaleNotFoundError."""
        error = ScaleNotFoundError("AA:BB:CC:DD:EE:FF")
        result = handle_scale_error(error)
        
        assert result["error"] == "Scale not found"
        assert result["category"] == "scale"
        assert result["retryable"] is False
        assert "recovery_suggestion" in result

    def test_handle_scale_connection_error(self):
        """Test handling ScaleConnectionError."""
        error = ScaleConnectionError()
        result = handle_scale_error(error)
        
        assert result["error"] == "Scale connection failed"
        assert result["category"] == "scale"
        assert result["retryable"] is True

    def test_handle_scale_read_error(self):
        """Test handling ScaleReadError."""
        error = ScaleReadError()
        result = handle_scale_error(error)
        
        assert result["error"] == "Failed to read from scale"
        assert result["retryable"] is True

    def test_handle_scale_battery_low_error(self):
        """Test handling ScaleBatteryLowError."""
        error = ScaleBatteryLowError(10)
        result = handle_scale_error(error)
        
        assert result["error"] == "Scale battery is low"
        assert result["severity"] == "warning"


class TestHandleValveError:
    """Tests for valve error handler."""

    def test_handle_valve_operation_error(self):
        """Test handling ValveOperationError."""
        error = ValveOperationError("step_forward")
        result = handle_valve_error(error)
        
        assert "Valve operation failed" in result["error"]
        assert result["category"] == "valve"
        assert result["retryable"] is False

    def test_handle_valve_timeout_error(self):
        """Test handling ValveTimeoutError."""
        error = ValveTimeoutError("return_to_start")
        result = handle_valve_error(error)
        
        assert "timed out" in result["error"]
        assert result["retryable"] is True


class TestHandleBrewError:
    """Tests for brew error handler."""

    def test_handle_brew_conflict_error(self):
        """Test handling BrewConflictError."""
        error = BrewConflictError("brew-123")
        result = handle_brew_error(error)
        
        assert "already in progress" in result["error"]
        assert result["severity"] == "warning"
        assert result["retryable"] is False

    def test_handle_brew_not_found_error(self):
        """Test handling BrewNotFoundError."""
        error = BrewNotFoundError("brew-456")
        result = handle_brew_error(error)
        
        assert "not found" in result["error"]
        assert result["retryable"] is False

    def test_handle_invalid_brew_state_error(self):
        """Test handling InvalidBrewStateError."""
        error = InvalidBrewStateError("brewing", "start")
        result = handle_brew_error(error)
        
        assert "Invalid operation" in result["error"]
        assert result["severity"] == "warning"


class TestHandleException:
    """Tests for main handle_exception function."""

    def test_handle_scale_exception(self):
        """Test handling scale exceptions."""
        error = ScaleConnectionError()
        result = handle_exception(error)
        
        assert result["category"] == "scale"
        assert result["retryable"] is True

    def test_handle_valve_exception(self):
        """Test handling valve exceptions."""
        error = ValveOperationError("step")
        result = handle_exception(error)
        
        assert result["category"] == "valve"

    def test_handle_timeseries_exception(self):
        """Test handling timeseries exceptions."""
        error = TimeSeriesConnectionError()
        result = handle_exception(error)
        
        assert result["category"] == "timeseries"

    def test_handle_generic_exception(self):
        """Test handling generic exceptions."""
        error = ValueError("some error")
        result = handle_exception(error)
        
        assert result["category"] == "brew"
        assert result["retryable"] is False
        assert result["exception_type"] == "ValueError"


class TestCreateErrorResponse:
    """Tests for create_error_response function."""

    def test_create_error_response_basic(self):
        """Test basic error response creation."""
        result = create_error_response(
            message="Test error",
            category=ErrorCategory.BREW,
            severity=ErrorSeverity.ERROR,
            retryable=False,
        )
        
        assert result["error"] == "Test error"
        assert result["category"] == "brew"
        assert result["severity"] == "error"
        assert result["retryable"] is False
        assert "timestamp" in result

    def test_create_error_response_with_brew_id(self):
        """Test error response with brew ID."""
        result = create_error_response(
            message="Test error",
            category=ErrorCategory.BREW,
            severity=ErrorSeverity.ERROR,
            retryable=True,
            brew_id="brew-123",
        )
        
        assert result["brew_id"] == "brew-123"

    def test_create_error_response_with_suggestion(self):
        """Test error response with recovery suggestion."""
        result = create_error_response(
            message="Test error",
            category=ErrorCategory.BREW,
            severity=ErrorSeverity.ERROR,
            retryable=True,
            suggestion="Try again later",
        )
        
        assert result["recovery_suggestion"] == "Try again later"
