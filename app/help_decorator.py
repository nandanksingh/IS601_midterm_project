# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/24/2025
# Midterm Project - Enhanced Calculator
# File: app/help_decorator.py
# ----------------------------------------------------------
# Description:
# Implements the Decorator Design Pattern for dynamic help menu
# generation in the Enhanced Calculator REPL.
#
# The pattern allows new operations to be automatically reflected
# in the help menu without changing the REPL logic.
# ----------------------------------------------------------

class HelpBase:
    """Base class defining the structure of the help system."""

    def show_help(self) -> str:
        """Return default help text."""
        return (
            "\nAvailable Commands:\n"
            "  add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff\n"
            "  undo, redo, history, clear\n"
            "  save, load, help, exit"
        )


class HelpDecorator:
    """Decorator class that dynamically extends the help menu."""

    def __init__(self, base_help: HelpBase):
        self._base_help = base_help

    def show_help(self) -> str:
        """Enhance base help text with decorator message."""
        base_text = self._base_help.show_help()
        return base_text + "\n\n(Hint: New operations added automatically via Decorator Pattern )"
