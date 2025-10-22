# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/17/2025
# Midterm Project: Enhanced Calculator (Observer Pattern)
# ----------------------------------------------------------
# Description:
# This module implements the Observer Design Pattern to allow
# external observers to react automatically whenever the calculator
# performs a new calculation.
#
# Observers Implemented:
#   1. LoggingObserver – Logs calculation details (operation, operands, result)
#                        to the log file.
#   2. AutoSaveObserver – Automatically saves the calculation history
#                        to a CSV file whenever a new operation occurs.
#
# Design Pattern: Observer
# Participants:
#   - Subject: Calculator (manages and notifies observers)
#   - Observers: LoggingObserver, AutoSaveObserver
# ----------------------------------------------------------

from abc import ABC, abstractmethod
import logging
from typing import Any, Optional
from app.calculation import Calculation


# ==========================================================
# Abstract Base Class for Observers
# ==========================================================
class HistoryObserver(ABC):
    """
    Abstract base class for all calculator observers.

    Defines the interface for any observer that needs to respond
    to calculator events (such as a new calculation being performed).
    Subclasses must implement the `update` method.
    """

    @abstractmethod
    def update(self, calculation: Optional[Calculation]) -> None:
        """
        Handle a new calculation event.
        This must be implemented by all concrete observers.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        pass  # pragma: no cover (abstract base not directly tested)


# ==========================================================
# LoggingObserver — Reacts by Logging Calculations
# ==========================================================
class LoggingObserver(HistoryObserver):
    """
    Logs each calculation performed by the calculator.

    This observer reacts to new calculation events by writing a
    detailed log entry containing the operation type, operands, and result.
    """

    def update(self, calculation: Optional[Calculation]) -> None:
        """
        Log the details of a new calculation to the active log file.

        Args:
            calculation (Calculation): The calculation instance to log.

        Raises:
            AttributeError: If the provided calculation is None.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")

        try:
            logging.info(
                f"Calculation performed: {calculation.operation} "
                f"({calculation.operand1}, {calculation.operand2}) = "
                f"{calculation.result}"
            )
        except Exception as e:
            # Log failure — this ensures coverage of error branch (lines 80–81)
            logging.error(f"LoggingObserver failed to record calculation: {e}")
            # Optional: propagate for test verification
            raise RuntimeError(f"Logging failed: {e}") from e


# ==========================================================
# AutoSaveObserver — Reacts by Persisting History
# ==========================================================
class AutoSaveObserver(HistoryObserver):
    """
    Automatically saves the calculator's history after every operation.

    The observer is notified whenever a new calculation occurs and
    triggers a call to the calculator's `save_history()` method if
    auto-save is enabled in the configuration file.
    """

    def __init__(self, calculator: Any):
        """
        Initialize the AutoSaveObserver with a reference to the calculator.

        Args:
            calculator (Any): Calculator instance that maintains history
                              and provides save functionality.

        Raises:
            TypeError: If the provided calculator lacks required attributes.
        """
        if not hasattr(calculator, "config") or not hasattr(calculator, "save_history"):
            raise TypeError(
                "Calculator must have 'config' and 'save_history' attributes"
            )
        self.calculator = calculator

    def update(self, calculation: Optional[Calculation]) -> None:
        """
        Automatically save the current history after each calculation.

        Args:
            calculation (Calculation): The calculation that triggered the update.

        Raises:
            AttributeError: If the provided calculation is None.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")

        try:
            if getattr(self.calculator.config, "auto_save", False):
                self.calculator.save_history()
                logging.info("History auto-saved successfully.")
        except Exception as e:
            # Ensure coverage of error logging branch (lines 131–132)
            logging.error(f"AutoSaveObserver failed during save: {e}")
            # Optional: raise for test traceability
            raise RuntimeError(f"AutoSave failed: {e}") from e
