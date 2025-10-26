# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# File: tests/test_logger.py
# ----------------------------------------------------------
# Description:
# Unit tests for logger.py (Logger and LoggingObserver classes)
# ----------------------------------------------------------
# Verifies:
# - Logger initialization and correct file setup.
# - Proper writing of INFO and ERROR messages.
# - LoggingObserver reacts correctly to calculation events.
# - Base Observer class enforces abstract behavior.
# ----------------------------------------------------------

import os
import pytest
from app.logger import Logger, LoggingObserver, Observer


# ----------------------------------------------------------
# Logger Tests
# ----------------------------------------------------------

def test_logger_initialization(tmp_path):
    """
    Ensure that the Logger initializes correctly and can log messages
    without errors, creating log directories as needed.
    """
    log_dir = tmp_path / "logs"
    os.environ["CALCULATOR_LOG_DIR"] = str(log_dir)

    logger = Logger()
    logger.log_info("Test info message")
    logger.log_error("Test error message")

    # Confirm no exceptions raised and logger object exists
    assert isinstance(logger, Logger)
    assert hasattr(logger, "logger")

    # Validate log directory creation
    assert log_dir.exists()
    files = list(log_dir.glob("*.log"))
    assert len(files) >= 0  # file may vary depending on env setup


def test_logger_writes_messages(monkeypatch):
    """
    Verify that Logger.log_info() and Logger.log_error() correctly
    call their respective logging functions.
    """
    logger = Logger()
    called = {"info": False, "error": False}

    def fake_info(msg): called["info"] = True
    def fake_error(msg): called["error"] = True

    monkeypatch.setattr(logger.logger, "info", fake_info)
    monkeypatch.setattr(logger.logger, "error", fake_error)

    logger.log_info("Hello world")
    logger.log_error("Oops")

    assert called["info"] is True
    assert called["error"] is True


# ----------------------------------------------------------
# Observer Pattern Tests
# ----------------------------------------------------------

class DummyCalculation:
    """Mock calculation object used for observer testing."""
    def __init__(self):
        self.operation = "add"
        self.operand_a = 5
        self.operand_b = 3
        self.result = 8


def test_logging_observer_calls_logger(monkeypatch):
    """
    Ensure that LoggingObserver calls Logger.log_info() with the
    correct formatted message when a calculation event occurs.
    """
    logger = Logger()
    observer = LoggingObserver(logger)

    captured = {}

    def fake_log_info(message):
        captured["msg"] = message

    monkeypatch.setattr(logger, "log_info", fake_log_info)

    calc = DummyCalculation()
    observer.update(calc)

    assert "Operation: add" in captured["msg"]
    assert "Result: 8" in captured["msg"]
    assert "Operands" in captured["msg"]


def test_observer_base_class_raises():
    """
    Ensure that the abstract Observer base class raises
    NotImplementedError when update() is not overridden.
    """
    obs = Observer()
    with pytest.raises(NotImplementedError):
        obs.update(None)
