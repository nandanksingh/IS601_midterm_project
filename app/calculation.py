# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/06/2025
# Assignment 5 - Enhanced Calculator
# ----------------------------------------------------------

########################
# Calculation Model    #
########################

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import datetime
import logging
from typing import Any, Dict

# Custom exception from exceptions.py
from app.exceptions import OperationError


@dataclass
class Calculation:
    """
    Represents one single math calculation.

    This class is responsible for:
    - storing the operation type (e.g., Addition)
    - performing the operation automatically when created
    - saving and loading the calculation details
    """

    operation: str            # The math operation (e.g., "Addition", "Division")
    operand1: Decimal         # First number
    operand2: Decimal         # Second number

    # Computed fields
    result: Decimal = field(init=False)  # Automatically calculated
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)  # Current time

    def __post_init__(self):
        """
        Runs right after dataclass is created.
        It automatically performs the calculation.
        """
        self.result = self.calculate()

    # ----------------------------------------------------------
    # Main calculation logic
    # ----------------------------------------------------------
    def calculate(self) -> Decimal:
        """
        Perform the requested math operation.

        Returns:
            Decimal: The computed result.
        Raises:
            OperationError: If operation is invalid or math fails.
        """
        # Dictionary linking operation names to the function to perform
        operations = {
            "Addition": lambda x, y: x + y,
            "Subtraction": lambda x, y: x - y,
            "Multiplication": lambda x, y: x * y,
            "Division": lambda x, y: x / y if y != 0 else self._raise_div_zero(),
            "Power": lambda x, y: Decimal(pow(float(x), float(y))) if y >= 0 else self._raise_neg_power(),
            "Root": lambda x, y: (
                Decimal(pow(float(x), 1 / float(y)))
                if x >= 0 and y != 0
                else self._raise_invalid_root(x, y)
            )
        }

        # Get the function for the selected operation
        op = operations.get(self.operation)
        if not op:
            raise OperationError(f"Unknown operation: {self.operation}")

        try:
            # Extra validation to trigger conversion errors when operands are invalid
            Decimal(self.operand1)
            Decimal(self.operand2)

            # Perform the actual math operation
            return op(self.operand1, self.operand2)

        except (InvalidOperation, ValueError, ArithmeticError) as e:
            # Catch any unexpected calculation error
            raise OperationError(f"Calculation failed: {e}")

    # ----------------------------------------------------------
    # Error helper methods
    # ----------------------------------------------------------
    @staticmethod
    def _raise_div_zero():
        """Raise an error when division by zero is attempted."""
        raise OperationError("Division by zero is not allowed")

    @staticmethod
    def _raise_neg_power():
        """Raise an error when a negative power is used."""
        raise OperationError("Negative exponents are not supported")

    @staticmethod
    def _raise_invalid_root(x: Decimal, y: Decimal):
        """
        Raise errors for invalid root operations.
        Example: root of negative number or 0-degree root.
        """
        if y == 0:
            raise OperationError("Zero root is undefined")
        if x < 0:
            raise OperationError("Cannot calculate root of negative number")
        raise OperationError("Invalid root operation")

    # ----------------------------------------------------------
    # Data serialization (for pandas and CSV history)
    # ----------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the calculation into a dictionary format.

        Used to save calculation details to CSV using pandas.
        """
        return {
            "operation": self.operation,
            "operand1": str(self.operand1),
            "operand2": str(self.operand2),
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Calculation':
        """
        Recreate a Calculation object from a dictionary.

        Used when loading saved history (like CSV or JSON files).
        """
        try:
            calc = Calculation(
                operation=data["operation"],
                operand1=Decimal(data["operand1"]),
                operand2=Decimal(data["operand2"])
            )

            # Keep original timestamp from the saved data
            calc.timestamp = datetime.datetime.fromisoformat(data["timestamp"])

            # Optional: verify that result matches saved one
            saved_result = Decimal(data["result"])
            if calc.result != saved_result:
                logging.warning(
                    f"Loaded result {saved_result} differs from computed result {calc.result}"
                )

            return calc

        except (KeyError, InvalidOperation, ValueError) as e:
            # Handles bad or missing data (covered by tests)
            raise OperationError(f"Invalid calculation data: {str(e)}")

    # ----------------------------------------------------------
    # Utility / Display Methods
    # ----------------------------------------------------------
    def __str__(self) -> str:
        """Readable summary shown to the user."""
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def __repr__(self) -> str:
        """Developer-friendly detailed view for debugging."""
        return (
            f"Calculation(operation='{self.operation}', operand1={self.operand1}, "
            f"operand2={self.operand2}, result={self.result}, "
            f"timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        """Compare two Calculation objects for equality."""
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation
            and self.operand1 == other.operand1
            and self.operand2 == other.operand2
            and self.result == other.result
        )

    def format_result(self, precision: int = 10) -> str:
        """
        Format the result with a set number of decimal places.

        This helps make printed results cleaner in REPL.
        """
        try:
            # Quantize means round to specified decimal places
            return str(self.result.normalize().quantize(
                Decimal('0.' + '0' * precision)
            ).normalize())
        except InvalidOperation:
            # Fallback for rare edge cases
            return str(self.result)
