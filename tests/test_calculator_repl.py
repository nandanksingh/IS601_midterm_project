# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/06/2025
# Assignment 5 - Enhanced Calculator (REPL Tests)
# ----------------------------------------------------------

import pytest
from unittest.mock import patch, MagicMock
from app.calculator_repl import calculator_repl, _perform_command
from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError


# ----------------------------------------------------------
# Helper Function
# ----------------------------------------------------------

def make_calc_mock():
    """Creates a safe mock Calculator object for REPL testing."""
    calc = MagicMock(spec=Calculator)
    calc.show_history.return_value = ["Addition(2, 3) = 5"]
    calc.undo.return_value = True
    calc.redo.return_value = True
    return calc


# ----------------------------------------------------------
# Unit Tests for _perform_command()
# ----------------------------------------------------------

def test_help_command(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "help")
    assert "Available commands" in capsys.readouterr().out


def test_exit_command(capsys):
    calc = make_calc_mock()
    calc.save_history = MagicMock()
    result = _perform_command(calc, "exit")
    assert result is False
    assert "Goodbye!" in capsys.readouterr().out


def test_exit_command_with_save_error(capsys):
    calc = make_calc_mock()
    calc.save_history.side_effect = Exception("save failed")
    result = _perform_command(calc, "exit")
    assert result is False
    assert "Warning" in capsys.readouterr().out


def test_history_command(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "history")
    assert "Calculation History" in capsys.readouterr().out


def test_history_empty(capsys):
    calc = make_calc_mock()
    calc.show_history.return_value = []
    _perform_command(calc, "history")
    assert "No calculations" in capsys.readouterr().out


def test_clear_command(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "clear")
    assert "History cleared" in capsys.readouterr().out


def test_undo_redo_commands(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "undo")
    _perform_command(calc, "redo")
    out = capsys.readouterr().out
    assert "Operation undone" in out or "Operation redone" in out


def test_save_load_commands(capsys):
    calc = make_calc_mock()
    _perform_command(calc, "save")
    _perform_command(calc, "load")
    out = capsys.readouterr().out
    assert "History saved" in out or "History loaded" in out


def test_save_load_with_errors(capsys):
    calc = make_calc_mock()
    calc.save_history.side_effect = Exception("save fail")
    calc.load_history.side_effect = Exception("load fail")
    _perform_command(calc, "save")
    _perform_command(calc, "load")
    out = capsys.readouterr().out
    assert "Error saving" in out or "Error loading" in out


# ----------------------------------------------------------
# Arithmetic Operation Tests (Safe for pytest I/O)
# ----------------------------------------------------------

@patch("builtins.input", side_effect=["cancel"])
def test_arithmetic_cancel_first(mock_input, capsys):
    """Ensure canceling on first input prints 'Operation cancelled'."""
    calc = make_calc_mock()
    _perform_command(calc, "add", input_func=lambda _: "cancel")
    assert "Operation cancelled" in capsys.readouterr().out


@patch("builtins.input", side_effect=["2", "cancel"])
def test_arithmetic_cancel_second(mock_input, capsys):
    """Ensure canceling on second input prints 'Operation cancelled'."""
    calc = make_calc_mock()
    responses = iter(["2", "cancel"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    assert "Operation cancelled" in capsys.readouterr().out


def test_arithmetic_valid(capsys):
    """Ensure valid arithmetic prints a result."""
    calc = make_calc_mock()
    calc.perform_operation.return_value = 5
    responses = iter(["2", "3"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    assert "Result" in capsys.readouterr().out


def test_arithmetic_validation_error(capsys):
    """Ensure validation errors print correctly."""
    calc = make_calc_mock()
    calc.perform_operation.side_effect = ValidationError("Invalid")
    responses = iter(["2", "3"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    assert "Error" in capsys.readouterr().out


def test_arithmetic_operation_error(capsys):
    """Ensure operation errors print correctly."""
    calc = make_calc_mock()
    calc.perform_operation.side_effect = OperationError("Op failed")
    responses = iter(["2", "3"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    assert "Error" in capsys.readouterr().out


def test_arithmetic_unexpected_error(capsys):
    """Ensure unexpected exceptions print correctly."""
    calc = make_calc_mock()
    calc.perform_operation.side_effect = Exception("Unexpected")
    responses = iter(["2", "3"])
    _perform_command(calc, "add", input_func=lambda _: next(responses))
    assert "Unexpected error" in capsys.readouterr().out


def test_unknown_command(capsys):
    """Ensure unknown commands are handled."""
    calc = make_calc_mock()
    _perform_command(calc, "random")
    assert "Unknown command" in capsys.readouterr().out


# ----------------------------------------------------------
# Integration Tests for calculator_repl() — Safe & Non-blocking
# ----------------------------------------------------------

@patch("builtins.print")
def test_repl_help_exit(mock_print):
    """Simulate a short REPL session with help and exit."""
    commands = iter(["help", "exit"])
    calculator_repl(input_func=lambda _: next(commands))
    mock_print.assert_any_call("Calculator started. Type 'help' for commands.")
    mock_print.assert_any_call("Goodbye!")


@patch("builtins.print")
def test_repl_keyboard_interrupt(mock_print):
    """Simulate Ctrl+C interruption inside REPL (safe exit)."""
    def interrupt_input(_):
        raise KeyboardInterrupt

    with patch("app.calculator.Calculator"):
        calculator_repl(input_func=interrupt_input)

    calls = [str(c) for c in mock_print.call_args_list]
    assert any("Calculator started" in c for c in calls)
    assert any("Ctrl+C" in c for c in calls)


@patch("builtins.print")
def test_repl_eof(mock_print):
    """Simulate Ctrl+D or EOF input."""
    def eof_input(_):
        raise EOFError

    with patch("app.calculator.Calculator"):
        calculator_repl(input_func=eof_input)
    mock_print.assert_any_call("Calculator started. Type 'help' for commands.")
    mock_print.assert_any_call("\nInput terminated (Ctrl+D). Exiting...")


@patch("builtins.print")
@patch("app.calculator.Calculator", side_effect=Exception("fatal"))
def test_repl_fatal_error(mock_calc, mock_print):
    """Simulate fatal error during REPL initialization."""
    #with pytest.raises(Exception, match="fatal"):
    calculator_repl()
    mock_print.assert_any_call("Fatal error: fatal")
