# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/19/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# File: tests/test_calculation.py
# ----------------------------------------------------------
# Description:
# Comprehensive tests for the Calculation dataclass and
# CalculationFactory using pytest.
# Covers:
#   - Attribute validation (operation, a, b, result, timestamp)
#   - All arithmetic operations and edge cases
#   - Factory registration and unknown operation handling
#   - Serialization / Deserialization (CSV compatibility)
#   - Formatting, equality, and repr/str checks
#   - 100 percent coverage including logging branches
# ----------------------------------------------------------

import pytest
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
from app.calculation import Calculation, CalculationFactory
from app.exceptions import OperationError


# ----------------------------------------------------------
# BASIC FUNCTIONAL TESTS
# ----------------------------------------------------------

def test_calculation_auto_computes_result():
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    assert calc.result == Decimal("5")
    assert isinstance(calc.timestamp, datetime)


@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("add", Decimal("4"), Decimal("6"), Decimal("10")),
        ("subtract", Decimal("10"), Decimal("3"), Decimal("7")),
        ("multiply", Decimal("2"), Decimal("5"), Decimal("10")),
        ("divide", Decimal("8"), Decimal("2"), Decimal("4")),
        ("modulus", Decimal("10"), Decimal("3"), Decimal("1")),
        ("int_divide", Decimal("9"), Decimal("2"), Decimal("4")),
        ("power", Decimal("2"), Decimal("3"), Decimal("8")),
        ("root", Decimal("16"), Decimal("2"), Decimal("4")),
        ("percent", Decimal("25"), Decimal("100"), Decimal("25")),
        ("abs_diff", Decimal("9"), Decimal("6"), Decimal("3")),
    ],
)
def test_all_operations_work_correctly(operation, a, b, expected):
    calc = Calculation(operation, a, b)
    assert calc.result == expected


# ----------------------------------------------------------
# ERROR HANDLING TESTS
# ----------------------------------------------------------

@pytest.mark.parametrize("operation", ["divide", "modulus", "int_divide", "percent"])
def test_division_by_zero_operations(operation):
    with pytest.raises(OperationError, match="Division by zero"):
        Calculation(operation, Decimal("8"), Decimal("0"))


def test_root_zero_raises_error():
    with pytest.raises(OperationError, match="Zero root is undefined"):
        Calculation("root", Decimal("9"), Decimal("0"))


def test_root_negative_number_raises_error():
    with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
        Calculation("root", Decimal("-16"), Decimal("2"))


def test_invalid_operands_raise_operationerror():
    with pytest.raises(OperationError, match="Invalid operands"):
        Calculation("add", "invalid", Decimal("5"))


def test_unknown_operation_raises_operationerror():
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation("unknown_op", Decimal("3"), Decimal("4"))


def test_arithmetic_error_branch(monkeypatch):
    """Forces the except (ArithmeticError, InvalidOperation, ValueError) block."""
    calc = Calculation("add", Decimal("2"), Decimal("3"))

    def bad_func(x, y):
        raise ArithmeticError("forced arithmetic error")

    CalculationFactory.operations["bad_op"] = bad_func
    calc.operation = "bad_op"

    with pytest.raises(OperationError, match="Calculation failed"):
        calc.perform_operation()


# ----------------------------------------------------------
# SERIALIZATION / DESERIALIZATION TESTS
# ----------------------------------------------------------

def test_to_dict_returns_expected_keys():
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    data = calc.to_dict()
    expected_keys = {"operation", "a", "b", "result", "timestamp"}
    assert set(data.keys()) == expected_keys
    assert data["a"] == "2" and data["b"] == "3" and data["result"] == "5"


def test_from_dict_restores_valid_calculation():
    data = {
        "operation": "add",
        "a": "2",
        "b": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat(),
    }
    calc = Calculation.from_dict(data)
    assert isinstance(calc, Calculation)
    assert calc.result == Decimal("5")


def test_from_dict_logs_warning_for_result_mismatch(caplog):
    data = {
        "operation": "add",
        "a": "2",
        "b": "3",
        "result": "999",
        "timestamp": datetime.now().isoformat(),
    }
    with caplog.at_level(logging.WARNING):
        calc = Calculation.from_dict(data)
    assert "differs from computed result" in caplog.text
    assert calc.result == Decimal("5")


def test_from_dict_invalid_data_raises_error():
    data = {
        "operation": "add",
        "a": "bad",
        "b": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat(),
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)


# ----------------------------------------------------------
# FACTORY REGISTRATION TESTS
# ----------------------------------------------------------

def test_register_custom_operation_and_use():
    @CalculationFactory.register("triple")
    def _triple(x, y):
        return (x + y) * 3

    calc = Calculation("triple", Decimal("2"), Decimal("1"))
    assert calc.result == Decimal("9")
    assert "triple" in CalculationFactory.operations


# ----------------------------------------------------------
# STRING, REPR, AND EQUALITY TESTS
# ----------------------------------------------------------

def test_str_and_repr_output_contains_expected_text():
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    assert "add" in str(calc)
    assert "Calculation" in repr(calc)


def test_equality_and_inequality_between_calculations():
    c1 = Calculation("add", Decimal("2"), Decimal("3"))
    c2 = Calculation("add", Decimal("2"), Decimal("3"))
    c3 = Calculation("subtract", Decimal("4"), Decimal("1"))
    assert c1 == c2
    assert c1 != c3


def test_eq_with_non_calculation_returns_notimplemented():
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    assert calc.__eq__(42) == NotImplemented


# ----------------------------------------------------------
# FORMAT RESULT TESTS
# ----------------------------------------------------------

def test_format_result_with_precision_variants():
    calc = Calculation("divide", Decimal("1"), Decimal("3"))
    r2 = calc.format_result(precision=2)
    r5 = calc.format_result(precision=5)
    assert r2.startswith("0.33")
    assert r5.startswith("0.33333")


def test_format_result_invalidoperation_branch():
    calc = Calculation("add", Decimal("2"), Decimal("3"))

    class BadDecimal(Decimal):
        def quantize(self, *_, **__):
            raise InvalidOperation

    calc.result = BadDecimal("5")
    assert calc.format_result(precision=3) == "5"
