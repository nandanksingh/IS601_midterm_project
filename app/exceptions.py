# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project: Enhanced Calculator Command-Line Application (Exception Hierarchy)
# ----------------------------------------------------------
# Description:
# Defines a clear and extensible exception hierarchy for the calculator.
# Enables unified, meaningful, and precise error handling across modules.
# ----------------------------------------------------------

class CalculatorError(Exception):
    """
    Base exception class for calculator-specific errors.

    All custom exceptions for the calculator application inherit from this class,
    allowing unified error handling and consistent messaging across the project.
    """
    pass


class ValidationError(CalculatorError):
    """
    Raised when input validation fails.

    Triggered when user inputs are not numeric, exceed allowed limits,
    or violate validation constraints.
    """
    pass


class OperationError(CalculatorError):
    """
    Raised when a calculation operation fails.

    Used for arithmetic failures such as division by zero, undefined operations,
    or data-related issues during computation.
    """
    pass


class ConfigurationError(CalculatorError):
    """
    Raised when calculator configuration is invalid.

    Occurs when environment variables, file paths, or configuration parameters
    are missing or set incorrectly.
    """
    pass
