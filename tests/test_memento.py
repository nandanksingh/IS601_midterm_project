# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/21/2025
# Midterm Project: Enhanced Calculator (Memento Tests)
# File: tests/test_memento.py
# ----------------------------------------------------------
# Description:
# This module tests the Memento design pattern implementation.
# It validates both:
#   - CalculatorMemento (snapshot storage)
#   - Caretaker (undo/redo stack management)
#
# Test Coverage:
#   Serialization and deserialization
#   Undo/Redo functionality
#   Type and error validation
#   Stack clearing and state retrieval
# ----------------------------------------------------------

import pytest
from datetime import datetime
from decimal import Decimal
from app.calculator_memento import CalculatorMemento, Caretaker
from app.exceptions import OperationError, HistoryError


# ----------------------------------------------------------
# Helper Dummy Calculation Class
# ----------------------------------------------------------
class DummyCalc:
    """A dummy calculation class that mimics real Calculation behavior."""
    def __init__(self, operation="add", a="2", b="3", result="5"):
        self.operation = operation
        self.a = a
        self.b = b
        self.result = result
        self.timestamp = datetime.now()

    def to_dict(self):
        """Return a dictionary matching Calculation.to_dict() format."""
        return {
            "operation": self.operation,
            "a": str(self.a),
            "b": str(self.b),
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data):
        """Recreate DummyCalc from a dict (for deserialization tests)."""
        return cls(
            operation=data.get("operation", "unknown"),
            a=data.get("a", "0"),
            b=data.get("b", "0"),
            result=data.get("result", "0"),
        )


# ----------------------------------------------------------
# MEMENTO TESTS
# ----------------------------------------------------------
def test_memento_basic_serialization_deserialization(monkeypatch):
    """Verify CalculatorMemento serializes and deserializes correctly."""
    monkeypatch.setattr("app.calculation.Calculation", DummyCalc)
    memento = CalculatorMemento(history=[DummyCalc()])
    data = memento.to_dict()
    restored = CalculatorMemento.from_dict(data)
    assert isinstance(restored, CalculatorMemento)
    assert len(restored.history) == 1
    assert isinstance(restored.timestamp, datetime)


def test_memento_to_dict_raises_operationerror():
    """Ensure OperationError is raised when serialization fails."""
    class BadCalc:
        def to_dict(self):
            raise Exception("serialize fail")
    memento = CalculatorMemento(history=[BadCalc()])
    with pytest.raises(OperationError, match="Failed to serialize"):
        memento.to_dict()


def test_memento_from_dict_invalid_timestamp(monkeypatch):
    """Ensure invalid timestamp format raises OperationError."""
    monkeypatch.setattr("app.calculation.Calculation", DummyCalc)
    bad_data = {
        "history": [{"operation": "add", "a": "2", "b": "3", "result": "5"}],
        "timestamp": 123,  # invalid type
    }
    with pytest.raises(OperationError, match="deserialize"):
        CalculatorMemento.from_dict(bad_data)


def test_memento_get_state_returns_copy():
    """Ensure get_state() returns a new list copy of the history."""
    memento = CalculatorMemento(history=[DummyCalc()])
    state_copy = memento.get_state()
    assert state_copy is not memento.history
    assert state_copy[0].operation == "add"


# ----------------------------------------------------------
# CARETAKER TESTS
# ----------------------------------------------------------
def test_caretaker_save_and_current_state():
    """Validate state saving and retrieval."""
    caretaker = Caretaker()
    m1 = CalculatorMemento(history=[DummyCalc("add")])
    caretaker.save_state(m1)
    current = caretaker.current_state()
    assert isinstance(current, CalculatorMemento)
    assert current.history[0].operation == "add"
    assert "Undo" in caretaker.history_summary()


def test_caretaker_undo_and_redo():
    """Test undo and redo mechanics."""
    caretaker = Caretaker()
    m1 = CalculatorMemento(history=[DummyCalc("add")])
    m2 = CalculatorMemento(history=[DummyCalc("sub")])

    caretaker.save_state(m1)
    caretaker.save_state(m2)

    # Undo restores previous state
    prev = caretaker.undo()
    assert isinstance(prev, CalculatorMemento)
    assert prev.history[0].operation == "add"

    # Redo brings back last undone state
    redone = caretaker.redo()
    assert redone.history[0].operation == "sub"


def test_caretaker_no_undo_or_redo_raises():
    """Undo/Redo with empty stacks should raise HistoryError."""
    caretaker = Caretaker()
    with pytest.raises(HistoryError, match="undo"):
        caretaker.undo()
    with pytest.raises(HistoryError, match="redo"):
        caretaker.redo()


def test_caretaker_clear_resets_stacks():
    """Ensure clear() empties both Undo and Redo stacks."""
    caretaker = Caretaker()
    caretaker.save_state(CalculatorMemento(history=[DummyCalc()]))
    caretaker.clear()
    assert caretaker.current_state() is None
    assert "Undo" in caretaker.history_summary()


def test_caretaker_can_undo_and_redo_flags():
    """Validate boolean flags for undo/redo availability."""
    caretaker = Caretaker()
    m1 = CalculatorMemento(history=[DummyCalc()])
    m2 = CalculatorMemento(history=[DummyCalc("sub")])
    caretaker.save_state(m1)
    caretaker.save_state(m2)
    assert caretaker.can_undo() is True
    caretaker.undo()
    assert caretaker.can_redo() is True


def test_caretaker_repr_output():
    """Verify readable __repr__ output for debugging."""
    caretaker = Caretaker()
    caretaker.save_state(CalculatorMemento(history=[DummyCalc()]))
    rep = repr(caretaker)
    assert "Caretaker" in rep
    assert "undo=" in rep

# ----------------------------------------------------------
# EDGE TESTS 
# ----------------------------------------------------------

def test_memento_repr_output_contains_timestamp():
    """Covers __repr__ method in CalculatorMemento."""
    from app.calculator_memento import CalculatorMemento
    m = CalculatorMemento(history=[DummyCalc()])
    rep = repr(m)
    # Confirm output structure and content
    assert "CalculatorMemento" in rep
    assert "timestamp=" in rep
    assert str(len(m.history)) in rep


def test_caretaker_save_invalid_type_triggers_historyerror():
    """Covers invalid memento type branch in save_state()."""
    from app.calculator_memento import Caretaker, HistoryError
    caretaker = Caretaker()
    with pytest.raises(HistoryError, match="Invalid memento type"):
        caretaker.save_state("not_a_memento")
