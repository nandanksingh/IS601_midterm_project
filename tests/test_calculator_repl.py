# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator (REPL Tests)
# ----------------------------------------------------------
# Description:
# Comprehensive test suite for the interactive REPL interface.
# Covers:
#  - Command execution (arithmetic, history, undo/redo, save/load)
#  - Error handling and cancellation
#  - Full REPL lifecycle (start → help → exit)
#  - KeyboardInterrupt, EOF, and fatal error conditions
# ----------------------------------------------------------

import re
import pytest
from unittest.mock import patch, MagicMock
from app.calculator_repl import calculator_repl, _perform_command
from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError


# ----------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------

def strip_ansi(text: str) -> str:
    """Remove ANSI color codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def make_calc_mock():
    """Create a mock Calculator with predictable responses."""
    calc = MagicMock(spec=Calculator)
    calc.show_history.return_value = ["Addition(2, 3) = 5"]
    calc.undo.return_value = True
    calc.redo.return_value = True
    calc.perform_operation.return_value = 5
    return calc


# ----------------------------------------------------------
# Unit Tests for _perform_command()
# ----------------------------------------------------------

def test_help_command(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "help")
    out = strip_ansi(capsys.readouterr().out)
    assert "Available commands" in out


def test_exit_command(capsys):
    calc = make_calc_mock()
    calc.save_history = MagicMock()
    result = _perform_command(calc, "exit")
    out = strip_ansi(capsys.readouterr().out)
    assert result is False
    assert "Goodbye" in out


def test_exit_command_with_save_error(capsys):
    calc = make_calc_mock()
    calc.save_history.side_effect = Exception("save failed")
    result = _perform_command(calc, "exit")
    out = strip_ansi(capsys.readouterr().out)
    assert result is False
    assert "Warning" in out


def test_history_command(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "history")
    out = strip_ansi(capsys.readouterr().out)
    assert "Calculation History" in out


def test_history_empty(capsys):
    calc = make_calc_mock()
    calc.show_history.return_value = []
    _perform_command(calc, "history")
    out = strip_ansi(capsys.readouterr().out)
    assert "No calculations" in out


def test_clear_command(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "clear")
    out = strip_ansi(capsys.readouterr().out)
    assert "History cleared" in out


def test_undo_redo_commands(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "undo")
    _perform_command(calc, "redo")
    out = strip_ansi(capsys.readouterr().out)
    assert "Operation undone" in out or "Operation redone" in out


def test_save_load_commands(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "save")
    _perform_command(calc, "load")
    out = strip_ansi(capsys.readouterr().out)
    assert "History saved" in out or "History loaded" in out


def test_save_load_with_errors(capsys):
    calc = make_calc_mock()
    calc.save_history.side_effect = Exception("save fail")
    calc.load_history.side_effect = Exception("load fail")
    _perform_command(calc, "save")
    _perform_command(calc, "load")
    out = strip_ansi(capsys.readouterr().out)
    assert "Error saving" in out or "Error loading" in out


# ----------------------------------------------------------
# Arithmetic Operation Tests
# ----------------------------------------------------------

@patch("builtins.input", side_effect=["cancel"])
def test_arithmetic_cancel_first(mock_input, capsys):
    """Cancelling on first number should abort operation."""
    calc = make_calc_mock()
    _perform_command(calc, "add", input_func=lambda _: "cancel")
    out = strip_ansi(capsys.readouterr().out)
    assert "Operation cancelled" in out


@patch("builtins.input", side_effect=["2", "cancel"])
def test_arithmetic_cancel_second(mock_input, capsys):
    """Cancelling on second number should abort operation."""
    calc = make_calc_mock()
    responses = iter(["2", "cancel"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    out = strip_ansi(capsys.readouterr().out)
    assert "Operation cancelled" in out


def test_arithmetic_valid(capsys):
    """Valid arithmetic should display a correct result."""
    calc = make_calc_mock()
    responses = iter(["2", "3"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    out = strip_ansi(capsys.readouterr().out)
    assert "Result" in out and "5" in out


def test_arithmetic_validation_error(capsys):
    """Validation errors should be printed properly."""
    calc = make_calc_mock()
    calc.perform_operation.side_effect = ValidationError("Invalid")
    responses = iter(["2", "3"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    out = strip_ansi(capsys.readouterr().out)
    assert "Validation Error" in out


def test_arithmetic_operation_error(capsys):
    """Operation errors should be printed properly."""
    calc = make_calc_mock()
    calc.perform_operation.side_effect = OperationError("Op failed")
    responses = iter(["2", "3"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    out = strip_ansi(capsys.readouterr().out)
    assert "Operation Error" in out


def test_arithmetic_unexpected_error(capsys):
    """Unexpected errors should be handled gracefully."""
    calc = make_calc_mock()
    calc.perform_operation.side_effect = Exception("Unexpected")
    responses = iter(["2", "3"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    out = strip_ansi(capsys.readouterr().out)
    assert "Unexpected Error" in out


@pytest.mark.parametrize("cmd", ["power", "root"])
def test_other_arithmetic_operations(cmd, capsys):
    """Ensure other arithmetic operations print a result."""
    calc = make_calc_mock()
    responses = iter(["2", "3"])
    _perform_command(calc, cmd, input_func=lambda _: next(responses))
    out = strip_ansi(capsys.readouterr().out)
    assert "Result" in out


def test_unknown_command(capsys):
    """Unknown commands should print a warning message."""
    calc = make_calc_mock()
    _perform_command(calc, "random")
    out = strip_ansi(capsys.readouterr().out)
    assert "Unknown command" in out


# ----------------------------------------------------------
# Integration Tests for calculator_repl()
# ----------------------------------------------------------

@patch("builtins.print")
def test_repl_help_exit(mock_print):
    """Simulate REPL session with help and exit."""
    commands = iter(["help", "exit"])
    calculator_repl(input_func=lambda _: next(commands))
    calls = [strip_ansi(str(c)) for c in mock_print.call_args_list]
    assert any("Calculator started" in c for c in calls)
    assert any("Goodbye" in c for c in calls)


@patch("builtins.print")
def test_repl_keyboard_interrupt(mock_print):
    """Simulate Ctrl+C inside REPL."""
    def interrupt_input(_):
        raise KeyboardInterrupt

    with patch("app.calculator.Calculator"):
        calculator_repl(input_func=interrupt_input)

    calls = [strip_ansi(str(c)) for c in mock_print.call_args_list]
    assert any("Calculator started" in c for c in calls)
    assert any("Ctrl+C" in c for c in calls)


@patch("builtins.print")
def test_repl_eof(mock_print):
    """Simulate Ctrl+D (EOF) inside REPL."""
    def eof_input(_):
        raise EOFError

    with patch("app.calculator.Calculator"):
        calculator_repl(input_func=eof_input)

    calls = [strip_ansi(str(c)) for c in mock_print.call_args_list]
    assert any("Calculator started" in c for c in calls)
    assert any("Ctrl+D" in c for c in calls)


@patch("builtins.print")
@patch("app.calculator.Calculator", side_effect=Exception("fatal"))
def test_repl_fatal_error(mock_calc, mock_print):
    """Simulate fatal Calculator initialization error."""
    calculator_repl()
    calls = [strip_ansi(str(c)) for c in mock_print.call_args_list]
    assert any("Fatal error" in c for c in calls)
