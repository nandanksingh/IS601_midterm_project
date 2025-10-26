# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/21/2025
# Midterm Project: Enhanced Calculator (Memento Pattern)
# File: app/calculator_memento.py
# ----------------------------------------------------------
# Description:
# Implements the Memento design pattern to enable Undo/Redo
# functionality in the Enhanced Calculator.
#
# Participants:
#   - Originator: Calculator (creates and restores snapshots)
#   - Memento: CalculatorMemento (stores calculator state)
#   - Caretaker: Manages Undo/Redo stacks
#
# Responsibilities:
#   Save calculation history state
#   Restore previous states safely
#   Manage Undo and Redo operations
#   Serialize and deserialize calculator state
# ----------------------------------------------------------

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from copy import deepcopy
from app.calculation import Calculation
from app.exceptions import OperationError, HistoryError


# ----------------------------------------------------------
# MEMENTO CLASS
# ----------------------------------------------------------
@dataclass
class CalculatorMemento:
    """
    The Memento class encapsulates the calculator's internal state
    (i.e., its history of calculations) at a specific point in time.
    """

    history: List[Calculation]
    timestamp: datetime = field(default_factory=datetime.now)

    # ------------------------------------------------------
    # Serialization
    # ------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Convert the calculator state into a serializable dictionary."""
        try:
            serialized_history = [calc.to_dict() for calc in self.history]
            return {
                "history": serialized_history,
                "timestamp": self.timestamp.isoformat(),
            }
        except Exception as e:
            raise OperationError(f"Failed to serialize memento: {e}")

    # ------------------------------------------------------
    # Deserialization
    # ------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CalculatorMemento":
        """Rebuild a CalculatorMemento instance from a dictionary."""
        try:
            restored_history = [
                Calculation.from_dict(item) for item in data.get("history", [])
            ]
            ts_value = data.get("timestamp", datetime.now().isoformat())
            if not isinstance(ts_value, str):
                raise TypeError("Invalid timestamp format: must be string")
            return cls(
                history=restored_history,
                timestamp=datetime.fromisoformat(ts_value),
            )
        except Exception as e:
            raise OperationError(f"Failed to deserialize memento: {e}")

    # ------------------------------------------------------
    # Accessor
    # ------------------------------------------------------
    def get_state(self) -> List[Calculation]:
        """Return a shallow copy of stored calculation history."""
        return [calc for calc in self.history]

    def __repr__(self) -> str:
        """Readable debug format for logs."""
        return f"CalculatorMemento(len={len(self.history)}, timestamp={self.timestamp})"


# ----------------------------------------------------------
# CARETAKER CLASS
# ----------------------------------------------------------
class Caretaker:
    """
    The Caretaker class manages Undo and Redo operations using
    CalculatorMemento snapshots.
    """

    def __init__(self) -> None:
        self._undo_stack: List[CalculatorMemento] = []
        self._redo_stack: List[CalculatorMemento] = []

    # ------------------------------------------------------
    # Core Undo/Redo Operations
    # ------------------------------------------------------
    def save_state(self, memento: CalculatorMemento) -> None:
        """Save a new calculator state and clear redo stack."""
        if not isinstance(memento, CalculatorMemento):
            raise HistoryError("Invalid memento type.")
        self._undo_stack.append(deepcopy(memento))
        self._redo_stack.clear()

    def undo(self) -> Optional[CalculatorMemento]:
        """
        Undo the last operation by moving it to the redo stack.
        Returns the previous state or None if unavailable.
        """
        if not self._undo_stack:
            raise HistoryError("No state to undo.")
        last_state = self._undo_stack.pop()
        self._redo_stack.append(last_state)
        return deepcopy(self._undo_stack[-1]) if self._undo_stack else None

    def redo(self) -> Optional[CalculatorMemento]:
        """
        Redo the most recently undone operation.
        Returns the restored state or None if unavailable.
        """
        if not self._redo_stack:
            raise HistoryError("No state to redo.")
        restored_state = self._redo_stack.pop()
        self._undo_stack.append(restored_state)
        return deepcopy(restored_state)

    def current_state(self) -> Optional[CalculatorMemento]:
        """Return the current calculator state without altering stacks."""
        return deepcopy(self._undo_stack[-1]) if self._undo_stack else None

    def clear(self) -> None:
        """Completely reset both Undo and Redo stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    # ------------------------------------------------------
    # Helper Properties
    # ------------------------------------------------------
    def can_undo(self) -> bool:
        """Return True if Undo is possible."""
        return len(self._undo_stack) > 1

    def can_redo(self) -> bool:
        """Return True if Redo is possible."""
        return len(self._redo_stack) > 0

    def history_summary(self) -> str:
        """Return readable summary of Undo/Redo stacks."""
        return f"Undo: {len(self._undo_stack)} | Redo: {len(self._redo_stack)}"

    def __repr__(self) -> str:
        """Readable internal representation."""
        return f"Caretaker(undo={len(self._undo_stack)}, redo={len(self._redo_stack)})"
