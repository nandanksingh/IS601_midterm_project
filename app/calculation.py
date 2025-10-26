# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/19/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# File: app/calculation.py
# ----------------------------------------------------------
# Description:
# Defines the Calculation dataclass and CalculationFactory
# for executing and recording arithmetic operations.
#
# Each Calculation object:
#   - Stores operands (a, b), operation name, computed result, and timestamp.
#   - Supports serialization to/from dictionaries for persistence.
#   - Integrates with the History and Memento modules.
# ----------------------------------------------------------

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, Callable
import logging

from app.exceptions import OperationError


# ==========================================================
# Dataclass: Calculation
# ==========================================================
@dataclass
class Calculation:
    """Represents a single arithmetic calculation record."""

    operation: str
    a: Decimal
    b: Decimal
    result: Decimal = field(init=False)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Compute result automatically once created."""
        self.result = self.perform_operation()

    def perform_operation(self) -> Decimal:
        """Safely execute the registered operation."""
        try:
            x, y = Decimal(self.a), Decimal(self.b)
        except (InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid operands: {e}")

        func = CalculationFactory.operations.get(self.operation.lower())
        if not func:
            raise OperationError(f"Unknown operation: {self.operation}")

        try:
            return func(x, y)
        except (ArithmeticError, InvalidOperation, ValueError) as e:
            msg = f"Calculation failed: {e}"
            logging.error(msg)
            raise OperationError(msg)

    def to_dict(self) -> Dict[str, str]:
        """Convert the Calculation to a serializable dictionary."""
        return {
            "operation": self.operation,
            "a": str(self.a),
            "b": str(self.b),
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, str]) -> "Calculation":
        """Rebuild a Calculation object from its dictionary form."""
        try:
            a_key = "a" if "a" in data else "operand1"
            b_key = "b" if "b" in data else "operand2"

            calc = Calculation(
                operation=data["operation"],
                a=Decimal(data[a_key]),
                b=Decimal(data[b_key]),
            )

            if "timestamp" in data:
                calc.timestamp = datetime.fromisoformat(str(data["timestamp"]))

            saved_result = Decimal(str(data.get("result", "0")))
            if calc.result != saved_result:
                logging.warning(
                    f"Loaded result {saved_result} differs from computed result {calc.result}"
                )

            return calc

        except (KeyError, InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid calculation data: {e}")

    def format_result(self, precision: int = 3) -> str:
        """Return result formatted to given precision."""
        try:
            q = Decimal("0." + "0" * precision)
            return str(self.result.quantize(q).normalize())
        except InvalidOperation:
            return str(self.result)

    def __str__(self):
        return f"{self.operation}({self.a}, {self.b}) = {self.result}"

    def __repr__(self):
        return (
            f"Calculation(operation='{self.operation}', a={self.a}, b={self.b}, "
            f"result={self.result}, timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation
            and self.a == other.a
            and self.b == other.b
            and self.result == other.result
        )


# ==========================================================
# Factory Pattern: CalculationFactory
# ==========================================================
class CalculationFactory:
    """Factory registry for all supported operations."""

    operations: Dict[str, Callable[[Decimal, Decimal], Decimal]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register an operation function."""
        def decorator(func: Callable[[Decimal, Decimal], Decimal]):
            cls.operations[name.lower()] = func
            return func
        return decorator


# ----------------------------------------------------------
# Register Built-In Arithmetic Operations
# ----------------------------------------------------------
@CalculationFactory.register("add")
def _add(x, y): return x + y

@CalculationFactory.register("subtract")
def _subtract(x, y): return x - y

@CalculationFactory.register("multiply")
def _multiply(x, y): return x * y

@CalculationFactory.register("divide")
def _divide(x, y):
    if y == 0:
        raise OperationError("Division by zero is not allowed")
    return x / y

@CalculationFactory.register("modulus")
def _modulus(x, y):
    if y == 0:
        raise OperationError("Division by zero is not allowed")
    return x % y

@CalculationFactory.register("int_divide")
def _int_divide(x, y):
    if y == 0:
        raise OperationError("Division by zero is not allowed")
    return x // y

@CalculationFactory.register("power")
def _power(x, y): return x ** y

@CalculationFactory.register("root")
def _root(x, y):
    if y == 0:
        raise OperationError("Zero root is undefined")
    if x < 0:
        raise OperationError("Cannot calculate root of negative number")
    return Decimal(pow(float(x), 1 / float(y)))

@CalculationFactory.register("percent")
def _percent(x, y):
    if y == 0:
        raise OperationError("Division by zero is not allowed")
    return (x / y) * 100

@CalculationFactory.register("abs_diff")
def _abs_diff(x, y): return abs(x - y)
