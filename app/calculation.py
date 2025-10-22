# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project - Enhanced Calculator (Calculation.py)
# ----------------------------------------------------------
# Description:
# Defines the Calculation model used throughout the calculator.
# Handles arithmetic computation, validation, and persistence.
# Includes serialization/deserialization support for pandas CSV history.
# ----------------------------------------------------------

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import datetime
import logging
from typing import Any, Dict

from app.exceptions import OperationError


@dataclass
class Calculation:
    """
    Represents one mathematical calculation.
    Automatically performs the computation on creation,
    and provides methods for serialization via pandas.
    """

    operation: str
    operand1: Decimal
    operand2: Decimal

    result: Decimal = field(init=False)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    # ----------------------------------------------------------
    # Initialization and automatic computation
    # ----------------------------------------------------------
    def __post_init__(self):
        """Run immediately after object creation to compute result."""
        self.result = self.calculate()

    # ----------------------------------------------------------
    # Core arithmetic logic
    # ----------------------------------------------------------
    def calculate(self) -> Decimal:
        """
        Execute the math operation safely.
        Raises OperationError for invalid or failed operations.
        """
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
            ),
        }

        func = operations.get(self.operation)
        if not func:
            raise OperationError(f"Unknown operation: {self.operation}")

        try:
            # Validate conversion to Decimal (ensures numeric input)
            Decimal(self.operand1)
            Decimal(self.operand2)

            return func(self.operand1, self.operand2)

        except (InvalidOperation, ValueError, ArithmeticError) as e:
            raise OperationError(f"Calculation failed: {e}")

    # ----------------------------------------------------------
    # Error helper methods
    # ----------------------------------------------------------
    @staticmethod
    def _raise_div_zero():
        raise OperationError("Division by zero is not allowed")

    @staticmethod
    def _raise_neg_power():
        raise OperationError("Negative exponents are not supported")

    @staticmethod
    def _raise_invalid_root(x: Decimal, y: Decimal):
        if y == 0:
            raise OperationError("Zero root is undefined")
        if x < 0:
            raise OperationError("Cannot calculate root of negative number")
        raise OperationError("Invalid root operation")

    # ----------------------------------------------------------
    # Serialization for pandas CSV history
    # ----------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the calculation into a serializable dictionary.
        Used for saving via pandas to CSV.
        """
        return {
            "operation": self.operation,
            "operand_a": str(self.operand1),
            "operand_b": str(self.operand2),
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Calculation":
        """
        Restore a Calculation object from dictionary data.
        Used during CSV history loading.
        """
        try:
            calc = Calculation(
                operation=data["operation"],
                operand1=Decimal(data.get("operand_a") or data.get("operand1")),
                operand2=Decimal(data.get("operand_b") or data.get("operand2")),
            )

            # Preserve saved timestamp
            if "timestamp" in data:
                calc.timestamp = datetime.datetime.fromisoformat(str(data["timestamp"]))

            # Validate result consistency
            saved_result = Decimal(data.get("result", "0"))
            if calc.result != saved_result:
                logging.warning(
                    f"Loaded result {saved_result} differs from computed result {calc.result}"
                )

            return calc

        except (KeyError, InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid calculation data: {e}")

    # ----------------------------------------------------------
    # Display utilities
    # ----------------------------------------------------------
    def __str__(self) -> str:
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def __repr__(self) -> str:
        return (
            f"Calculation(operation='{self.operation}', "
            f"operand1={self.operand1}, operand2={self.operand2}, "
            f"result={self.result}, timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation
            and self.operand1 == other.operand1
            and self.operand2 == other.operand2
            and self.result == other.result
        )

    # ----------------------------------------------------------
    # Formatting helper
    # ----------------------------------------------------------
    def format_result(self, precision: int = 10) -> str:
        """
        Return a clean, rounded string version of the result.
        Used for REPL display.
        """
        try:
            return str(
                self.result.normalize().quantize(
                    Decimal("0." + "0" * precision)
                ).normalize()
            )
        except InvalidOperation:
            return str(self.result)
