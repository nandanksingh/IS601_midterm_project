# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator (Memento Tests)
# ----------------------------------------------------------
# Description:
# This test module validates the functionality of the
# CalculatorMemento class which is responsible for storing
# and restoring the calculator's internal history state.
#
# The tests verify:
#   1. Correct serialization and deserialization
#   2. Proper handling of exceptions during save/restore
#   3. Type validation for timestamps
#
# Framework: pytest
# ----------------------------------------------------------

import pytest
from datetime import datetime
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError


# ----------------------------------------------------------
# Test Case 1: Basic Serialization and Deserialization
# ----------------------------------------------------------

def test_memento_basic_serialization_deserialization():
    """
    Verify that a CalculatorMemento can be serialized into a
    dictionary and restored back to a valid instance.
    """
    class DummyCalc:
        def to_dict(self):
            # Mimic a real Calculation object
            return {
                "operation": "Addition",
                "operand1": "1",
                "operand2": "2",
                "result": "3",
                "timestamp": datetime.now().isoformat(),
            }

    # Create memento and serialize it
    memento = CalculatorMemento(history=[DummyCalc()])
    data = memento.to_dict()

    # Deserialize and verify structure
    restored = CalculatorMemento.from_dict(data)
    assert isinstance(restored, CalculatorMemento)
    assert len(restored.history) == 1
    assert isinstance(restored.timestamp, datetime)


# ----------------------------------------------------------
# Test Case 2: to_dict() Exception Handling
# ----------------------------------------------------------

def test_memento_to_dict_failure():
    """
    Ensure that an OperationError is raised if a calculation
    cannot be serialized properly.
    """
    class DummyCalc:
        def to_dict(self):
            # Simulate failure inside to_dict
            raise OperationError("fake fail")

    memento = CalculatorMemento(history=[DummyCalc()])

    # Expect OperationError to propagate
    with pytest.raises(OperationError, match="fake fail"):
        memento.to_dict()


# ----------------------------------------------------------
# Test Case 3: from_dict() with Invalid History
# ----------------------------------------------------------

def test_memento_from_dict_inner_exception():
    """
    Validate that an invalid or corrupt history structure raises
    an OperationError during deserialization.
    """
    bad_data = {
        "history": [{"invalid_key": 123}],  # Missing expected keys
        "timestamp": datetime.now().isoformat(),
    }

    # Should raise OperationError due to malformed data
    with pytest.raises(OperationError):
        CalculatorMemento.from_dict(bad_data)


# ----------------------------------------------------------
# Test Case 4: from_dict() with Invalid Timestamp
# ----------------------------------------------------------

def test_memento_from_dict_outer_exception():
    """
    Confirm that a non-string timestamp raises a TypeError
    during memento restoration.
    """
    bad_data = {"history": [], "timestamp": 123}  # Invalid type

    with pytest.raises(TypeError):
        CalculatorMemento.from_dict(bad_data)
