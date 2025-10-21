# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/06/2025
# Assignment 5 - Enhanced Calculator
# ----------------------------------------------------------

########################
# Calculator Memento   #
########################

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from app.calculation import Calculation


@dataclass
class CalculatorMemento:
    """
    Stores calculator state for undo/redo functionality.

    This class uses the Memento design pattern to capture and restore
    the calculator's history. It helps implement undo and redo features
    by saving snapshots of the calculation history.
    """

    history: List[Calculation]  # List of past calculations
    timestamp: datetime = field(default_factory=datetime.now)  # When the snapshot was taken

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memento to a dictionary.

        This is useful for saving the state to a file or transmitting it.

        Returns:
            Dict[str, Any]: Serialized memento data.
        """
        return {
            "history": [calc.to_dict() for calc in self.history],
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculatorMemento':
        """
        Recreate a memento from a dictionary.

        This is useful for restoring a saved state from a file.

        Args:
            data (Dict[str, Any]): Serialized memento data.

        Returns:
            CalculatorMemento: Restored memento instance.
        """
        # Deserialize each calculation and restore timestamp
        restored_history = [Calculation.from_dict(calc) for calc in data.get("history", [])]
        restored_timestamp = datetime.fromisoformat(
            data.get("timestamp", datetime.now().isoformat())
        )
        return cls(history=restored_history, timestamp=restored_timestamp)
