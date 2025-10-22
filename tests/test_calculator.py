# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator (Calculator Tests)
# ----------------------------------------------------------
# Description:
# Comprehensive test suite for app/calculator.py validating:
# - Factory + Strategy integration for all operations
# - Observer Pattern behavior
# - History persistence (save/load/undo/redo)
# - REPL command coverage and edge cases
# ----------------------------------------------------------

import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory

from app.calculator import Calculator
from app.calculator_repl import calculator_repl, _perform_command
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver

# ----------------------------------------------------------
# Fixtures
# ----------------------------------------------------------

@pytest.fixture
def calculator():
    """Creates an isolated calculator instance in a temporary directory."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:

            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"

            yield Calculator(config=config)

# ----------------------------------------------------------
# Initialization and Logging
# ----------------------------------------------------------

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

@patch("app.calculator.logging.info")
def test_logging_setup(mock_log_info):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_file:
        mock_dir.return_value = Path("/tmp/logs")
        mock_file.return_value = Path("/tmp/logs/calculator.log")
        Calculator(CalculatorConfig())
        mock_log_info.assert_any_call("Calculator initialized successfully")

def test_calculator_initializes_with_default_config():
    calc = Calculator()
    assert isinstance(calc.config, CalculatorConfig)

# ----------------------------------------------------------
# Observer Pattern
# ----------------------------------------------------------

def test_add_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# ----------------------------------------------------------
# Factory + Strategy Pattern
# ----------------------------------------------------------

def test_set_operation_factory_success(calculator):
    calculator.set_operation("add")
    assert calculator.operation_strategy is not None
    assert "Addition" in str(calculator.operation_strategy)

def test_set_operation_factory_invalid(calculator):
    with pytest.raises(OperationError, match="Unknown operation"):
        calculator.set_operation("invalid_op")

# ----------------------------------------------------------
# Operation Execution
# ----------------------------------------------------------

def test_perform_operation_addition(calculator):
    calculator.set_operation("add")
    result = calculator.perform_operation(2, 3)
    assert result == Decimal("5")

def test_perform_operation_validation_error(calculator):
    calculator.set_operation("add")
    with pytest.raises(ValidationError):
        calculator.perform_operation("invalid", 3)

def test_perform_operation_no_strategy(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# ----------------------------------------------------------
# Undo / Redo / Clear
# ----------------------------------------------------------

def test_undo_redo_clear(calculator):
    calculator.set_operation("add")
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []
    calculator.redo()
    assert len(calculator.history) == 1
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# ----------------------------------------------------------
# History Save / Load
# ----------------------------------------------------------

@patch("app.calculator.pd.DataFrame.to_csv")
def test_save_history(mock_to_csv, calculator):
    calculator.set_operation("add")
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch("app.calculator.pd.read_csv")
@patch("app.calculator.Path.exists", return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    mock_read_csv.return_value = pd.DataFrame({
        "operation": ["Addition"],
        "operand1": ["2"],
        "operand2": ["3"],
        "result": ["5"],
        "timestamp": [datetime.datetime.now().isoformat()],
    })
    calculator.load_history()
    assert len(calculator.history) == 1
    assert calculator.history[0].result == Decimal("5")

@patch("app.calculator.pd.read_csv", side_effect=Exception("mock failure"))
@patch("app.calculator.Path.exists", return_value=True)
def test_load_history_failure(mock_exists, mock_read_csv, calculator):
    with pytest.raises(OperationError, match="Failed to load history"):
        calculator.load_history()

# ----------------------------------------------------------
# History Utilities
# ----------------------------------------------------------

def test_get_history_dataframe(calculator):
    calculator.set_operation("add")
    calculator.perform_operation(2, 3)
    df = calculator.get_history_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_show_history_returns_formatted_strings(calculator):
    calculator.set_operation("add")
    calculator.perform_operation(2, 3)
    history = calculator.show_history()
    assert "Addition(2, 3) = 5" in history[0]

# ----------------------------------------------------------
# REPL Command Tests (Safe / Non-Blocking)
# ----------------------------------------------------------

def test_perform_command_all(monkeypatch):
    calc = Calculator()
    monkeypatch.setattr("builtins.input", lambda _: "cancel")

    for cmd in ["help", "history", "clear", "undo", "redo", "save", "load", "add", "unknown"]:
        assert _perform_command(calc, cmd)
    assert _perform_command(calc, "exit") is False

@patch("builtins.print")
def test_repl_addition_integration(mock_print):
    commands = iter(["add", "2", "3", "exit"])
    calculator_repl(input_func=lambda _: next(commands))
    assert any("Result" in str(call) and "5" in str(call)
               for call in mock_print.call_args_list)

@patch("builtins.print")
def test_repl_help_exit(mock_print):
    commands = iter(["help", "exit"])
    calculator_repl(input_func=lambda _: next(commands))
    assert any("Available commands" in str(call) for call in mock_print.call_args_list)

@patch("builtins.print")
def test_repl_exit_with_save(mock_print):
    with patch("app.calculator.Calculator.save_history") as mock_save:
        commands = iter(["exit"])
        calculator_repl(input_func=lambda _: next(commands))
        mock_save.assert_called_once()

# ----------------------------------------------------------
# Edge-Case Coverage
# ----------------------------------------------------------

def test_setup_logging_failure(monkeypatch, tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config)
    monkeypatch.setattr("os.makedirs", lambda *a, **k: (_ for _ in ()).throw(OSError("Permission denied")))
    with pytest.raises(Exception, match="Permission denied"):
        calc._setup_logging()

def test_setup_directories_failure(monkeypatch, tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config)
    monkeypatch.setattr("pathlib.Path.mkdir", lambda *a, **k: (_ for _ in ()).throw(OSError("Dir create fail")))
    with pytest.raises(OSError, match="Dir create fail"):
        calc._setup_directories()

def test_save_history_failure(monkeypatch, tmp_path):
    import pandas as pd
    from app.exceptions import OperationError
    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config)
    calc.history.append(
        type("FakeCalc", (), {
            "operation": "Add", "operand1": 1, "operand2": 2, "result": 3,
            "timestamp": datetime.datetime.now()
        })()
    )
    monkeypatch.setattr(pd.DataFrame, "to_csv", lambda *a, **k: (_ for _ in ()).throw(OSError("Write fail")))
    with pytest.raises(OperationError, match="Write fail"):
        calc.save_history()

def test_load_empty_and_missing(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    calc = Calculator(config)
    calc.history.clear()
    calc.config.history_file.unlink(missing_ok=True)
    calc.load_history()
    assert calc.history == []

def test_get_history_dataframe_empty(tmp_path):
    calc = Calculator(CalculatorConfig(base_dir=tmp_path))
    df = calc.get_history_dataframe()
    assert df.empty

def test_undo_redo_empty(tmp_path):
    calc = Calculator(CalculatorConfig(base_dir=tmp_path))
    assert calc.undo() is False
    assert calc.redo() is False
