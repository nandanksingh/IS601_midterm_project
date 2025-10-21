# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/06/2025
# Assignment 5 - Enhanced Calculator (Memento Tests)
# ----------------------------------------------------------

import pytest
from datetime import datetime
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError


def test_memento_basic_serialization_deserialization():
    """Verify normal to_dict and from_dict behavior."""
    class DummyCalc:
        def to_dict(self):
            return {
                "operation": "Addition",
                "operand1": "1",
                "operand2": "2",
                "result": "3",
                "timestamp": datetime.now().isoformat(),
            }

    memento = CalculatorMemento(history=[DummyCalc()])
    data = memento.to_dict()
    restored = CalculatorMemento.from_dict(data)
    assert isinstance(restored, CalculatorMemento)
    assert len(restored.history) == 1
    assert isinstance(restored.timestamp, datetime)


def test_memento_to_dict_failure():
    """Force OperationError path when serialization fails."""
    class DummyCalc:
        def to_dict(self):
            raise OperationError("fake fail")

    memento = CalculatorMemento(history=[DummyCalc()])
    with pytest.raises(OperationError, match="fake fail"):
        memento.to_dict()


def test_memento_from_dict_inner_exception():
    """Expect OperationError when invalid structure is processed."""
    bad_data = {
        "history": [{"invalid_key": 123}],
        "timestamp": datetime.now().isoformat(),
    }
    with pytest.raises(OperationError):
        CalculatorMemento.from_dict(bad_data)


def test_memento_from_dict_outer_exception():
    """Trigger outer TypeError for invalid timestamp type."""
    bad_data = {"history": [], "timestamp": 123}
    with pytest.raises(TypeError):
        CalculatorMemento.from_dict(bad_data)
