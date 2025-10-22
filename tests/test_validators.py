# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project - Enhanced Calculator (Unit Tests)
# ----------------------------------------------------------
# Description:
# Unit tests for InputValidator to ensure:
#   - Valid numeric inputs are accepted
#   - Invalid, empty, or out-of-range inputs raise ValidationError
# ----------------------------------------------------------

import pytest
from decimal import Decimal
from app.input_validators import InputValidator
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

config = CalculatorConfig()


# ----------------------------------------------------------
# Valid input tests
# ----------------------------------------------------------
def test_valid_integer():
    """Validate integer input."""
    assert InputValidator.validate_number(10, config) == Decimal("10")


def test_valid_decimal_string():
    """Validate decimal string input."""
    assert InputValidator.validate_number("3.14", config) == Decimal("3.14")


# ----------------------------------------------------------
# Invalid input tests
# ----------------------------------------------------------
def test_empty_string_raises():
    """Empty or whitespace-only string should raise ValidationError."""
    with pytest.raises(ValidationError, match="empty"):
        InputValidator.validate_number("   ", config)


def test_none_raises():
    """None input should raise ValidationError."""
    with pytest.raises(ValidationError, match="None"):
        InputValidator.validate_number(None, config)


def test_exceeds_max_value():
    """Value exceeding config.max_input_value should raise ValidationError."""
    config.max_input_value = Decimal("1000")
    with pytest.raises(ValidationError, match="exceeds"):
        InputValidator.validate_number("2000", config)


def test_invalid_non_numeric_type():
    """Non-numeric input should raise ValidationError."""
    with pytest.raises(ValidationError, match="Invalid number format"):
        InputValidator.validate_number("abc", config)
