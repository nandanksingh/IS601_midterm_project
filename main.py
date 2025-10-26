# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/18/2025
# Midterm Project - Enhanced Calculator (Main Entry Point)
# File: main.py
# ----------------------------------------------------------
# Description:
# This is the main entry point for the Enhanced Calculator application.
# It launches the interactive REPL (Read–Eval–Print Loop) interface,
# allowing users to perform advanced arithmetic operations with features like:
#   • Undo / Redo
#   • History saving and loading
#   • Input validation and error handling
#   • Observer and Memento pattern integration
#
# Acts as the glue connecting all calculator modules:
#   app/calculator_repl.py   → Handles user interaction (REPL)
#   app/calculator.py        → Core business logic and state management
#   app/operations.py        → Operation factory and strategy classes
#   app/input_validators.py  → Input validation and sanitization
#   app/history.py           → Persistence and observer pattern
#   app/logger.py            → Logging and tracing
#
# Running this file directly starts the calculator REPL session.
# ----------------------------------------------------------

from app.calculator_repl import calculator_repl


# ----------------------------------------------------------
# Main Application Entry Point
# ----------------------------------------------------------
if __name__ == "__main__":
    try:
        print("Starting Enhanced Calculator...\n")
        calculator_repl()
        print("\nCalculator session closed. Goodbye!")
    except KeyboardInterrupt:
        print("\nSession terminated by user. Exiting gracefully...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        raise
