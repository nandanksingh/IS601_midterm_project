# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/24/2025
# Midterm Project - Enhanced Calculator
# File: tests/test_help_decorator.py
# ----------------------------------------------------------
# Description:
# Unit tests for app/help_decorator.py implementing the
# Decorator Design Pattern for dynamic help menu generation.
#
# Covers:
#   • Verification of HelpBase default output and structure
#   • Validation of HelpDecorator behavior and enhancements
#   • Ensures proper text formatting and output consistency
#   • Confirms decorator chaining, independence, and robustness
# ----------------------------------------------------------

import pytest
from app.help_decorator import HelpBase, HelpDecorator


@pytest.fixture
def base_help():
    """Provide a HelpBase instance for base-level tests."""
    return HelpBase()


@pytest.fixture
def decorated_help(base_help):
    """Provide a HelpDecorator instance wrapping HelpBase."""
    return HelpDecorator(base_help)


# ----------------------------------------------------------
# Tests for HelpBase
# ----------------------------------------------------------
def test_help_base_contains_core_sections(base_help):
    """Check that HelpBase includes all primary calculator commands."""
    text = base_help.show_help()
    assert isinstance(text, str)
    assert "add" in text
    assert "subtract" in text
    assert "undo" in text
    assert "exit" in text
    assert "help" in text
    assert text.startswith("\nAvailable Commands:")


def test_help_base_formatting(base_help):
    """Ensure HelpBase output has correct formatting and indentation."""
    text = base_help.show_help()
    assert "\n  add" in text
    assert "help, exit" in text
    assert "undo, redo, history, clear" in text


# ----------------------------------------------------------
# Tests for HelpDecorator
# ----------------------------------------------------------
def test_help_decorator_appends_dynamic_message(decorated_help):
    """Ensure HelpDecorator extends base help text with an additional message."""
    base_text = HelpBase().show_help()
    decorated_text = decorated_help.show_help()
    assert decorated_text.startswith(base_text)
    assert "Decorator Pattern" in decorated_text
    assert "Hint:" in decorated_text


def test_help_decorator_independence(base_help):
    """Check that multiple HelpDecorator instances behave consistently."""
    d1 = HelpDecorator(base_help)
    d2 = HelpDecorator(base_help)
    assert d1.show_help() == d2.show_help()


def test_help_decorator_output_differs_from_base(base_help):
    """Confirm decorator output differs and extends beyond base output."""
    decorated = HelpDecorator(base_help)
    assert decorated.show_help() != base_help.show_help()
    assert len(decorated.show_help()) > len(base_help.show_help())


def test_help_decorator_chainability(base_help):
    """Verify decorators can be chained together for multiple enhancements."""
    first_layer = HelpDecorator(base_help)
    second_layer = HelpDecorator(first_layer)
    text = second_layer.show_help()
    assert text.count("Decorator Pattern") >= 2
    assert "(Hint:" in text


# ----------------------------------------------------------
# Edge Case and Robustness Tests
# ----------------------------------------------------------
def test_help_base_no_error_on_direct_call():
    """Ensure HelpBase.show_help executes without any runtime error."""
    hb = HelpBase()
    result = hb.show_help()
    assert isinstance(result, str)
    assert "Available Commands" in result


def test_help_decorator_no_error_on_direct_call():
    """Ensure HelpDecorator.show_help executes safely without error."""
    hd = HelpDecorator(HelpBase())
    result = hd.show_help()
    assert isinstance(result, str)
    assert "Decorator Pattern" in result


def test_help_decorator_robustness_against_empty_base(monkeypatch):
    """Handle edge case where base help returns an empty string."""
    class EmptyBase:
        def show_help(self): 
            return ""
    decorator = HelpDecorator(EmptyBase())
    result = decorator.show_help()
    assert "(Hint:" in result
    assert "Decorator Pattern" in result


def test_help_decorator_text_integrity(monkeypatch):
    """Ensure the decorator preserves base text and appends additional content."""
    class DummyBase:
        def show_help(self):
            return "COMMANDS"
    decorator = HelpDecorator(DummyBase())
    result = decorator.show_help()
    assert result.startswith("COMMANDS")
    assert "Decorator Pattern" in result
