# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/25/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# File: tests/test_calculator_repl.py
# ----------------------------------------------------------
# Description:
# Comprehensive test suite for the interactive REPL interface.
# Covers:
#   • Command execution (arithmetic, history, undo/redo, save/load)
#   • Dynamic help menu (Decorator Pattern)
#   • Error handling and cancellation
#   • Full REPL lifecycle (start → help → exit)
#   • KeyboardInterrupt, EOF, and fatal error conditions
# Validates REPL commands, arithmetic operations, exception handling,
# colorized output (via colorama), and interactive loop behavior.
# ----------------------------------------------------------

import pytest
import sys
import re
from unittest.mock import patch, MagicMock
from app.calculator_repl import calculator_repl, _perform_command, cprint, _load_colorama


# ----------------------------------------------------------
# Fixture: Mock Calculator
# ----------------------------------------------------------
@pytest.fixture
def mock_calculator():
    """Create a mock Calculator with all required methods and fake history."""
    calc = MagicMock()
    mock_calc_obj = MagicMock()
    mock_calc_obj.__str__ = lambda self=None: "add(2,3)=5"
    mock_calc_obj.__repr__ = lambda self=None: "add(2,3)=5"

    calc.list_history.return_value = [mock_calc_obj]
    calc.undo.return_value = True
    calc.redo.return_value = True
    calc.calculate.return_value = MagicMock(result=5)
    calc.save_history.side_effect = None
    calc.load_history.side_effect = None
    return calc


