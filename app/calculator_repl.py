# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator (REPL Interface)
# ----------------------------------------------------------
# Description:
# Implements the command-line REPL for the calculator.
# Supports operations via Factory + Strategy patterns, along with
# history management (undo/redo/save/load) and graceful error handling.
# Color-coded outputs.
# ----------------------------------------------------------

import sys
from colorama import Fore, Style, init
from app.exceptions import OperationError, ValidationError

# Initialize colorama for colored console output
init(autoreset=True)


# ----------------------------------------------------------
# Helper functions for colored messages
# ----------------------------------------------------------
def success(msg):
    print(Fore.GREEN + msg + Style.RESET_ALL)

def info(msg):
    print(Fore.CYAN + msg + Style.RESET_ALL)

def warn(msg):
    print(Fore.YELLOW + msg + Style.RESET_ALL)

def error(msg):
    print(Fore.RED + msg + Style.RESET_ALL)


def safe_import_calculator():
    """
    Safely import Calculator inside function.
    This avoids recursive mock failures during pytest.
    """
    from app.calculator import Calculator
    return Calculator


# ----------------------------------------------------------
# Command Execution
# ----------------------------------------------------------
def _perform_command(calc, command, input_func=input):
    """Execute a single command using the calculator instance."""
    try:
        # ------------------------------------------------------
        # Arithmetic Commands (10 total)
        # ------------------------------------------------------
        if command in (
            "add", "subtract", "multiply", "divide",
            "power", "root", "modulus", "int_divide",
            "percent", "abs_diff"
        ):
            info("\nEnter numbers (or 'cancel' to abort):")

            num1 = input_func(Fore.YELLOW + "First number: " + Style.RESET_ALL).strip()
            if num1.lower() == "cancel":
                warn("Operation cancelled.")
                return True

            num2 = input_func(Fore.YELLOW + "Second number: " + Style.RESET_ALL).strip()
            if num2.lower() == "cancel":
                warn("Operation cancelled.")
                return True

            calc.set_operation(command)
            result = calc.perform_operation(num1, num2)
            success(f"Result: {result}")
            return True

        # ------------------------------------------------------
        # History & Maintenance Commands
        # ------------------------------------------------------
        elif command == "history":
            hist = calc.show_history()
            if not hist:
                warn("No calculations yet.")
            else:
                info("\nCalculation History:")
                for entry in hist:
                    print(Fore.WHITE + f"  {entry}" + Style.RESET_ALL)
            return True

        elif command == "clear":
            calc.clear_history()
            warn("History cleared.")
            return True

        elif command == "undo":
            msg = "Operation undone." if calc.undo() else "Nothing to undo."
            info(msg)
            return True

        elif command == "redo":
            msg = "Operation redone." if calc.redo() else "Nothing to redo."
            info(msg)
            return True

        # ------------------------------------------------------
        # Persistence Commands
        # ------------------------------------------------------
        elif command == "save":
            try:
                calc.save_history()
                success("History saved successfully.")
            except Exception as e:
                error(f"Error saving history: {e}")
            return True

        elif command == "load":
            try:
                calc.load_history()
                success("History loaded successfully.")
            except Exception as e:
                error(f"Error loading history: {e}")
            return True

        # ------------------------------------------------------
        # Help & Exit
        # ------------------------------------------------------
        elif command == "help":
            info("""
Available commands:
  add, subtract, multiply, divide, power, root,
  modulus, int_divide, percent, abs_diff - Perform calculations

  history  - Show calculation history
  clear    - Clear calculation history
  undo     - Undo last calculation
  redo     - Redo last undone calculation
  save     - Save history to file
  load     - Load history from file
  help     - Show this help menu
  exit     - Exit the calculator
""")
            return True

        elif command == "exit":
            try:
                calc.save_history()
                warn("Goodbye!")
            except Exception as e:
                error(f"Warning: Failed to save history: {e}")
            return False

        # ------------------------------------------------------
        # Unknown Command Handling
        # ------------------------------------------------------
        else:
            error(f"Unknown command: {command}")
            return True

    # ------------------------------------------------------
    # Error Handling (Validation, Operation, or General)
    # ------------------------------------------------------
    except ValidationError as e:
        error(f"Validation Error: {e}")
    except OperationError as e:
        error(f"Operation Error: {e}")
    except Exception as e:
        error(f"Unexpected Error: {e}")
    return True


# ----------------------------------------------------------
# REPL Loop
# ----------------------------------------------------------
def calculator_repl(input_func=input):
    """Main REPL loop for interactive calculator usage."""
    try:
        Calculator = safe_import_calculator()
        calc = Calculator()
        info("Calculator started. Type 'help' for commands.")

        while True:
            try:
                cmd = input_func(Fore.YELLOW + "\nEnter command: " + Style.RESET_ALL).strip().lower()
                if not _perform_command(calc, cmd, input_func):
                    break
            except KeyboardInterrupt:
                warn("\nOperation cancelled (Ctrl+C). Exiting REPL safely.")
                break
            except EOFError:
                warn("\nInput terminated (Ctrl+D). Exiting...")
                break
            except Exception as e:
                error(f"Unexpected error in REPL: {e}")
                continue

    except Exception as e:
        # Handle fatal initialization errors
        error(f"Fatal error: {e}")
        return


if __name__ == "__main__":
    try:
        calculator_repl()
    except Exception:
        sys.exit(1)
