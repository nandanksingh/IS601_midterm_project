# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project: Enhanced Calculator Command-Line Application
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
    ConfigurationError,
)

# ----------------------------------------------------------
# Base Class Tests
# ----------------------------------------------------------

def test_calculator_error_is_base_exception():
    """Ensure CalculatorError serves as the root of all custom exceptions."""
    with pytest.raises(CalculatorError) as exc_info:
        raise CalculatorError("Base calculator error occurred")
    assert str(exc_info.value) == "Base calculator error occurred"

# ----------------------------------------------------------
# ValidationError Tests
# ----------------------------------------------------------

def test_validation_error_is_calculator_error():
    """ValidationError should inherit from CalculatorError."""
    with pytest.raises(CalculatorError) as exc_info:
        raise ValidationError("Validation failed")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "Validation failed"

def test_validation_error_specific_exception():
    """Ensure ValidationError behaves as expected."""
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("Validation error")
    assert str(exc_info.value) == "Validation error"

# ----------------------------------------------------------
# OperationError Tests
# ----------------------------------------------------------

def test_operation_error_is_calculator_error():
    """OperationError should inherit from CalculatorError."""
    with pytest.raises(CalculatorError) as exc_info:
        raise OperationError("Operation failed")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "Operation failed"

def test_operation_error_specific_exception():
    """Ensure OperationError behaves as expected."""
    with pytest.raises(OperationError) as exc_info:
        raise OperationError("Specific operation error")
    assert str(exc_info.value) == "Specific operation error"

# ----------------------------------------------------------
# ConfigurationError Tests
# ----------------------------------------------------------

def test_configuration_error_is_calculator_error():
    """ConfigurationError should inherit from CalculatorError."""
    with pytest.raises(CalculatorError) as exc_info:
        raise ConfigurationError("Configuration invalid")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "Configuration invalid"

def test_configuration_error_specific_exception():
    """Ensure ConfigurationError behaves as expected."""
    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError("Specific configuration error")
    assert str(exc_info.value) == "Specific configuration error"