# ----------------------------------------------------------
# Command Execution Tests
# ----------------------------------------------------------
@patch("builtins.print")
def test_perform_command_addition(mock_print, mock_calculator, monkeypatch):
    """Simulate performing an addition operation with valid inputs."""
    inputs = iter(["2", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = _perform_command(mock_calculator, "add")
    assert result is True
    mock_calculator.calculate.assert_called_once()


@patch("builtins.print")
def test_perform_command_cancel_first_input(mock_print, mock_calculator, monkeypatch):
    """Cancel arithmetic operation immediately after first prompt."""
    inputs = iter(["cancel"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    _perform_command(mock_calculator, "multiply")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Operation cancelled" in text


@patch("builtins.print")
def test_perform_command_cancel_second_input(mock_print, mock_calculator, monkeypatch):
    """Cancel arithmetic operation after second input."""
    inputs = iter(["2", "cancel"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    _perform_command(mock_calculator, "divide")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Operation cancelled" in text


@patch("builtins.print")
def test_perform_command_invalid_number_input(mock_print, mock_calculator, monkeypatch):
    """Invalid number input triggers ValidationError."""
    from app.exceptions import ValidationError
    inputs = iter(["abc", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    mock_calculator.calculate.side_effect = ValidationError("Invalid numeric input.")
    _perform_command(mock_calculator, "add")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Validation Error" in text or "Invalid numeric input" in text


@patch("builtins.print")
def test_perform_command_history(mock_print, mock_calculator):
    """Verify printing of stored calculation history."""
    _perform_command(mock_calculator, "history")
    text = " ".join(" ".join(map(str, c.args)) for c in mock_print.call_args_list)
    assert "Calculation History" in text
    assert "add(2,3)=5" in text or "add" in text or "5" in text


@patch("builtins.print")
def test_perform_command_history_empty(mock_print, mock_calculator):
    """When list_history() returns empty list."""
    mock_calculator.list_history.return_value = []
    _perform_command(mock_calculator, "history")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "No calculations yet" in text


@patch("builtins.print")
def test_perform_command_undo_redo(mock_print, mock_calculator):
    """Undo/redo commands trigger calculator methods correctly."""
    _perform_command(mock_calculator, "undo")
    _perform_command(mock_calculator, "redo")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Undo successful" in text
    assert "Redo successful" in text


@patch("builtins.print")
def test_perform_command_clear_save_load(mock_print, mock_calculator):
    """Test clear, save, and load commands."""
    _perform_command(mock_calculator, "clear")
    _perform_command(mock_calculator, "save")
    _perform_command(mock_calculator, "load")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "History cleared" in text
    assert "History saved successfully" in text
    assert "History loaded successfully" in text


@patch("builtins.print")
def test_perform_command_help_and_exit(mock_print, mock_calculator):
    """Validate dynamic help decorator and exit flow."""
    _perform_command(mock_calculator, "help")

    # Simulate save_history failure to hit safe-exit try/except
    mock_calculator.save_history.side_effect = Exception("save failed")
    _perform_command(mock_calculator, "exit")

    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Help" in text or "Decorator Pattern" in text
    assert "Exiting the calculator" in text


@patch("builtins.print")
def test_perform_command_unknown(mock_print, mock_calculator):
    """Unknown commands handled gracefully."""
    _perform_command(mock_calculator, "xyz")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Unknown command" in text


# ----------------------------------------------------------
# Error Handling Tests
# ----------------------------------------------------------
@patch("builtins.print")
def test_validation_operation_generic_errors(mock_print, mock_calculator, monkeypatch):
    """Trigger ValidationError, OperationError, and Exception branches."""
    from app.exceptions import ValidationError, OperationError
    inputs = iter(["2", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    mock_calculator.calculate.side_effect = ValidationError("invalid input")
    _perform_command(mock_calculator, "add")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Validation Error" in text
    mock_print.reset_mock()

    # OperationError
    mock_calculator.calculate.side_effect = OperationError("forced op fail")
    _perform_command(mock_calculator, "add")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    assert (
        "Operation Error" in text
        or "Unexpected error" in text
        or "forced op fail" in text
    )
    mock_print.reset_mock()

    # Generic Exception
    mock_calculator.calculate.side_effect = Exception("unexpected fail")
    _perform_command(mock_calculator, "add")
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Unexpected error" in text


@patch("builtins.print")
def test_perform_command_operationerror_branch(mock_print, mock_calculator, monkeypatch):
    """Explicitly trigger OperationError inside _perform_command to cover lines 162–163."""
    from app.exceptions import OperationError

    # Monkeypatch input() to avoid reading from stdin
    monkeypatch.setattr("builtins.input", lambda _: "2")

    # Force OperationError directly in calculator.calculate()
    mock_calculator.calculate.side_effect = OperationError("operation failed internally")

    _perform_command(mock_calculator, "add")

    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)

    assert "Operation Error" in text
    assert "operation failed internally" in text


# ----------------------------------------------------------
# REPL Lifecycle Tests
# ----------------------------------------------------------
@patch("builtins.print")
def test_repl_exit_flow(mock_print):
    """Simulate typing 'exit' to confirm REPL shuts down cleanly."""
    commands = iter(["exit"])
    calculator_repl(input_func=lambda _: next(commands))
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Exiting the calculator" in text


@patch("builtins.print")
def test_repl_keyboard_interrupt(mock_print):
    """KeyboardInterrupt exits gracefully."""
    def raise_interrupt(_): raise KeyboardInterrupt
    calculator_repl(input_func=raise_interrupt)
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Keyboard interrupt" in text


@patch("builtins.print")
def test_repl_eof_exit(mock_print):
    """EOFError (Ctrl+D) exits gracefully."""
    def raise_eof(_): raise EOFError
    calculator_repl(input_func=raise_eof)
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Input closed" in text


@patch("builtins.print")
def test_repl_fatal_error_outer_loop(mock_print):
    """Trigger fatal error in the outer REPL loop"""
    class ExplodingInput:
        def __call__(self, prompt):
            raise RuntimeError("crash in input")

    calculator_repl(input_func=ExplodingInput())

    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Fatal REPL error" in text
    assert "crash in input" in text


@patch("builtins.print")
def test_repl_empty_then_exit(mock_print):
    """Handle empty input followed by an exit command."""
    commands = iter(["", "exit"])
    calculator_repl(input_func=lambda _: next(commands))
    text = " ".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "Exiting the calculator" in text


# ----------------------------------------------------------
# Color Output Tests
# ----------------------------------------------------------
@patch("builtins.print")
def test_cprint_with_color(mock_print, monkeypatch):
    """Verify that cprint adds color codes when colorama is available."""
    from types import SimpleNamespace
    fake_fore = SimpleNamespace(GREEN="G", RED="R", YELLOW="Y", CYAN="C", WHITE="W")
    fake_style = SimpleNamespace(RESET_ALL="!")
    monkeypatch.setattr("app.calculator_repl.Fore", fake_fore)
    monkeypatch.setattr("app.calculator_repl.Style", fake_style)
    cprint("Hello", color="green")
    mock_print.assert_called_once_with("GHello!")


@patch("builtins.print")
def test_cprint_without_color(mock_print, monkeypatch):
    """Ensure cprint falls back to plain printing when colorama not available."""
    monkeypatch.setattr("app.calculator_repl.Fore", None)
    monkeypatch.setattr("app.calculator_repl.Style", None)
    cprint("Plain Text", color="red")
    mock_print.assert_called_once_with("Plain Text")


# ----------------------------------------------------------
# Colorama Import Tests
# ----------------------------------------------------------
def test_load_colorama_success(monkeypatch):
    """Confirm successful import of colorama returns Fore and Style objects."""
    fake_module = type("Fake", (), {"init": lambda autoreset: True, "Fore": "fore", "Style": "style"})
    monkeypatch.setitem(sys.modules, "colorama", fake_module)
    fore, style = _load_colorama()
    assert fore == "fore" and style == "style"


def test_load_colorama_failure(monkeypatch):
    """Ensure ImportError during colorama import handled gracefully."""
    sys.modules.pop("colorama", None)
    import builtins
    original_import = builtins.__import__

    def raise_import(name, *args, **kwargs):
        if name == "colorama":
            raise ImportError
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", raise_import)
    fore, style = _load_colorama()
    assert fore is None and style is None
