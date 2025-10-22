# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project - Enhanced Calculator (Calculation.py)
# ----------------------------------------------------------
# Covers:
#   • All arithmetic operations
#   • Error and edge cases
#   • Serialization / Deserialization (pandas CSV compatibility)
#   • Formatting and display utilities
#   • Equality and representation
# ----------------------------------------------------------

import pytest
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError


# ----------------------------------------------------------
# Basic arithmetic operations
# ----------------------------------------------------------

def test_addition():
    """Test addition operation."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    assert calc.result == Decimal("5")


def test_subtraction():
    """Test subtraction operation."""
    calc = Calculation("Subtraction", Decimal("5"), Decimal("3"))
    assert calc.result == Decimal("2")


def test_multiplication():
    """Test multiplication operation."""
    calc = Calculation("Multiplication", Decimal("4"), Decimal("2"))
    assert calc.result == Decimal("8")


def test_division():
    """Test normal division operation."""
    calc = Calculation("Division", Decimal("8"), Decimal("2"))
    assert calc.result == Decimal("4")


# ----------------------------------------------------------
# Error handling and edge cases
# ----------------------------------------------------------

def test_division_by_zero():
    """Division by zero should raise OperationError."""
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation("Division", Decimal("8"), Decimal("0"))


def test_power_operation():
    """Test power operation."""
    calc = Calculation("Power", Decimal("2"), Decimal("3"))
    assert calc.result == Decimal("8")


def test_negative_power_error():
    """Negative exponent should raise OperationError."""
    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation("Power", Decimal("2"), Decimal("-3"))


def test_root_operation():
    """Test square root operation."""
    calc = Calculation("Root", Decimal("16"), Decimal("2"))
    assert calc.result == Decimal("4")


def test_zero_root_error():
    """Zero root should raise OperationError."""
    with pytest.raises(OperationError, match="Zero root is undefined"):
        Calculation("Root", Decimal("9"), Decimal("0"))


def test_invalid_root_negative_number():
    """Root of a negative number should raise OperationError."""
    with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
        Calculation("Root", Decimal("-16"), Decimal("2"))


def test_invalid_root_generic_error():
    """Trigger the final branch of _raise_invalid_root."""
    with pytest.raises(OperationError, match="Invalid root operation"):
        Calculation._raise_invalid_root(Decimal("4"), Decimal("5"))


def test_unknown_operation():
    """Unknown operation should raise OperationError."""
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation("Unknown", Decimal("5"), Decimal("3"))


# ----------------------------------------------------------
# Serialization / Deserialization (Step 9)
# ----------------------------------------------------------

def test_to_dict_keys_match():
    """Verify dictionary keys for pandas serialization."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    d = calc.to_dict()
    expected_keys = {"operation", "operand_a", "operand_b", "result", "timestamp"}
    assert set(d.keys()) == expected_keys
    assert d["operand_a"] == "2"
    assert d["operand_b"] == "3"
    assert d["result"] == "5"


def test_from_dict_valid_data():
    """Recreate a calculation from dictionary with new key names."""
    data = {
        "operation": "Addition",
        "operand_a": "2",
        "operand_b": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat(),
    }
    calc = Calculation.from_dict(data)
    assert isinstance(calc, Calculation)
    assert calc.result == Decimal("5")


def test_from_dict_old_key_compatibility():
    """Support backward-compatible operand1/operand2 keys."""
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat(),
    }
    calc = Calculation.from_dict(data)
    assert calc.result == Decimal("5")


def test_from_dict_result_mismatch_logs_warning(caplog):
    """If saved result differs, a warning should be logged."""
    data = {
        "operation": "Addition",
        "operand_a": "2",
        "operand_b": "3",
        "result": "10",  # incorrect result
        "timestamp": datetime.now().isoformat(),
    }
    with caplog.at_level(logging.WARNING):
        calc = Calculation.from_dict(data)
    assert "differs from computed result" in caplog.text
    assert calc.result == Decimal("5")


def test_from_dict_invalid_data():
    """Invalid operand should raise OperationError."""
    data = {
        "operation": "Addition",
        "operand_a": "invalid",
        "operand_b": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat(),
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)


# ----------------------------------------------------------
# Utility functions and formatting
# ----------------------------------------------------------

def test_format_result_precision():
    """Result formatting with variable precision."""
    calc = Calculation("Division", Decimal("1"), Decimal("3"))
    assert calc.format_result(precision=2).startswith("0.33")
    assert calc.format_result(precision=8).startswith("0.33333333")


def test_format_result_invalid_operation():
    """Simulate InvalidOperation inside format_result."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))

    class BadDecimal(Decimal):
        def quantize(self, *_, **__):
            raise InvalidOperation

    calc.result = BadDecimal("5")
    assert calc.format_result(precision=5) == "5"


def test_str_and_repr_contains_expected_text():
    """Ensure __str__ and __repr__ return meaningful strings."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    assert "Addition" in str(calc)
    assert "Calculation" in repr(calc)


def test_equality_and_inequality():
    """Verify equality checks and comparison logic."""
    a = Calculation("Addition", Decimal("2"), Decimal("3"))
    b = Calculation("Addition", Decimal("2"), Decimal("3"))
    c = Calculation("Subtraction", Decimal("5"), Decimal("3"))
    assert a == b
    assert a != c


def test_eq_with_non_calculation_returns_notimplemented():
    """Comparing with non-Calculation should return NotImplemented."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    assert calc.__eq__(42) == NotImplemented
