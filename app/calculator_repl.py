# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/06/2025
# Assignment 5 - Enhanced Calculator (REPL)
# ----------------------------------------------------------

import sys
from app.operations import OperationFactory
from app.exceptions import OperationError, ValidationError

# Import inside function for safety to avoid recursive mock crash
def safe_import_calculator():
    """Safely import Calculator even if module patched during tests."""
    from app.calculator import Calculator
    return Calculator


def _perform_command(calc, command, input_func=input):
    """Execute a single command using the calculator instance."""
    try:
        # Arithmetic commands
        if command in ("add", "subtract", "multiply", "divide", "power", "root"):
            print("\nEnter numbers (or 'cancel' to abort):")
            num1 = input_func("First number: ").strip()
            if num1.lower() == "cancel":
                print("Operation cancelled.")
                return True

            num2 = input_func("Second number: ").strip()
            if num2.lower() == "cancel":
                print("Operation cancelled.")
                return True

            calc.set_operation(OperationFactory.create_operation(command))
            result = calc.perform_operation(num1, num2)
            print(f"Result: {result}")
            return True

        # History / Maintenance
        elif command == "history":
            hist = calc.show_history()
            if not hist:
                print("No calculations yet.")
            else:
                print("\nCalculation History:")
                for entry in hist:
                    print(f"  {entry}")
            return True

        elif command == "clear":
            calc.clear_history()
            print("History cleared.")
            return True

        elif command == "undo":
            print("Operation undone." if calc.undo() else "Nothing to undo.")
            return True

        elif command == "redo":
            print("Operation redone." if calc.redo() else "Nothing to redo.")
            return True

        # Persistence
        elif command == "save":
            try:
                calc.save_history()
                print("History saved successfully.")
            except Exception as e:
                print(f"Error saving history: {e}")
            return True

        elif command == "load":
            try:
                calc.load_history()
                print("History loaded successfully.")
            except Exception as e:
                print(f"Error loading history: {e}")
            return True

        # Help / Exit
        elif command == "help":
            print("""
Available commands:
  add, subtract, multiply, divide, power, root - Perform calculations
  history - Show calculation history
  clear - Clear calculation history
  undo - Undo the last calculation
  redo - Redo the last undone calculation
  save - Save calculation history to file
  load - Load calculation history from file
  exit - Exit the calculator
""")
            return True

        elif command == "exit":
            try:
                calc.save_history()
                print("Goodbye!")
            except Exception as e:
                print(f"Warning: Failed to save history: {e}")
            return False

        else:
            print(f"Unknown command: {command}")
            return True

    except ValidationError as e:
        print(f"Error: {e}")
    except OperationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return True


def calculator_repl(input_func=input):
    """Main REPL loop for calculator — safe against mock recursion and fatal init errors."""
    try:
        Calculator = safe_import_calculator()
        calc = Calculator()
        print("Calculator started. Type 'help' for commands.")

        while True:
            try:
                cmd = input_func("\nEnter command: ").strip().lower()
                if not _perform_command(calc, cmd, input_func):
                    break
            except KeyboardInterrupt:
                print("\nOperation cancelled (Ctrl+C). Exiting REPL safely.")
                break
            except EOFError:
                print("\nInput terminated (Ctrl+D). Exiting...")
                break
            except Exception as e:
                print(f"Unexpected error in REPL: {e}")
                continue

    except Exception as e:
        # Handle fatal init errors cleanly — do not re-raise to avoid pytest segfault
        print(f"Fatal error: {e}")
        return  # exit gracefully


if __name__ == "__main__":
    try:
        calculator_repl()
    except Exception:
        sys.exit(1)
