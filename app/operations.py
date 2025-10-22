# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# ----------------------------------------------------------
# Description:
# This module implements all arithmetic operation classes used in the
# Enhanced Calculator application. It follows the Factory Design Pattern
# to dynamically create operation objects. Each operation is implemented
# ----------------------------------------------------------

import math
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Type
from app.exceptions import ValidationError


# ----------------------------------------------------------
# Base Abstract Class for All Operations
# ----------------------------------------------------------
class Operation(ABC):
    """
    Abstract base class defining the interface for all arithmetic operations.
    Each subclass must implement the execute() method.
    """

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Perform the arithmetic operation."""
        pass  # pragma: no cover

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Optional operand validation; overridden in subclasses if needed."""
        pass

    def __str__(self) -> str:
        """Return the operation name (used for logging and display)."""
        return self.__class__.__name__


# ----------------------------------------------------------
# Basic Arithmetic Operations
# ----------------------------------------------------------
class Addition(Operation):
    """Adds two numbers."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a + b


class Subtraction(Operation):
    """Subtracts the second number from the first."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a - b


class Multiplication(Operation):
    """Multiplies two numbers."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a * b


class Division(Operation):
    """Performs division of one number by another with zero-check."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Division by zero is not allowed.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a / b


# ----------------------------------------------------------
# Advanced Arithmetic Operations (Midterm Additions)
# ----------------------------------------------------------
class Power(Operation):
    """Raises one number to the power of another."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        # Using float for compatibility with fractional powers
        return Decimal(pow(float(a), float(b)))


class Root(Operation):
    """Calculates the nth root of a number."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Zero root is undefined.")
        if a < 0 and b % 2 == 0:
            raise ValidationError("Cannot calculate even root of a negative number.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        # nth root = a ** (1/n)
        return Decimal(pow(float(a), 1 / float(b)))


class Modulus(Operation):
    """Computes the remainder of division (a % b)."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Cannot perform modulus with divisor 0.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a % b


class IntegerDivision(Operation):
    """Performs integer (floor) division with correct handling for negatives."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Cannot perform integer division by zero.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        try:
            self.validate_operands(a, b)
            result = math.floor(float(a) / float(b))
            return Decimal(result)
        except Exception as e:
            raise ValidationError(f"Integer division failed: {e}")


class Percentage(Operation):
    """Calculates the percentage of a with respect to b."""
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Cannot calculate percentage with divisor 0.")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        # Formula: (a / b) * 100
        return (a / b) * 100


class AbsoluteDifference(Operation):
    """Calculates the absolute difference between two numbers."""
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return abs(a - b)


# ----------------------------------------------------------
# Factory Pattern for Dynamic Operation Creation
# ----------------------------------------------------------
class OperationFactory:
    """
    Implements the Factory Design Pattern.
    Provides a centralized mechanism to create operation instances dynamically.
    """

    # Mapping of operation names to their implementing classes
    _operations: Dict[str, Type[Operation]] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'power': Power,
        'root': Root,
        'modulus': Modulus,
        'int_divide': IntegerDivision,
        'percent': Percentage,
        'percentage': Percentage,
        'abs_diff': AbsoluteDifference,
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: Type[Operation]) -> None:
        """
        Register a new operation dynamically at runtime.
        Useful for adding future extensions (e.g., logarithm, sine, cosine).
        """
        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation.")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """
        Create and return an operation instance based on its name.
        This method is tolerant to both:
            - factory keys (e.g., 'percent', 'modulus')
            - class names (e.g., 'Percentage', 'Modulus')
        Raises ValueError if the requested operation type is not registered.
        """
        operation_type = operation_type.lower().strip()

        # Direct key match
        if operation_type in cls._operations:
            return cls._operations[operation_type]()

        # Class-name fallback (handles e.g. 'Percentage' or 'IntegerDivision')
        for key, op_cls in cls._operations.items():
            if op_cls.__name__.lower() == operation_type:
                return op_cls()

        # If not found, raise an explicit error
        raise ValueError(f"Unknown operation: {operation_type}")
