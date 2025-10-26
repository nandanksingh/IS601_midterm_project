# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/19/2025
# Midterm Project - Enhanced Calculator 
# File: app/input_validators.py
# ----------------------------------------------------------
# Description:
# Provides robust validation and sanitization for all numeric
# inputs used in the Enhanced Calculator. Ensures:
#   • Inputs are not None or empty
#   • Inputs are convertible to Decimal
#   • Values respect configured max limits
# Raises ValidationError for any invalid input.
# ----------------------------------------------------------

from decimal import Decimal, InvalidOperation
from typing import Any
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

# ----------------------------------------------------------
# Function: ensure_number
# ----------------------------------------------------------
def ensure_number(value: Any) -> Decimal:
    """
    Validate that the given input is a valid numeric value.
    Raises ValidationError for None, empty, or invalid numbers.
    """
    if value is None:
        raise ValidationError("Input cannot be None. Please enter a valid number.")

    if isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValidationError("Input cannot be empty or whitespace.")

    try:
        number = Decimal(str(value)).normalize()
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(
            f"Invalid number format: {value}. Please enter a valid numeric value."
        )
    return number


# ----------------------------------------------------------
# Function: ensure_within_range
# ----------------------------------------------------------
def ensure_within_range(number: Decimal, config: CalculatorConfig) -> Decimal:
    """
    Ensure the number is within the allowed range from CalculatorConfig.
    Raises ValidationError if the number exceeds configured limit.
    """
    if abs(number) > config.max_input_value:
        raise ValidationError(
            f"Value {number} exceeds the maximum allowed limit "
            f"({config.max_input_value})."
        )
    return number


# ----------------------------------------------------------
# Function: validate_input
# ----------------------------------------------------------
def validate_input(value: Any, config: CalculatorConfig) -> Decimal:
    """
    Combined validator that:
      1. Ensures input is numeric
      2. Ensures input is within configured range
    """
    number = ensure_number(value)
    return ensure_within_range(number, config)
