# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# File: app/exceptions.py
# ----------------------------------------------------------
# Description:
# Defines a structured exception hierarchy for the Enhanced Calculator.
# Each subclass targets a specific error domain such as input validation,
# configuration, operation failures, or history management.
# ----------------------------------------------------------


class CalculatorError(Exception):
    """Base class for all calculator-specific exceptions."""
    def __init__(self, message: str = "An unexpected calculator error occurred"):
        super().__init__(message)


class ValidationError(CalculatorError):
    """Raised when user input validation fails."""
    def __init__(self, message: str = "Invalid input provided"):
        super().__init__(message)


class OperationError(CalculatorError):
    """Raised when an arithmetic or logical operation fails."""
    def __init__(self, message: str = "Operation failed"):
        super().__init__(message)


class ConfigError(CalculatorError):
    """Raised when configuration (.env or precision settings) is invalid."""
    def __init__(self, message: str = "Configuration error"):
        super().__init__(message)


class HistoryError(CalculatorError):
    """Raised for persistence or history management issues."""
    def __init__(self, message: str = "History management error"):
        super().__init__(message)


__all__ = [
    "CalculatorError",
    "ValidationError",
    "OperationError",
    "ConfigError",
    "HistoryError",
]
