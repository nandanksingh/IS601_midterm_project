# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator (Memento Pattern)
# ----------------------------------------------------------
# Description:
# This module implements the Memento design pattern to enable
# undo and redo functionality in the calculator.
#
# The CalculatorMemento class captures the internal state
# (i.e., the calculation history) of the Calculator at a given
# time, so it can be restored later without violating encapsulation.
#
# Key Responsibilities:
# - Save the current list of calculations into a serializable snapshot
# - Restore calculator state from a saved snapshot
# - Handle serialization and deserialization errors gracefully
#
# Design Pattern: Memento
# Participants:
#   - Originator: Calculator (creates and restores mementos)
#   - Memento: CalculatorMemento (stores calculator state)
#   - Caretaker: Undo/Redo stack in Calculator (manages mementos)
# ----------------------------------------------------------

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from app.calculation import Calculation
from app.exceptions import OperationError


@dataclass
class CalculatorMemento:
    """
    The Memento class encapsulates the Calculator's internal state
    (its history of calculations) so that it can be restored later.
    """

    # The list of calculations at the time the snapshot was taken
    history: List[Calculation]

    # Timestamp of when this snapshot was created
    timestamp: datetime = field(default_factory=datetime.now)

    # ------------------------------------------------------
    # Serialization Logic
    # ------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the current calculator state into a serializable dictionary.

        Returns:
            dict: Contains serialized history and timestamp.

        Raises:
            OperationError: If any calculation in the history
                            cannot be serialized properly.
        """
        try:
            serialized_history = []
            for calc in self.history:
                try:
                    serialized_history.append(calc.to_dict())
                except Exception as e:
                    # Propagate the serialization issue as OperationError
                    raise OperationError(str(e))

            return {
                "history": serialized_history,
                "timestamp": self.timestamp.isoformat(),
            }

        except Exception as e:
            raise OperationError(f"Failed to serialize memento: {e}")

    # ------------------------------------------------------
    # Deserialization Logic
    # ------------------------------------------------------

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CalculatorMemento":
        """
        Recreate a CalculatorMemento instance from serialized data.

        Args:
            data (dict): Dictionary containing 'history' and 'timestamp'.

        Returns:
            CalculatorMemento: Fully restored memento object.

        Raises:
            OperationError: If the history data cannot be deserialized.
            TypeError: If the timestamp is not a valid string format.
        """
        try:
            # Rebuild history safely
            restored_history = []
            for item in data.get("history", []):
                try:
                    restored_history.append(Calculation.from_dict(item))
                except Exception as e:
                    raise OperationError(f"Invalid history data: {e}")

            # Validate timestamp
            ts_value = data.get("timestamp", datetime.now().isoformat())
            if not isinstance(ts_value, str):
                raise TypeError("Invalid timestamp format: must be string")

            restored_timestamp = datetime.fromisoformat(ts_value)
            return cls(history=restored_history, timestamp=restored_timestamp)

        except OperationError:
            raise  # Pass through known OperationError
        except TypeError:
            raise  # Pass through known TypeError
        except Exception as e:
            # Handle unexpected deserialization errors
            raise OperationError(f"Failed to deserialize memento: {e}")

    # ------------------------------------------------------
    # Accessor Method
    # ------------------------------------------------------

    def get_state(self) -> List[Calculation]:
        """
        Retrieve a copy of the stored calculation history.

        This ensures the caller cannot modify the original state
        stored in the memento directly.

        Returns:
            list: A copy of the calculator's past calculations.
        """
        return [calc for calc in self.history]
