# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/20/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# File: app/calculator.py
# ----------------------------------------------------------
# Description:
# The Calculator class serves as the core controller that integrates:
#   • Factory Pattern → Operation creation via OperationFactory
#   • Memento Pattern → Undo/Redo support for history state
#   • Observer Pattern → Logging and AutoSave behaviors
#   • Persistent History Management → CSV-based data storage
#
# Responsibilities:
#   Evaluate and execute user operations
#   Manage History, Mementos, and Observers
#   Implement undo/redo logic
#   Integrate Calculation + OperationFactory
#   Trigger auto-save and logging through observers
#   Provide REPL-compatible operation interface (set_operation, perform_operation)
# ----------------------------------------------------------

import logging
from decimal import Decimal
from pathlib import Path
from typing import List, Optional
import pandas as pd

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.history import LoggingObserver, AutoSaveObserver
from app.exceptions import OperationError, HistoryError
from app.calculation import CalculationFactory


# ----------------------------------------------------------
# Calculator Controller
# ----------------------------------------------------------
class Calculator:
    """Main calculator controller implementing Factory, Memento, and Observer patterns."""

    def __init__(self, config: Optional[CalculatorConfig] = None):
        # Initialize configuration and ensure directories exist
        self.config = config or CalculatorConfig()
        self.config.validate()

        Path(self.config.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.history_dir).mkdir(parents=True, exist_ok=True)

        self._setup_logging()

        # Core components
        self.history: List[Calculation] = []
        self.undo_stack: List[CalculatorMemento] = []
        self.redo_stack: List[CalculatorMemento] = []
        self.observers = [
            LoggingObserver(),
            AutoSaveObserver(self),
        ]

        # REPL-compatible attribute
        self.current_operation: Optional[str] = None

        # Attempt to load history
        try:
            self.load_history()
        except Exception as e:
            logging.warning(f"History load skipped: {e}")

        logging.info("Calculator initialized successfully.")

    # ------------------------------------------------------
    # Setup & Initialization
    # ------------------------------------------------------
    def _setup_logging(self) -> None:
        """Initialize logging configuration."""
        try:
            logging.basicConfig(
                filename=str(self.config.log_file),
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                force=True,
            )
            logging.info("Logging setup complete.")
        except Exception as e:
            raise HistoryError(f"Logging setup failed: {e}")

    # ------------------------------------------------------
    # REPL Compatibility
    # ------------------------------------------------------
    def set_operation(self, operation_name: str) -> None:
        """Store the current operation name for REPL usage."""
        self.current_operation = operation_name.lower()
    
    def perform_operation(self, a, b) -> Decimal:
        """Perform arithmetic using the currently selected operation (REPL-safe)."""
        if not self.current_operation:
            raise OperationError("No operation selected.")

        try:
            # Convert REPL input (strings) into Decimals safely
            a_dec = Decimal(str(a))
            b_dec = Decimal(str(b))
            result = self.calculate(self.current_operation, a_dec, b_dec).result
            return result

        except Exception as e:
            # Wrap any numeric or factory-level errors in a uniform message
            raise OperationError(f"Operation failed: {e}")


    # ------------------------------------------------------
    # Factory Pattern – Arithmetic Execution
    # ------------------------------------------------------
    def calculate(self, operation: str, a: Decimal, b: Decimal) -> Calculation:
        """Perform an arithmetic operation using the registered factory."""
        try:
            func = CalculationFactory.operations.get(operation.lower())
            if not func:
                raise OperationError(f"Unknown operation: {operation}")

            result = func(a, b)
            calc = Calculation(operation, a, b)
            self.history.append(calc)

            # Maintain bounded history
            if len(self.history) > self.config.max_history_size:
                self.history.pop(0)

            self._save_memento()
            self._notify_observers(calc)

            logging.info(f"Operation performed successfully: {calc}")
            return calc

        except OperationError:
            raise
        except Exception as e:
            raise OperationError(f"Operation failed: {e}")

    # ------------------------------------------------------
    # History Management (Persistence)
    # ------------------------------------------------------
    def save_history(self) -> None:
        """Save all calculations to a CSV file."""
        try:
            data = [calc.to_dict() for calc in self.history]
            df = pd.DataFrame(data)
            df.to_csv(self.config.history_file, index=False)
            logging.info(f"History saved → {self.config.history_file}")
        except Exception as e:
            raise HistoryError(f"Failed to save history: {e}")

    def load_history(self) -> None:
        """Load previous calculations from the CSV file (if exists)."""
        try:
            file_path = Path(self.config.history_file)
            if not file_path.exists():
                logging.info("No previous history file found.")
                return

            df = pd.read_csv(file_path)
            if not df.empty:
                self.history = [
                    Calculation.from_dict(row.to_dict())
                    for _, row in df.iterrows()
                ]
                logging.info(f"Loaded {len(self.history)} records from history.")
        except Exception as e:
            raise HistoryError(f"Failed to load history: {e}")

    def clear_history(self) -> None:
        """Erase all stored history and mementos."""
        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        logging.info("🧹 History cleared.")

    def list_history(self) -> List[str]:
        """Return formatted strings of all stored calculations."""
        return [str(calc) for calc in self.history]

    # ------------------------------------------------------
    # Memento Pattern – Undo/Redo Logic
    # ------------------------------------------------------
    def _save_memento(self) -> None:
        """Save current state for undo/redo functionality."""
        snapshot = CalculatorMemento(self.history.copy())
        self.undo_stack.append(snapshot)
        self.redo_stack.clear()
        logging.debug("Memento snapshot saved.")

    def undo(self) -> None:
        """Revert to previous state."""
        if not self.undo_stack:
            raise HistoryError("Nothing to undo.")
        self.redo_stack.append(CalculatorMemento(self.history.copy()))
        snapshot = self.undo_stack.pop()
        self.history = snapshot.get_state()
        logging.info("Undo performed.")

    def redo(self) -> None:
        """Reapply a previously undone state."""
        if not self.redo_stack:
            raise HistoryError("Nothing to redo.")
        self.undo_stack.append(CalculatorMemento(self.history.copy()))
        snapshot = self.redo_stack.pop()
        self.history = snapshot.get_state()
        logging.info("Redo performed.")

    # ------------------------------------------------------
    # Observer Pattern
    # ------------------------------------------------------
    def _notify_observers(self, calculation: Calculation) -> None:
        """Notify all observers when a new calculation is completed."""
        for observer in self.observers:
            try:
                observer.update(calculation)
            except Exception as e:
                logging.warning(f"Observer {observer} failed: {e}")

    def add_observer(self, observer) -> None:
        """Register a new observer."""
        self.observers.append(observer)
        logging.info(f"Observer added: {observer.__class__.__name__}")

    def remove_observer(self, observer) -> None:
        """Unregister an observer."""
        self.observers.remove(observer)
        logging.info(f"Observer removed: {observer.__class__.__name__}")

    # ------------------------------------------------------
    # Representation
    # ------------------------------------------------------
    def __repr__(self) -> str:
        """Readable object representation."""
        return f"<Calculator with {len(self.history)} records>"
