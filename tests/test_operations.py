# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# ----------------------------------------------------------
# Description:
# This test suite validates all arithmetic operations implemented in
# app/operations.py, ensuring correctness, validation handling, and
# Factory Design Pattern integrity.
# ----------------------------------------------------------

import pytest
from decimal import Decimal
from typing import Any, Dict, Type

from app.exceptions import ValidationError
from app.operations import (
    Operation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Power,
    Root,
    Modulus,
    IntegerDivision,
    Percentage,
    AbsoluteDifference,
    OperationFactory,
)


# ----------------------------------------------------------
# Test Base Operation Functionality
# ----------------------------------------------------------
class TestOperation:
    """Verify base Operation class behavior."""

    def test_str_representation(self):
        """Ensure string representation returns class name."""
        class TestOp(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a
        assert str(TestOp()) == "TestOp"


# ----------------------------------------------------------
# Common Reusable Base for Operation Tests
# ----------------------------------------------------------
class BaseOperationTest:
    """Reusable base test structure for arithmetic operations."""
    operation_class: Type[Operation]
    valid_test_cases: Dict[str, Dict[str, Any]]
    invalid_test_cases: Dict[str, Dict[str, Any]]

    def test_valid_operations(self):
        """Run valid test cases."""
        operation = self.operation_class()
        for name, case in self.valid_test_cases.items():
            a = Decimal(str(case["a"]))
            b = Decimal(str(case["b"]))
            expected = Decimal(str(case["expected"]))
            result = operation.execute(a, b)
            assert result == expected, f"Failed case: {name}"

    def test_invalid_operations(self):
        """Run invalid test cases (should raise ValidationError)."""
        if not self.invalid_test_cases:
            pytest.skip("No invalid cases defined for this operation.")
        operation = self.operation_class()
        for name, case in self.invalid_test_cases.items():
            a = Decimal(str(case["a"]))
            b = Decimal(str(case["b"]))
            error = case.get("error", ValidationError)
            message = case.get("message", "")
            with pytest.raises(error, match=message):
                operation.execute(a, b)


# ----------------------------------------------------------
# Basic Arithmetic Operation Tests
# ----------------------------------------------------------
class TestAddition(BaseOperationTest):
    operation_class = Addition
    valid_test_cases = {
        "positive": {"a": "5", "b": "3", "expected": "8"},
        "negative": {"a": "-5", "b": "-3", "expected": "-8"},
        "mixed": {"a": "-5", "b": "3", "expected": "-2"},
        "zero": {"a": "5", "b": "-5", "expected": "0"},
        "decimal": {"a": "5.5", "b": "3.3", "expected": "8.8"},
    }
    invalid_test_cases = {}


class TestSubtraction(BaseOperationTest):
    operation_class = Subtraction
    valid_test_cases = {
        "positive": {"a": "5", "b": "3", "expected": "2"},
        "negative": {"a": "-5", "b": "-3", "expected": "-2"},
        "mixed": {"a": "-5", "b": "3", "expected": "-8"},
        "zero_result": {"a": "5", "b": "5", "expected": "0"},
    }
    invalid_test_cases = {}


class TestMultiplication(BaseOperationTest):
    operation_class = Multiplication
    valid_test_cases = {
        "positive": {"a": "5", "b": "3", "expected": "15"},
        "negative": {"a": "-5", "b": "-3", "expected": "15"},
        "mixed": {"a": "-5", "b": "3", "expected": "-15"},
        "by_zero": {"a": "5", "b": "0", "expected": "0"},
    }
    invalid_test_cases = {}


class TestDivision(BaseOperationTest):
    operation_class = Division
    valid_test_cases = {
        "positive": {"a": "6", "b": "2", "expected": "3"},
        "negative": {"a": "-6", "b": "-2", "expected": "3"},
        "mixed": {"a": "-6", "b": "2", "expected": "-3"},
        "decimal": {"a": "5.5", "b": "2", "expected": "2.75"},
    }
    invalid_test_cases = {
        "divide_by_zero": {
            "a": "5", "b": "0",
            "error": ValidationError,
            "message": "Division by zero is not allowed"
        },
    }


# ----------------------------------------------------------
# Advanced Operation Tests (Midterm Additions)
# ----------------------------------------------------------
class TestPower(BaseOperationTest):
    operation_class = Power
    valid_test_cases = {
        "base_exponent": {"a": "2", "b": "3", "expected": "8"},
        "zero_exp": {"a": "5", "b": "0", "expected": "1"},
        "decimal_base": {"a": "2.5", "b": "2", "expected": "6.25"},
    }
    invalid_test_cases = {}


class TestRoot(BaseOperationTest):
    operation_class = Root
    valid_test_cases = {
        "square_root": {"a": "9", "b": "2", "expected": "3"},
        "cube_root": {"a": "27", "b": "3", "expected": "3"},
    }
    invalid_test_cases = {
        "zero_root": {
            "a": "9", "b": "0",
            "error": ValidationError,
            "message": "Zero root is undefined"
        },
    }


class TestModulus(BaseOperationTest):
    operation_class = Modulus
    valid_test_cases = {
        "positive": {"a": "10", "b": "3", "expected": "1"},
        "negative": {"a": "-10", "b": "3", "expected": "-1"},
        "divisible": {"a": "6", "b": "3", "expected": "0"},
    }
    invalid_test_cases = {
        "mod_by_zero": {
            "a": "5", "b": "0",
            "error": ValidationError,
            "message": "Cannot perform modulus with divisor 0"
        },
    }


class TestIntegerDivision(BaseOperationTest):
    operation_class = IntegerDivision
    valid_test_cases = {
        "positive": {"a": "7", "b": "2", "expected": "3"},
        "negative": {"a": "-7", "b": "2", "expected": "-4"},
        "exact": {"a": "6", "b": "3", "expected": "2"},
    }
    invalid_test_cases = {
        "div_by_zero": {
            "a": "7", "b": "0",
            "error": ValidationError,
            "message": "Cannot perform integer division by zero"
        },
    }


class TestPercentage(BaseOperationTest):
    operation_class = Percentage
    valid_test_cases = {
        "simple": {"a": "50", "b": "200", "expected": "25"},
        "full": {"a": "100", "b": "100", "expected": "100"},
        "half": {"a": "1", "b": "2", "expected": "50"},
    }
    invalid_test_cases = {
        "div_by_zero": {
            "a": "5", "b": "0",
            "error": ValidationError,
            "message": "Cannot calculate percentage with divisor 0"
        },
    }


class TestAbsoluteDifference(BaseOperationTest):
    operation_class = AbsoluteDifference
    valid_test_cases = {
        "positive_diff": {"a": "10", "b": "6", "expected": "4"},
        "negative_diff": {"a": "3", "b": "8", "expected": "5"},
        "zero_diff": {"a": "5", "b": "5", "expected": "0"},
    }
    invalid_test_cases = {}  # Always valid


# ----------------------------------------------------------
# Factory Design Pattern Tests
# ----------------------------------------------------------
class TestOperationFactory:
    """Validate operation creation through the Factory pattern."""

    def test_create_all_operations(self):
        """Ensure all known operations are instantiable."""
        mapping = {
            'add': Addition,
            'subtract': Subtraction,
            'multiply': Multiplication,
            'divide': Division,
            'power': Power,
            'root': Root,
            'modulus': Modulus,
            'int_divide': IntegerDivision,
            'percentage': Percentage,
            'abs_diff': AbsoluteDifference,
        }

        for op_name, op_class in mapping.items():
            instance = OperationFactory.create_operation(op_name)
            assert isinstance(instance, op_class)
            # Test case-insensitivity
            instance_upper = OperationFactory.create_operation(op_name.upper())
            assert isinstance(instance_upper, op_class)

    def test_create_invalid_operation(self):
        """Unknown operation should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown operation: invalid_op"):
            OperationFactory.create_operation("invalid_op")

    def test_register_new_operation(self):
        """Registering a valid new operation dynamically."""
        class NewOp(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a + b
        OperationFactory.register_operation("new_op", NewOp)
        instance = OperationFactory.create_operation("new_op")
        assert isinstance(instance, NewOp)

    def test_register_invalid_operation(self):
        """Registering invalid operation should raise TypeError."""
        class Invalid:
            pass
        with pytest.raises(TypeError, match="Operation class must inherit"):
            OperationFactory.register_operation("bad_op", Invalid)
