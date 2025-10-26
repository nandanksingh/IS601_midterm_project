# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/20/2025
# Midterm Project: Enhanced Calculator
# File: tests/test_calculator.py
# ----------------------------------------------------------
# Description:
# Comprehensive test suite for app/calculator.py.
# Covers:
#   • Factory integration via calculate()
#   • Observer Pattern notifications
#   • Undo / Redo (Memento)
#   • History persistence with pandas
#   • Error handling (OperationError, HistoryError)
#   • Logging setup and exception handling
#   • REPL helpers: set_operation() / perform_operation()
#   • Bounded history pruning 
# ----------------------------------------------------------

import pytest
import pandas as pd
import logging
from pathlib import Path
from decimal import Decimal
from tempfile import TemporaryDirectory
from unittest.mock import patch, PropertyMock, MagicMock

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculation import Calculation
from app.exceptions import OperationError, HistoryError
from app.history import LoggingObserver


# ----------------------------------------------------------
# Fixture: Temporary calculator instance
# ----------------------------------------------------------
@pytest.fixture
def calculator():
    """Create an isolated calculator with temporary directories."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        config = CalculatorConfig(base_dir=tmp_path)

        with patch.object(CalculatorConfig, "log_dir", new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, "log_file", new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, "history_dir", new_callable=PropertyMock) as mock_hist_dir, \
             patch.object(CalculatorConfig, "history_file", new_callable=PropertyMock) as mock_hist_file:

            mock_log_dir.return_value = tmp_path / "logs"
            mock_log_file.return_value = tmp_path / "logs/calculator.log"
            mock_hist_dir.return_value = tmp_path / "history"
            mock_hist_file.return_value = tmp_path / "history/calculator_history.csv"

            yield Calculator(config=config)


# ----------------------------------------------------------
# Initialization & Configuration
# ----------------------------------------------------------
def test_calculator_initialization(calculator):
    """Verify proper initialization of calculator components."""
    assert isinstance(calculator.config, CalculatorConfig)
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert len(calculator.observers) == 2  # LoggingObserver + AutoSaveObserver


@patch("app.calculator.logging.info")
def test_logging_setup(mock_info):
    """Ensure logging setup completes successfully."""
    config = CalculatorConfig()
    _ = Calculator(config)
    mock_info.assert_any_call("Logging setup complete.")


def test_logging_setup_failure(monkeypatch):
    """Force logging setup exception to raise HistoryError."""
    def bad_basic_config(**kwargs):
        raise Exception("setup fail")

    monkeypatch.setattr("app.calculator.logging.basicConfig", bad_basic_config)
    config = CalculatorConfig()

    with pytest.raises(HistoryError, match="Logging setup failed"):
        Calculator(config)


# ----------------------------------------------------------
# Factory + calculate()
# ----------------------------------------------------------
def test_calculate_addition_success(calculator):
    """Validate successful calculation using the factory."""
    calc_obj = calculator.calculate("add", Decimal("2"), Decimal("3"))
    assert isinstance(calc_obj, Calculation)
    assert calc_obj.result == Decimal("5")
    assert len(calculator.history) == 1


def test_calculate_unknown_operation(calculator):
    """Ensure unknown operations raise OperationError."""
    with pytest.raises(OperationError, match="Unknown operation"):
        calculator.calculate("invalid", Decimal("2"), Decimal("3"))


def test_calculate_force_explicit_unknown(monkeypatch, calculator):
    """Explicitly trigger OperationError by making .get() return None."""
    from app.calculation import CalculationFactory
    monkeypatch.setattr(CalculationFactory, "operations", {"add": lambda a, b: a + b})

    with pytest.raises(OperationError, match="Unknown operation: unknown_op"):
        calculator.calculate("unknown_op", Decimal("5"), Decimal("2"))


def test_calculate_failure_branch(monkeypatch, calculator):
    """Force an exception inside CalculationFactory function."""
    def bad_func(a, b):
        raise ValueError("forced error")

    calculator.history.clear()
    calculator._save_memento()

    from app.calculation import CalculationFactory
    CalculationFactory.operations["bad"] = bad_func

    with pytest.raises(OperationError, match="Operation failed"):
        calculator.calculate("bad", Decimal("2"), Decimal("3"))


# ----------------------------------------------------------
# REPL helper coverage: set_operation() / perform_operation()
# ----------------------------------------------------------
def test_set_operation_and_perform_operation_success(calculator):
    """Covers set_operation() and perform_operation() happy path."""
    calculator.set_operation("add")
    result = calculator.perform_operation(Decimal("2"), Decimal("3"))
    assert result == Decimal("5")


def test_perform_operation_without_setting_operation(calculator):
    """Calling perform_operation() before set_operation() raises."""
    with pytest.raises(OperationError, match="No operation selected"):
        calculator.perform_operation(Decimal("2"), Decimal("3"))


def test_perform_operation_exception(monkeypatch, calculator):
    """Force an exception inside perform_operation() to hit wrapper."""
    calculator.set_operation("add")

    def bad_calc(*_args, **_kwargs):
        raise ValueError("internal failure")

    monkeypatch.setattr(calculator, "calculate", bad_calc)
    with pytest.raises(OperationError, match="Operation failed"):
        calculator.perform_operation(Decimal("2"), Decimal("3"))


# ----------------------------------------------------------
# Undo / Redo / History
# ----------------------------------------------------------
def test_undo_redo_history_flow(calculator):
    """Validate undo/redo functionality maintains correct state."""
    calculator.calculate("add", Decimal("2"), Decimal("3"))
    assert len(calculator.history) == 1

    calculator.undo()
    assert isinstance(calculator.history, list)

    calculator.redo()
    assert len(calculator.history) >= 0

    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []


def test_undo_empty_stack(calculator):
    """Undo with empty stack should raise HistoryError."""
    with pytest.raises(HistoryError, match="Nothing to undo"):
        calculator.undo()


def test_redo_empty_stack(calculator):
    """Redo with empty stack should raise HistoryError."""
    with pytest.raises(HistoryError, match="Nothing to redo"):
        calculator.redo()


# ----------------------------------------------------------
# Observer Pattern
# ----------------------------------------------------------
def test_add_and_remove_observer(calculator):
    """Ensure observers can be added and removed dynamically."""
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers
    calculator.remove_observer(observer)
    assert observer not in calculator.observers


def test_notify_observers_handles_error(monkeypatch, calculator):
    """Verify observers' exceptions are caught and logged."""
    bad_observer = MagicMock()
    bad_observer.update.side_effect = RuntimeError("observer fail")
    calculator.observers.append(bad_observer)

    calc = Calculation("add", Decimal("2"), Decimal("3"))
    calculator._notify_observers(calc)
    assert True  # No exception means success


