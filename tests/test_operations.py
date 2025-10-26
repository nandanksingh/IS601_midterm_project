# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/20/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# File: tests/test_operations.py
# ----------------------------------------------------------
# Description:
# Tests all arithmetic operations and the factory registration mechanism.
# Covers:
#   - Arithmetic correctness
#   - Validation errors (e.g., divide by zero)
#   - Dynamic operation creation
#   - Operation registry integrity
# ----------------------------------------------------------

import pytest
from decimal import Decimal
from app.exceptions import ValidationError
from app.operations import (
    Add,
    Subtract,
    Multiply,
    Divide,
    Power,
    Root,
    Modulus,
    IntDivide,
    Percent,
    AbsDiff,
    OperationFactory,
    register_operation,
    Operation,
)

# ----------------------------------------------------------
# BASIC OPERATIONS
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "op,a,b,expected",
    [
        (Add(), "5", "3", "8"),
        (Subtract(), "10", "4", "6"),
        (Multiply(), "6", "3", "18"),
        (Divide(), "6", "2", "3"),
    ],
)
def test_basic_operations(op, a, b, expected):
    """Check basic arithmetic correctness."""
    result = op.execute(Decimal(a), Decimal(b))
    assert result == Decimal(expected)


@pytest.mark.parametrize("a,b", [("5", "0"), ("10", "0"), ("-8", "0")])
def test_divide_by_zero(a, b):
    """Division by zero must raise ValidationError."""
    with pytest.raises(ValidationError, match="Division by zero"):
        Divide().execute(Decimal(a), Decimal(b))


# ----------------------------------------------------------
# ADVANCED OPERATIONS
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "op,a,b,expected",
    [
        (Power(), "2", "3", "8"),
        (Power(), "5", "0", "1"),
        (Root(), "9", "2", "3"),
        (Root(), "27", "3", "3"),
        (Modulus(), "10", "3", "1"),
        (IntDivide(), "7", "2", "3"),
        (Percent(), "50", "200", "25"),
        (AbsDiff(), "10", "6", "4"),
    ],
)
def test_advanced_operations(op, a, b, expected):
    """Check advanced arithmetic correctness."""
    result = op.execute(Decimal(a), Decimal(b))
    assert result == Decimal(expected)


# ----------------------------------------------------------
# VALIDATION AND EDGE CASES
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "op,a,b,message",
    [
        (Root(), "9", "0", "Zero root"),
        (Root(), "-16", "2", "even root"),
        (Modulus(), "5", "0", "modulus"),
        (IntDivide(), "7", "0", "integer division"),
        (Percent(), "5", "0", "percentage"),
    ],
)
def test_invalid_operand_cases(op, a, b, message):
    """Check ValidationError for invalid operand cases."""
    with pytest.raises(ValidationError, match=message):
        op.execute(Decimal(a), Decimal(b))


# ----------------------------------------------------------
# FACTORY PATTERN TESTS
# ----------------------------------------------------------
def test_factory_creates_operations():
    """Ensure all registered operations are constructible."""
    for name in [
        "add",
        "subtract",
        "multiply",
        "divide",
        "power",
        "root",
        "modulus",
        "int_divide",
        "percent",
        "abs_diff",
    ]:
        op = OperationFactory.create_operation(name)
        assert isinstance(op, Operation)


def test_factory_case_insensitive():
    """OperationFactory should be case-insensitive."""
    assert isinstance(OperationFactory.create_operation("ADD"), Add)
    assert isinstance(OperationFactory.create_operation("Add"), Add)


def test_factory_invalid_operation():
    """Unknown operation must raise ValueError."""
    with pytest.raises(ValueError, match="Unknown operation"):
        OperationFactory.create_operation("invalid")


def test_register_new_operation_dynamically():
    """Register a new operation dynamically."""
    @register_operation("triple")
    class Triple(Operation):
        def execute(self, a, b):
            return a * 3

    op = OperationFactory.create_operation("triple")
    assert op.execute(Decimal("5"), Decimal("0")) == Decimal("15")


def test_list_operations_returns_dict():
    """OperationFactory.list_operations() should return a mapping."""
    ops = OperationFactory.list_operations()
    assert isinstance(ops, dict)
    assert "add" in ops


# ----------------------------------------------------------
# EXTRA COVERAGE TESTS
# ----------------------------------------------------------
def test_base_validate_operands_noop():
    """Cover base validate_operands()."""
    class Dummy(Operation):
        def execute(self, a, b):
            return a
    Dummy().validate_operands(Decimal("1"), Decimal("2"))


def test_power_overflow(monkeypatch):
    """Force overflow path in Power.execute()."""
    op = Power()
    def fake_pow(a, b):
        raise OverflowError
    monkeypatch.setattr("builtins.pow", fake_pow)
    with pytest.raises(ValidationError, match="Power result too large"):
        op.execute(Decimal("99"), Decimal("99"))


def test_str_representation():
    """Operation string output should be class name."""
    op = Multiply()
    assert str(op) == "Multiply"
