# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# ----------------------------------------------------------
# Description:
# Core calculator class that coordinates all major functionalities:
# - Uses Factory Pattern to dynamically create operation instances
# - Employs Strategy Pattern for executing arithmetic logic
# - Utilizes Observer Pattern for logging and auto-save
# - Implements Memento Pattern for undo/redo history management
# ----------------------------------------------------------

import logging
import os
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Union
import pandas as pd

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import OperationFactory, Operation

Number = Union[int, float, Decimal]


class Calculator:
    """Main Calculator class implementing multiple design patterns."""

    def __init__(self, config: Optional[CalculatorConfig] = None):
        # Load configuration
        if config is None:
            project_root = Path(__file__).parent.parent
            config = CalculatorConfig(base_dir=project_root)

        self.config = config
        self.config.validate()

        # Setup environment
        os.makedirs(self.config.log_dir, exist_ok=True)
        self._setup_logging()
        self._setup_directories()

        # Initialize state variables
        self.history: List[Calculation] = []
        self.operation_strategy: Optional[Operation] = None
        self.observers: List[HistoryObserver] = []
        self.undo_stack: List[CalculatorMemento] = []
        self.redo_stack: List[CalculatorMemento] = []

        # Attempt to load saved history
        try:
            self.load_history()
        except Exception as e:
            logging.warning(f"Could not load existing history: {e}")

        logging.info("Calculator initialized successfully")

    # ------------------------------------------------------
    # Logging & Directory Setup
    # ------------------------------------------------------
    def _setup_logging(self) -> None:
        """Configure logging file and format."""
        try:
            os.makedirs(self.config.log_dir, exist_ok=True)
            log_file = self.config.log_file.resolve()
            logging.basicConfig(
                filename=str(log_file),
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                force=True,
            )
            logging.info(f"Logging initialized at: {log_file}")
        except Exception as e:
            print(f"Error setting up logging: {e}")
            raise

    def _setup_directories(self) -> None:
        """Ensure required directories exist."""
        self.config.history_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------
    # Observer Pattern
    # ------------------------------------------------------
    def add_observer(self, observer: HistoryObserver) -> None:
        """Register an observer (e.g., LoggingObserver, AutoSaveObserver)."""
        self.observers.append(observer)
        logging.info(f"Added observer: {observer.__class__.__name__}")

    def remove_observer(self, observer: HistoryObserver) -> None:
        """Unregister an observer."""
        self.observers.remove(observer)
        logging.info(f"Removed observer: {observer.__class__.__name__}")

    def notify_observers(self, calculation: Calculation) -> None:
        """Notify all observers of a new calculation event."""
        for observer in self.observers:
            try:
                observer.update(calculation)
            except Exception as e:
                logging.warning(f"Observer {observer} failed: {e}")

    # ------------------------------------------------------
    # Factory + Strategy Pattern
    # ------------------------------------------------------
    def set_operation(self, operation_name: str) -> None:
        """
        Select and create an operation strategy dynamically.
        Example: set_operation("power") or set_operation("divide")
        """
        try:
            self.operation_strategy = OperationFactory.create_operation(operation_name)
            logging.info(f"Set operation: {operation_name}")
        except ValueError as e:
            logging.error(f"Invalid operation: {e}")
            raise OperationError(str(e))

    # ------------------------------------------------------
    # Core Operation Execution
    # ------------------------------------------------------
    def perform_operation(self, a: Union[str, Number], b: Union[str, Number]) -> Decimal:
        """
        Validate inputs, perform selected operation, update history, and notify observers.
        """
        if not self.operation_strategy:
            raise OperationError("No operation set. Please select an operation first.")

        try:
            # Step 1: Validate numeric inputs
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)

            # Step 2: Execute the operation
            result = self.operation_strategy.execute(validated_a, validated_b)

            # Step 3: Record the calculation
            calculation = Calculation(
                operation=str(self.operation_strategy),
                operand1=validated_a,
                operand2=validated_b,
            )

            # Step 4: Save current state for undo/redo
            self.undo_stack.append(CalculatorMemento(self.history.copy()))
            self.redo_stack.clear()

            # Step 5: Update history
            self.history.append(calculation)
            if len(self.history) > self.config.max_history_size:
                self.history.pop(0)

            # Step 6: Notify observers
            self.notify_observers(calculation)

            logging.info(f"Performed operation: {calculation}")
            return result

        except ValidationError as e:
            logging.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Operation failed: {str(e)}")
            raise OperationError(f"Operation failed: {str(e)}")

    # ------------------------------------------------------
    # History Management (pandas-based)
    # ------------------------------------------------------
    def save_history(self) -> None:
        """Persist calculation history to a CSV file."""
        try:
            self.config.history_dir.mkdir(parents=True, exist_ok=True)
            history_data = [
                {
                    "operation": str(calc.operation),
                    "operand1": str(calc.operand1),
                    "operand2": str(calc.operand2),
                    "result": str(calc.result),
                    "timestamp": calc.timestamp.isoformat(),
                }
                for calc in self.history
            ]
            df = pd.DataFrame(
                history_data or [],
                columns=["operation", "operand1", "operand2", "result", "timestamp"],
            )
            df.to_csv(self.config.history_file, index=False)
            logging.info(f"History saved to {self.config.history_file}")
        except Exception as e:
            logging.error(f"Failed to save history: {e}")
            raise OperationError(f"Failed to save history: {e}")

    def load_history(self) -> None:
        """Load existing calculation history from CSV (if present)."""
        try:
            if self.config.history_file.exists():
                df = pd.read_csv(self.config.history_file)
                if not df.empty:
                    self.history = [
                        Calculation.from_dict(row.to_dict())
                        for _, row in df.iterrows()
                    ]
                    logging.info(f"Loaded {len(self.history)} past calculations.")
        except Exception as e:
            logging.error(f"Failed to load history: {e}")
            raise OperationError(f"Failed to load history: {e}")

    def get_history_dataframe(self) -> pd.DataFrame:
        """Return the full calculation history as a DataFrame."""
        data = [
            {
                "operation": str(calc.operation),
                "operand1": str(calc.operand1),
                "operand2": str(calc.operand2),
                "result": str(calc.result),
                "timestamp": calc.timestamp,
            }
            for calc in self.history
        ]
        return pd.DataFrame(data)

    def show_history(self):
        """Return a formatted list of past calculations."""
        return [
            f"{calc.operation}({calc.operand1}, {calc.operand2}) = {calc.result}"
            for calc in self.history
        ]

    def clear_history(self):
        """Clear current history and undo/redo stacks."""
        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        logging.info("History cleared successfully.")

    # ------------------------------------------------------
    # Undo / Redo (Memento Pattern)
    # ------------------------------------------------------
    def undo(self) -> bool:
        """Revert to the previous calculator state."""
        if not self.undo_stack:
            return False
        self.redo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = self.undo_stack.pop().get_state()
        logging.info("Undo performed.")
        return True

    def redo(self) -> bool:
        """Reapply the previously undone state."""
        if not self.redo_stack:
            return False
        self.undo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = self.redo_stack.pop().get_state()
        logging.info("Redo performed.")
        return True