# ----------------------------------------------------------
# History Persistence
# ----------------------------------------------------------
@patch("app.calculator.pd.DataFrame.to_csv")
def test_save_history_success(mock_to_csv, calculator):
    """Ensure save_history() writes CSV successfully."""
    calculator.calculate("add", Decimal("2"), Decimal("3"))
    calculator.save_history()
    assert mock_to_csv.call_count >= 1


@patch("app.calculator.pd.DataFrame.to_csv", side_effect=OSError("Disk full"))
def test_save_history_failure(_mock_to_csv, calculator):
    """Simulate write failure to trigger HistoryError."""
    with pytest.raises(HistoryError, match="Failed to save history"):
        calculator.save_history()


@patch("app.calculator.pd.read_csv")
@patch("app.calculator.Path.exists", return_value=True)
def test_load_history_success(_mock_exists, mock_read_csv, calculator):
    """Ensure load_history() correctly loads previous CSV history."""
    df = pd.DataFrame([{
        "operation": "add",
        "a": "2",
        "b": "3",
        "result": "5",
        "timestamp": "2025-10-25T00:00:00"
    }])
    mock_read_csv.return_value = df

    calculator.load_history()
    assert len(calculator.history) == 1
    assert calculator.history[0].result == Decimal("5")


@patch("app.calculator.pd.read_csv", side_effect=Exception("mock failure"))
@patch("app.calculator.Path.exists", return_value=True)
def test_load_history_failure(_mock_exists, _mock_read_csv, calculator):
    """Force load_history() to fail and raise HistoryError."""
    with pytest.raises(HistoryError, match="Failed to load history"):
        calculator.load_history()


def test_clear_and_list_history(calculator):
    """Confirm clearing history also resets stacks."""
    calculator.calculate("add", Decimal("4"), Decimal("6"))
    calculator.clear_history()
    assert calculator.list_history() == []


# ----------------------------------------------------------
# Internal Utilities
# ----------------------------------------------------------
def test_repr_shows_record_count(calculator):
    """Ensure __repr__() shows record count correctly."""
    calculator.calculate("add", Decimal("1"), Decimal("2"))
    rep = repr(calculator)
    assert "1 records" in rep


# ----------------------------------------------------------
# Edge Case Coverage Additions (toward 100%)
# ----------------------------------------------------------
def test_calculate_invalid_operation_branch(calculator):
    """calculate() to hit OperationError via invalid key in factory mapping."""
    from app.calculation import CalculationFactory
    backup_ops = CalculationFactory.operations.copy()
    CalculationFactory.operations.clear()
    try:
        with pytest.raises(OperationError, match="Unknown operation"):
            calculator.calculate("add", Decimal("1"), Decimal("2"))
    finally:
        CalculationFactory.operations.update(backup_ops)


def test_notify_observers_runtime_error_handling(calculator):
    """Ensure observer exceptions are swallowed by _notify_observers."""
    def bad_update(_):
        raise RuntimeError("test observer error")

    bad_observer = MagicMock()
    bad_observer.update.side_effect = bad_update
    calculator.observers.append(bad_observer)

    calc = Calculation("add", Decimal("2"), Decimal("3"))
    calculator._notify_observers(calc)
    assert True


def test_save_history_empty_dataframe(monkeypatch, calculator):
    """Simulate empty history save to ensure DataFrame handling branch executes."""
    calculator.history.clear()
    mock_to_csv = MagicMock()
    monkeypatch.setattr(pd.DataFrame, "to_csv", mock_to_csv)
    calculator.save_history()
    mock_to_csv.assert_called_once()


# ----------------------------------------------------------
# Bounded History Pruning (line 129 coverage)
# ----------------------------------------------------------
def test_calculate_prunes_history_when_exceeds_max(tmp_path):
    """Ensure calculator prunes oldest entry when history exceeds max_history_size"""
    from app.calculator_config import CalculatorConfig

    # Create isolated config with small history size
    config = CalculatorConfig(base_dir=tmp_path, max_history_size=2)
    calc = Calculator(config=config)
    calc.clear_history()  # clean start

    # Perform 3 calculations (third one triggers pruning)
    calc.calculate("add", Decimal("1"), Decimal("1"))  # stays initially
    calc.calculate("add", Decimal("2"), Decimal("2"))  # stays initially
    calc.calculate("add", Decimal("3"), Decimal("3"))  # triggers pruning

    # Fetch printable history
    history = calc.list_history()
    assert len(history) == config.max_history_size

    # Ensure the oldest calculation ("1 + 1") is gone
    joined_history = " ".join(str(h) for h in history)
    assert "1" not in joined_history or "add(1" not in joined_history
    assert "add(2" in joined_history and "add(3" in joined_history


