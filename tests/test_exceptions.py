# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# File: tests/test_exceptions.py
# ----------------------------------------------------------
# Description:
# Unit tests verifying the behavior of custom calculator exceptions.
# Ensures correct inheritance, meaningful messages, and reliable error handling.
# ----------------------------------------------------------

import pytest
from app.exceptions import (
    CalculatorError,
    ValidationError,
    OperationError,
    ConfigError,
    HistoryError,
)

# ----------------------------------------------------------
# Base Class Tests
# ----------------------------------------------------------

def test_calculator_error_is_base_exception():
    """Ensure CalculatorError serves as the root of all custom exceptions."""
    with pytest.raises(CalculatorError) as exc_info:
        raise CalculatorError("Base calculator error occurred")
    assert str(exc_info.value) == "Base calculator error occurred"


def test_all_exceptions_inherit_from_calculator_error():
    """Ensure all defined exceptions inherit from CalculatorError."""
    for exc in [ValidationError, OperationError, ConfigError, HistoryError]:
        assert issubclass(exc, CalculatorError)

# ----------------------------------------------------------
# ValidationError Tests
# ----------------------------------------------------------

def test_validation_error_is_calculator_error():
    """ValidationError should inherit from CalculatorError."""
    with pytest.raises(CalculatorError) as exc_info:
        raise ValidationError("Validation failed")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "Validation failed"


def test_validation_error_default_message():
    """Check the default message for ValidationError."""
    err = ValidationError()
    assert "Invalid input" in str(err)

# ----------------------------------------------------------
# OperationError Tests
# ----------------------------------------------------------

def test_operation_error_is_calculator_error():
    """OperationError should inherit from CalculatorError."""
    with pytest.raises(CalculatorError) as exc_info:
        raise OperationError("Operation failed")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "Operation failed"


def test_operation_error_default_message():
    """Check the default message for OperationError."""
    err = OperationError()
    assert "Operation failed" in str(err)

# ----------------------------------------------------------
# ConfigError Tests
# ----------------------------------------------------------

def test_config_error_is_calculator_error():
    """ConfigError should inherit from CalculatorError."""
    with pytest.raises(CalculatorError) as exc_info:
        raise ConfigError("Configuration invalid")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "Configuration invalid"


def test_config_error_default_message():
    """Check the default message for ConfigError."""
    err = ConfigError()
    assert "Configuration" in str(err)

# ----------------------------------------------------------
# HistoryError Tests
# ----------------------------------------------------------

def test_history_error_is_calculator_error():
    """HistoryError should inherit from CalculatorError."""
    with pytest.raises(CalculatorError) as exc_info:
        raise HistoryError("History operation failed")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "History operation failed"


def test_history_error_default_message():
    """Check the default message for HistoryError."""
    err = HistoryError()
    assert "History" in str(err)
