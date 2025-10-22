# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project - Enhanced Calculator (Input Validation)
# ----------------------------------------------------------
# Description:
# This provides a robust input validation mechanism
# for the Enhanced Calculator application.
# It ensures all user inputs are:
#   - Numerically valid (convertible to Decimal)
#   - Within configured limits (from CalculatorConfig)
#   - Clean and non-empty (no None or whitespace-only inputs)
#
# The validated and normalized Decimal values are then used
# safely across calculator operations, minimizing runtime errors.
# ----------------------------------------------------------

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError


# ==========================================================
# InputValidator Class Definition
# ==========================================================
@dataclass
class InputValidator:
    """
    Validates and sanitizes calculator inputs before computation.

    Responsibilities:
    -----------------
    - Check if the input is not None or empty
    - Convert valid input to a Decimal type for precision arithmetic
    - Enforce maximum absolute value limits using CalculatorConfig
    - Raise descriptive ValidationError messages for invalid cases
    """

    # ----------------------------------------------------------
    # Static Method: validate_number()
    # ----------------------------------------------------------
    @staticmethod
    def validate_number(value: Optional[Any], config: CalculatorConfig) -> Decimal:
        """
        Validate and convert the input value to a normalized Decimal.

        Args:
            value (Any): The input value to validate (can be str, int, float, Decimal)
            config (CalculatorConfig): The global calculator configuration
                                       used to enforce max input constraints.

        Returns:
            Decimal: The validated and normalized number ready for computation.

        Raises:
            ValidationError: If the input is invalid, empty, non-numeric,
                             or exceeds configured maximum value limits.
        """

        try:
            # ------------------------------------------------------
            # STEP 1: Check for None or blank string input
            # ------------------------------------------------------
            if value is None:
                raise ValidationError("Input cannot be None. Please enter a valid number.")

            if isinstance(value, str):
                value = value.strip()
                if not value:
                    raise ValidationError("Input cannot be empty or whitespace.")

            # ------------------------------------------------------
            # STEP 2: Attempt safe Decimal conversion
            # ------------------------------------------------------
            number = Decimal(str(value))

            # ------------------------------------------------------
            # STEP 3: Enforce configured maximum absolute value
            # ------------------------------------------------------
            if abs(number) > config.max_input_value:
                raise ValidationError(
                    f"Value {number} exceeds the maximum allowed limit "
                    f"({config.max_input_value})."
                )

            # ------------------------------------------------------
            # STEP 4: Return normalized decimal value
            # ------------------------------------------------------
            return number.normalize()

        except (InvalidOperation, TypeError, ValueError) as e:
            # ------------------------------------------------------
            # STEP 5: Handle invalid numeric formats gracefully
            # ------------------------------------------------------
            raise ValidationError(
                f"Invalid number format: {value}. Please enter a valid numeric value."
            ) from e
