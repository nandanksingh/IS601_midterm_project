# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project - Enhanced Calculator (Main Entry Point)
# ----------------------------------------------------------
# Description:
# This is the main entry point for the Enhanced Calculator application.
# It launches the interactive REPL (Read–Eval–Print Loop) interface,
# allowing users to perform advanced arithmetic operations with features like:
#   - Undo/Redo
#   - History saving and loading
#   - Input validation and error handling
#   - Observer and Memento pattern integration
#
# This file acts as the glue connecting all calculator modules together:
#   calculator_repl.py → Handles user interaction (REPL)
#   calculator.py      → Core business logic and state management
#   operations.py      → Operation factory and strategy classes
#   input_validators.py→ Input validation and sanitization
#   history.py         → Persistence and observer pattern
#   logger.py          → Logging and tracing
#
# Running this file directly starts the calculator REPL session.
# ----------------------------------------------------------

from app.calculator_repl import calculator_repl


# ----------------------------------------------------------
# Main Application Entry Point
# ----------------------------------------------------------
if __name__ == "__main__":
    print("Starting Enhanced Calculator...\n")
    calculator_repl()
    print("\nCalculator session closed. Goodbye!")
