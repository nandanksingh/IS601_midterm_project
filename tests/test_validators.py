# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/19/2025
# Midterm Project - Enhanced Calculator
# File: tests/test_validators.py
# ----------------------------------------------------------
# Description:
# Pytest suite for input validation helper functions.
# Ensures correct behavior for numeric, invalid, and edge cases.
# ----------------------------------------------------------

import pytest
from decimal import Decimal
from app.input_validators import (
    ensure_number,
    ensure_within_range,
    validate_input
)
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

# Shared configuration fixture
config = CalculatorConfig()

# ----------------------------------------------------------
# VALID INPUT TESTS
# ----------------------------------------------------------

def test_valid_integer_input():
    """Integer values should pass validation and convert to Decimal."""
    result = ensure_number(10)
    assert result == Decimal("10")


def test_valid_decimal_string_input():
    """String-based decimals should be converted to Decimal."""
    result = ensure_number("3.14")
    assert result == Decimal("3.14")


def test_valid_negative_number():
    """Negative values within limit should be accepted."""
    number = ensure_number("-99.99")
    validated = ensure_within_range(number, config)
    assert validated == Decimal("-99.99")

# ----------------------------------------------------------
# INVALID INPUT TESTS
# ----------------------------------------------------------

def test_none_input_raises_validationerror():
    """None input should raise ValidationError."""
    with pytest.raises(ValidationError, match="None"):
        ensure_number(None)


def test_empty_string_raises_validationerror():
    """Empty or whitespace-only string should raise ValidationError."""
    with pytest.raises(ValidationError, match="empty"):
        ensure_number("   ")


def test_non_numeric_string_raises_error():
    """Non-numeric input should raise ValidationError."""
    with pytest.raises(ValidationError, match="Invalid number format"):
        ensure_number("abc")


def test_invalid_type_list_raises_error():
    """Invalid types (like list) should raise ValidationError."""
    with pytest.raises(ValidationError, match="Invalid number format"):
        ensure_number([1, 2, 3])


def test_exceeding_max_limit_raises_error():
    """Numbers beyond config.max_input_value should raise ValidationError."""
    config.max_input_value = Decimal("1000")
    with pytest.raises(ValidationError, match="exceeds"):
        ensure_within_range(Decimal("5000"), config)

# ----------------------------------------------------------
# COMBINED VALIDATION TEST
# ----------------------------------------------------------

def test_validate_input_combines_number_and_range():
    """Combined helper should validate number and enforce range."""
    config.max_input_value = Decimal("100")
    result = validate_input("50", config)
    assert result == Decimal("50")


def test_validate_input_exceeds_combined_range_raises():
    """Combined helper should raise when exceeding range."""
    config.max_input_value = Decimal("10")
    with pytest.raises(ValidationError, match="exceeds"):
        validate_input("1000", config)

# ----------------------------------------------------------
# NORMALIZATION TEST
# ----------------------------------------------------------

def test_decimal_is_normalized():
    """Ensure trailing zeros are removed when normalized."""
    result = ensure_number("10.000")
    assert result == Decimal("10")
