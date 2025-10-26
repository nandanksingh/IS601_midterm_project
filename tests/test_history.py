# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/17/2025
# Midterm Project: Enhanced Calculator 
# File: tests/test_history.py
# ----------------------------------------------------------
# Description:
# Tests persistence and observer mechanisms in app/history.py
# Covers:
#   • History CRUD and persistence (save/load)
#   • Error handling and exception branches
#   • LoggingObserver and AutoSaveObserver
#   • 100% coverage, including all except branches
# ----------------------------------------------------------

import os
import pytest
import pandas as pd
import logging
from unittest.mock import Mock, patch
from decimal import Decimal
from app.history import History, LoggingObserver, AutoSaveObserver
from app.calculation import Calculation
from app.exceptions import HistoryError
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig


# ----------------------------------------------------------
# HISTORY CLASS TESTS
# ----------------------------------------------------------

def test_append_and_len_methods(tmp_path):
    file = tmp_path / "history.csv"
    history = History(str(file))
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    history.append(calc)
    assert len(history) == 1
    rep = repr(history)
    assert "add" in rep or "recent" in rep


def test_append_invalid_type_raises_error():
    history = History()
    with pytest.raises(HistoryError, match="Invalid calculation type"):
        history.append("not_a_calc")


def test_clear_resets_history():
    history = History()
    history.records = [Mock(), Mock()]
    history.clear()
    assert len(history.records) == 0


def test_save_and_load_roundtrip(tmp_path):
    """Validate saving and loading using pandas CSV."""
    file = tmp_path / "history.csv"
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    history = History(str(file))
    history.append(calc)
    history.save()

    loaded = History(str(file))
    loaded.load()
    assert len(loaded) == 1
    assert loaded.records[0].operation == "add"


def test_save_handles_exception(monkeypatch):
    history = History("bad_path.csv")
    monkeypatch.setattr(pd.DataFrame, "to_csv", lambda *a, **k: (_ for _ in ()).throw(IOError("disk full")))
    with pytest.raises(HistoryError, match="Failed to save history"):
        history.save()


def test_load_handles_missing_file(tmp_path, caplog):
    file = tmp_path / "missing.csv"
    history = History(str(file))
    history.load()
    assert len(history) == 0
    assert "No existing history" in caplog.text


def test_load_handles_corrupt_file(monkeypatch):
    monkeypatch.setattr(pd, "read_csv", lambda _: (_ for _ in ()).throw(ValueError("bad csv")))
    history = History("fake.csv")
    with pytest.raises(HistoryError, match="Failed to load history"):
        history.load()


# ----------------------------------------------------------
# OBSERVER TESTS
# ----------------------------------------------------------

@patch("logging.info")
def test_logging_observer_logs_calculation(mock_log):
    calc = Calculation("add", Decimal("1"), Decimal("2"))
    observer = LoggingObserver()
    observer.update(calc)
    mock_log.assert_called_once()


def test_logging_observer_none_raises():
    observer = LoggingObserver()
    with pytest.raises(AttributeError):
        observer.update(None)


def test_autosave_observer_triggers_save():
    calc_mock = Mock(spec=Calculator)
    calc_mock.config = Mock(spec=CalculatorConfig)
    calc_mock.config.auto_save = True
    observer = AutoSaveObserver(calc_mock)
    observer.update(Mock())
    calc_mock.save_history.assert_called_once()


def test_autosave_observer_disabled_does_not_trigger():
    calc_mock = Mock(spec=Calculator)
    calc_mock.config = Mock(spec=CalculatorConfig)
    calc_mock.config.auto_save = False
    observer = AutoSaveObserver(calc_mock)
    observer.update(Mock())
    calc_mock.save_history.assert_not_called()


def test_autosave_observer_invalid_calculator():
    with pytest.raises(TypeError):
        AutoSaveObserver(None)


def test_autosave_observer_logs_failure(monkeypatch):
    class DummyCalc:
        config = type("cfg", (), {"auto_save": True})()
        def save_history(self):
            raise IOError("Disk full")

    observer = AutoSaveObserver(DummyCalc())
    with pytest.raises(RuntimeError, match="AutoSave failed"):
        observer.update(Mock())


# ----------------------------------------------------------
# EXTRA BRANCH COVERAGE TESTS (for 100%)
# ----------------------------------------------------------

def test_save_unexpected_exception(monkeypatch):
    """Force an unexpected exception type in save() to hit except branch."""
    history = History("fake.csv")
    monkeypatch.setattr(pd.DataFrame, "to_csv", lambda *a, **k: (_ for _ in ()).throw(Exception("generic fail")))
    with pytest.raises(HistoryError, match="Failed to save history: generic fail"):
        history.save()


def test_load_unexpected_exception(monkeypatch):
    """Force a generic exception during load() to hit except branch."""
    monkeypatch.setattr(pd, "read_csv", lambda _: (_ for _ in ()).throw(RuntimeError("broken pandas")))
    history = History("fake.csv")
    with pytest.raises(HistoryError, match="Failed to load history: broken pandas"):
        history.load()


def test_logging_observer_exception_branch(monkeypatch):
    """Force a logging failure inside LoggingObserver.update()."""
    observer = LoggingObserver()
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    monkeypatch.setattr(logging, "info", lambda msg: (_ for _ in ()).throw(Exception("log fail")))
    with pytest.raises(RuntimeError, match="Logging failed"):
        observer.update(calc)


def test_autosave_observer_generic_exception(monkeypatch):
    """Force a generic exception in AutoSaveObserver to reach final except branch."""
    class DummyCalc:
        config = type("cfg", (), {"auto_save": True})()
        def save_history(self):
            raise ValueError("unknown failure")

    observer = AutoSaveObserver(DummyCalc())
    with pytest.raises(RuntimeError, match="AutoSave failed: unknown failure"):
        observer.update(Mock())

# ----------------------------------------------------------
# FINAL COVERAGE TESTS 
# ----------------------------------------------------------

def test_iter_method_returns_iterator():
    """Ensure __iter__ allows iteration over stored calculations."""
    history = History()
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    history.append(calc)
    result = list(history)  # triggers __iter__
    assert len(result) == 1
    assert isinstance(result[0], Calculation)


def test_repr_for_empty_history():
    """Ensure __repr__ includes 'empty' when history is blank."""
    history = History()
    rep = repr(history)
    assert "empty" in rep
    assert "History(size=0" in rep


def test_autosave_observer_update_none_raises():
    """Ensure AutoSaveObserver.update(None) raises AttributeError."""
    class DummyCalc:
        config = type("cfg", (), {"auto_save": True})()
        def save_history(self):
            pass

    observer = AutoSaveObserver(DummyCalc())
    with pytest.raises(AttributeError, match="cannot be None"):
        observer.update(None)
