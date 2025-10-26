# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/17/2025
# Midterm Project: Enhanced Calculator 
# File: app/history.py
# ----------------------------------------------------------
# Description:
# Implements:
#   1. History management — to store, save, and load calculation history.
#   2. Observer Design Pattern — enabling logging and auto-saving behavior.
#
# Classes:
#   - History            → Manages calculation records and persistence.
#   - HistoryObserver    → Abstract observer base class.
#   - LoggingObserver    → Logs every calculation automatically.
#   - AutoSaveObserver   → Auto-saves history when auto_save is enabled.
#
# Dependencies:
#   - pandas (for CSV operations)
#   - app.calculation.Calculation
#   - app.exceptions.HistoryError
# ----------------------------------------------------------

import pandas as pd
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from app.calculation import Calculation
from app.exceptions import HistoryError


# ==========================================================
# HISTORY CLASS — Core Persistence Manager
# ==========================================================
class History:
    """
    Manages all calculator history operations:
      - append() new results
      - clear() all records
      - save() and load() from CSV (persistent storage)
    """

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path or "./calculator_history.csv"
        self.records: List[Calculation] = []

    # ------------------------------------------------------
    # Core Operations
    # ------------------------------------------------------
    def append(self, calculation: Calculation) -> None:
        """Append a new calculation to history."""
        if not isinstance(calculation, Calculation):
            raise HistoryError("Invalid calculation type for history.")
        self.records.append(calculation)

    def clear(self) -> None:
        """Clear all stored calculations."""
        self.records.clear()

    # ------------------------------------------------------
    # CSV Persistence
    # ------------------------------------------------------
    def save(self) -> None:
        """Save calculation history to CSV using pandas."""
        try:
            data = [calc.to_dict() for calc in self.records]
            df = pd.DataFrame(data)
            df.to_csv(self.file_path, index=False)
            logging.info(f"History saved successfully to {self.file_path}")
        except Exception as e:
            logging.error(f"Failed to save history: {e}")
            raise HistoryError(f"Failed to save history: {e}") from e

    def load(self) -> None:
        """Load calculation history from CSV using pandas."""
        try:
            df = pd.read_csv(self.file_path)
            self.records = [Calculation.from_dict(row) for _, row in df.iterrows()]
            logging.info(f"History loaded successfully from {self.file_path}")
        except FileNotFoundError:
            logging.warning(f"No existing history file found at {self.file_path}")
            self.records = []
        except Exception as e:
            logging.error(f"Failed to load history: {e}")
            raise HistoryError(f"Failed to load history: {e}") from e

    # ------------------------------------------------------
    # Helpers
    # ------------------------------------------------------
    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        return iter(self.records)

    def __repr__(self) -> str:
        """Readable summary of history contents."""
        if self.records:
            recent_ops = [calc.operation for calc in self.records[-3:]]  # show last few ops
            preview = ", ".join(recent_ops)
        else:
            preview = "empty"
        return f"History(size={len(self.records)}, file='{self.file_path}', recent=[{preview}])"


# ==========================================================
# OBSERVER PATTERN IMPLEMENTATION
# ==========================================================
class HistoryObserver(ABC):
    """Abstract base class for all calculator observers."""

    @abstractmethod
    def update(self, calculation: Optional[Calculation]) -> None:
        """React to a new calculation event."""
        pass  # pragma: no cover


# ----------------------------------------------------------
# LoggingObserver — Reacts by Logging Calculations
# ----------------------------------------------------------
class LoggingObserver(HistoryObserver):
    """Logs calculation details to the configured logger."""

    def update(self, calculation: Optional[Calculation]) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")

        try:
            logging.info(
                f"Calculation performed: {calculation.operation} "
                f"({calculation.a}, {calculation.b}) = "
                f"{calculation.result}"
            )
        except Exception as e:
            logging.error(f"LoggingObserver failed to record calculation: {e}")
            raise RuntimeError(f"Logging failed: {e}") from e


# ----------------------------------------------------------
# AutoSaveObserver — Reacts by Persisting History
# ----------------------------------------------------------
class AutoSaveObserver(HistoryObserver):
    """Automatically saves history whenever a new calculation occurs."""

    def __init__(self, calculator: Any):
        if not hasattr(calculator, "config") or not hasattr(calculator, "save_history"):
            raise TypeError(
                "Calculator must have 'config' and 'save_history' attributes"
            )
        self.calculator = calculator

    def update(self, calculation: Optional[Calculation]) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")

        try:
            if getattr(self.calculator.config, "auto_save", False):
                self.calculator.save_history()
                logging.info("History auto-saved successfully.")
        except Exception as e:
            logging.error(f"AutoSaveObserver failed during save: {e}")
            raise RuntimeError(f"AutoSave failed: {e}") from e
