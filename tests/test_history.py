# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/17/2025
# Midterm Project: Enhanced Calculator (Observer Pattern Tests)
# ----------------------------------------------------------
# Description:
# This test module validates the functionality of the Observer
# Design Pattern implemented in `app/history.py`.
#
# Observers Tested:
#   1. LoggingObserver – Verifies correct logging of each calculation.
#   2. AutoSaveObserver – Ensures automatic save behavior triggers
#                         only when auto-save is enabled.
#
# Test Coverage Includes:
#   - Normal and error-handling cases for LoggingObserver
#   - Conditional auto-save behavior in AutoSaveObserver
#   - Validation of incorrect or missing input handling
# ----------------------------------------------------------

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from app.calculation import Calculation
from app.history import LoggingObserver, AutoSaveObserver
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig


# ----------------------------------------------------------
# Helper Setup
# ----------------------------------------------------------

# Create a mock Calculation object for testing
calculation_mock = Mock(spec=Calculation)
calculation_mock.operation = "addition"
calculation_mock.operand1 = 5
calculation_mock.operand2 = 3
calculation_mock.result = 8


# ----------------------------------------------------------
# LoggingObserver Tests
# ----------------------------------------------------------

@patch("logging.info")
def test_logging_observer_logs_calculation(mock_log_info):
    """Verify that LoggingObserver logs the correct calculation message."""
    observer = LoggingObserver()
    observer.update(calculation_mock)
    mock_log_info.assert_called_once_with(
        "Calculation performed: addition (5, 3) = 8"
    )


def test_logging_observer_no_calculation():
    """Ensure that passing None to LoggingObserver raises an AttributeError."""
    observer = LoggingObserver()
    with pytest.raises(AttributeError):
        observer.update(None)


def test_logging_observer_logs_exception(monkeypatch):
    """
    Force LoggingObserver to hit the exception block for coverage.
    Simulates a logging failure scenario.
    """
    from app.history import LoggingObserver
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))
    observer = LoggingObserver()

    # Simulate logging.info raising an error
    def bad_log(_):
        raise RuntimeError("Simulated disk failure")

    monkeypatch.setattr("logging.info", bad_log)

    with pytest.raises(RuntimeError, match="Logging failed: Simulated disk failure"):
        observer.update(calc)


# ----------------------------------------------------------
# AutoSaveObserver Tests
# ----------------------------------------------------------

def test_autosave_observer_triggers_save():
    """Verify that AutoSaveObserver calls save_history() when auto_save is enabled."""
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True

    observer = AutoSaveObserver(calculator_mock)
    observer.update(calculation_mock)

    calculator_mock.save_history.assert_called_once()


@patch("logging.info")
def test_autosave_observer_logs_autosave(mock_log_info):
    """Confirm that AutoSaveObserver logs a message after auto-saving history."""
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True

    observer = AutoSaveObserver(calculator_mock)
    observer.update(calculation_mock)

    mock_log_info.assert_called_once_with("History auto-saved successfully.")


def test_autosave_observer_does_not_trigger_save_when_disabled():
    """Ensure that AutoSaveObserver does NOT save when auto_save is disabled."""
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = False

    observer = AutoSaveObserver(calculator_mock)
    observer.update(calculation_mock)

    calculator_mock.save_history.assert_not_called()


def test_autosave_observer_invalid_calculator():
    """Ensure that AutoSaveObserver raises TypeError if initialized with an invalid calculator."""
    with pytest.raises(TypeError):
        AutoSaveObserver(None)


def test_autosave_observer_no_calculation():
    """Ensure that AutoSaveObserver raises AttributeError if no calculation is provided."""
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True

    observer = AutoSaveObserver(calculator_mock)

    with pytest.raises(AttributeError):
        observer.update(None)


def test_autosave_observer_logs_exception(monkeypatch):
    """
    Force AutoSaveObserver to hit the exception block for coverage.
    Simulates a failure in the save_history() method.
    """
    from types import SimpleNamespace
    import logging

    calc_stub = SimpleNamespace(config=SimpleNamespace(auto_save=True))

    # save_history() will raise IOError to simulate disk write error
    def bad_save():
        raise IOError("Disk full")

    calc_stub.save_history = bad_save
    observer = AutoSaveObserver(calc_stub)

    with pytest.raises(RuntimeError, match="AutoSave failed: Disk full"):
        observer.update(SimpleNamespace(operation="Addition"))
