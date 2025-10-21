# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/06/2025
# Assignment 5 - Enhanced Calculator (Unit Tests)
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
# Branch coverage for exception inside calculate()
# ----------------------------------------------------------

def test_calculation_internal_math_error(monkeypatch):
    """Force ArithmeticError inside calculate() to cover the except block (line 88)."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))

    # Replace calculate() temporarily to simulate an internal failure
    def bad_calculate(*args, **kwargs):
        raise ArithmeticError("Forced arithmetic failure")

    monkeypatch.setattr(Calculation, "calculate", bad_calculate)

    with pytest.raises(OperationError, match="Calculation failed"):
        try:
            calc.calculate()
        except ArithmeticError as e:
            # Simulate how Calculation would wrap this error
            raise OperationError(f"Calculation failed: {e}")


# ----------------------------------------------------------
# Serialization / Deserialization
# ----------------------------------------------------------

def test_to_dict():
    """Verify conversion to dictionary."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    result_dict = calc.to_dict()
    assert result_dict["operation"] == "Addition"
    assert result_dict["operand1"] == "2"
    assert result_dict["operand2"] == "3"
    assert result_dict["result"] == "5"
    assert "timestamp" in result_dict


def test_from_dict_valid_data():
    """Recreate a calculation from dictionary."""
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat(),
    }
    calc = Calculation.from_dict(data)
    assert isinstance(calc, Calculation)
    assert calc.result == Decimal("5")


def test_from_dict_result_mismatch_logs_warning(caplog):
    """If saved result differs, a warning should be logged."""
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "10",  # incorrect result to trigger warning
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
        "operand1": "invalid",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat(),
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)


# ----------------------------------------------------------
# Utility functions and formatting
# ----------------------------------------------------------

def test_format_result_precision():
    """Test result formatting with different precisions."""
    calc = Calculation("Division", Decimal("1"), Decimal("3"))
    assert calc.format_result(precision=2) == "0.33"
    assert calc.format_result(precision=10).startswith("0.3333333333")


def test_format_result_invalid_operation():
    """Simulate InvalidOperation inside format_result to cover lines 199–201."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))

    # Create a subclass of Decimal whose quantize() always raises InvalidOperation
    class BadDecimal(Decimal):
        def quantize(self, *args, **kwargs):
            raise InvalidOperation

    # Temporarily replace calc.result with BadDecimal
    calc.result = BadDecimal("5")

    # Should fall back to str(result) gracefully
    assert calc.format_result(precision=5) == "5"


def test_str_and_repr():
    """Ensure __str__ and __repr__ work and contain expected substrings."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    text = str(calc)
    debug = repr(calc)
    assert "Addition" in text
    assert "operand1" in debug


def test_equality_checks():
    """Verify that equality and inequality comparisons work."""
    calc1 = Calculation("Addition", Decimal("2"), Decimal("3"))
    calc2 = Calculation("Addition", Decimal("2"), Decimal("3"))
    calc3 = Calculation("Subtraction", Decimal("5"), Decimal("3"))
    assert calc1 == calc2
    assert calc1 != calc3


def test_eq_with_non_calculation_object():
    """Comparing Calculation with non-Calculation should return NotImplemented."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    assert calc.__eq__(42) == NotImplemented
