# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# File: app/operations.py
# ----------------------------------------------------------
# Description:
# Defines all arithmetic operation classes used by the Enhanced Calculator.
# Implements the Factory Design Pattern via @register_operation for modular
# and extensible operation management.
# ----------------------------------------------------------

import math
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Callable, Dict, Type
from app.exceptions import ValidationError

# ----------------------------------------------------------
# Operation Registry (Global)
# ----------------------------------------------------------
_operation_registry: Dict[str, Type["Operation"]] = {}


def register_operation(name: str) -> Callable:
    """
    Decorator for registering operations dynamically.
    Example:
        @register_operation("add")
        class Add(Operation): ...
    """
    def decorator(cls: Type["Operation"]) -> Type["Operation"]:
        _operation_registry[name.lower()] = cls
        return cls
    return decorator


# ----------------------------------------------------------
# Abstract Base Class
# ----------------------------------------------------------
class Operation(ABC):
    """Abstract base class for all operations."""

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Perform the operation."""
        pass  # pragma: no cover

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Optional operand validation for specific rules."""
        pass

    def __str__(self) -> str:
        """Return human-readable name of the operation class."""
        return self.__class__.__name__


# ----------------------------------------------------------
# Basic Arithmetic Operations
# ----------------------------------------------------------
@register_operation("add")
class Add(Operation):
    """Adds two numbers."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a + b


@register_operation("subtract")
class Subtract(Operation):
    """Subtracts the second number from the first."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a - b


@register_operation("multiply")
class Multiply(Operation):
    """Multiplies two numbers."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a * b


@register_operation("divide")
class Divide(Operation):
    """Divides one number by another."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Division by zero is not allowed.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a / b


# ----------------------------------------------------------
# Advanced Arithmetic Operations
# ----------------------------------------------------------
@register_operation("power")
class Power(Operation):
    """Raises one number to the power of another."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        try:
            return Decimal(pow(float(a), float(b)))
        except OverflowError:
            raise ValidationError("Power result too large.")


@register_operation("root")
class Root(Operation):
    """Calculates the nth root of a number."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Zero root is undefined.")
        if a < 0 and int(b) % 2 == 0:
            raise ValidationError("Cannot calculate even root of a negative number.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1 / float(b)))


@register_operation("modulus")
class Modulus(Operation):
    """Computes remainder of division (a % b)."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Cannot perform modulus with divisor 0.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a % b


@register_operation("int_divide")
class IntDivide(Operation):
    """Performs integer (floor) division."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Cannot perform integer division by zero.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(math.floor(a / b))


@register_operation("percent")
class Percent(Operation):
    """Calculates (a / b) * 100."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Cannot calculate percentage with divisor 0.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return (a / b) * 100


@register_operation("abs_diff")
class AbsDiff(Operation):
    """Returns the absolute difference |a - b|."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return abs(a - b)


# ----------------------------------------------------------
# Factory for Dynamic Operation Creation
# ----------------------------------------------------------
class OperationFactory:
    """Factory class to create operation instances dynamically."""

    @staticmethod
    def create_operation(name: str) -> Operation:
        """Return a registered operation instance by name."""
        name = name.lower().strip()
        if name in _operation_registry:
            return _operation_registry[name]()
        raise ValueError(f"Unknown operation: {name}")

    @staticmethod
    def list_operations() -> Dict[str, Type[Operation]]:
        """Return dictionary of all registered operations."""
        return dict(_operation_registry)
