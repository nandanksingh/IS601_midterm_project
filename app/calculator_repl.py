# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/25/2025
# Midterm Project - Enhanced Calculator (REPL Interface)
# File: app/calculator_repl.py
# ----------------------------------------------------------
# Description:
# Provides the interactive Read–Eval–Print Loop (REPL)
# for the Enhanced Calculator application.
#
# Features:
#  • Executes arithmetic and utility commands
#  • Dynamic help menu (Decorator Pattern)
#  • Color-coded outputs (using colorama)
#  • Clean, user-friendly prompts with cancel/exit options
#  • Graceful handling of keyboard and input errors
# ----------------------------------------------------------

import sys
from decimal import Decimal
from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError 
from app.help_decorator import HelpBase, HelpDecorator


# ----------------------------------------------------------
# Optional Color Support Setup
# ----------------------------------------------------------
def _load_colorama():
    """Safely import colorama for colored terminal output."""
    try:
        from colorama import init, Fore, Style
        init(autoreset=True)
        return Fore, Style
    except ImportError:
        # Fallback to None if colorama is not installed
        return None, None


# Load colorama palette safely
Fore, Style = _load_colorama()


# ----------------------------------------------------------
# Helper: Color print wrapper
# ----------------------------------------------------------
def cprint(text: str, color: str = "white") -> None:
    """Print text with color when available, fallback to plain output."""
    if Fore and Style:
        palette = {
            "green": Fore.GREEN,
            "red": Fore.RED,
            "yellow": Fore.YELLOW,
            "cyan": Fore.CYAN,
            "white": Fore.WHITE,
        }
        print(palette.get(color, Fore.WHITE) + text + Style.RESET_ALL)
    else:
        print(text)


# ----------------------------------------------------------
# Perform a single command
# ----------------------------------------------------------
def _perform_command(calculator: Calculator, command: str) -> bool:
    """Execute one REPL command safely and handle exceptions."""
    try:
        command = command.lower().strip()

        # Exit command
        if command in {"exit", "quit", "q"}:
            try:
                calculator.save_history()
            except Exception:
                pass  # Ignore save errors during exit
            cprint("Exiting the calculator. Goodbye!", "yellow")
            return False

        # Dynamic Help (Decorator Pattern)
        elif command == "help":
            help_menu = HelpDecorator(HelpBase())
            cprint("\nDynamic Help Menu (Decorator Pattern Enabled):", "cyan")
            cprint(help_menu.show_help(), "white")
            return True

        # History display
        elif command == "history":
            history = calculator.list_history()
            if not history:
                cprint("\nNo calculations yet.", "yellow")
            else:
                cprint("\nCalculation History:", "cyan")
                for record in history:
                    print(" ", record)
            return True

        # Undo / Redo
        elif command == "undo":
            calculator.undo()
            cprint("Undo successful.", "yellow")
            return True
        elif command == "redo":
            calculator.redo()
            cprint("Redo successful.", "yellow")
            return True

        # Clear
        elif command == "clear":
            calculator.clear_history()
            cprint("History cleared.", "yellow")
            return True

        # Save / Load
        elif command == "save":
            calculator.save_history()
            cprint("History saved successfully.", "green")
            return True
        elif command == "load":
            calculator.load_history()
            cprint("History loaded successfully.", "green")
            return True

        # Arithmetic Commands
        elif command in [
            "add", "subtract", "multiply", "divide",
            "power", "root", "modulus", "int_divide",
            "percent", "abs_diff"
        ]:
            print("\n(Press Enter without typing or 'cancel' to return to main menu)\n")
            a = input("Enter first number: ").strip()
            if not a or a.lower() == "cancel":
                cprint("Operation cancelled.", "yellow")
                return True

            b = input("Enter second number: ").strip()
            if not b or b.lower() == "cancel":
                cprint("Operation cancelled.", "yellow")
                return True

            # Convert to Decimal for precision
            try:
                a_val, b_val = Decimal(a), Decimal(b)
            except Exception:
                raise ValidationError("Invalid numeric input.")

            calc = calculator.calculate(command, a_val, b_val)
            cprint(f"Result: {calc.result}", "green")
            return True

        # Unknown Command
        else:
            cprint(f"Unknown command: '{command}'", "red")
            return True

    # ------------------------------------------------------
    # Error Handling (fully covered by tests)
    # ------------------------------------------------------
    except ValidationError as ve:
        cprint(f"Validation Error: {ve}", "red")
        return True
    except OperationError as oe:
        cprint(f"Operation Error: {oe}", "red")
        return True
    except Exception as e:
        # Last-resort safety for unexpected conditions
        cprint(f"Unexpected error: {e}", "red")
        return True


# ----------------------------------------------------------
# Main REPL Loop
# ----------------------------------------------------------
def calculator_repl(input_func=input) -> None:
    """Main Read–Eval–Print loop for interactive calculator."""
    calculator = Calculator()

    cprint("Welcome to the Enhanced Calculator!", "cyan")
    print("Type 'help' to see available commands.\n")

    while True:
        try:
            command = input_func("Enter command: ").strip()
            if not command:
                continue
            proceed = _perform_command(calculator, command)
            if not proceed:
                break
        except KeyboardInterrupt:
            cprint("\nKeyboard interrupt. Exiting.", "yellow")
            break
        except EOFError:
            cprint("\nInput closed. Exiting.", "yellow")
            break
        except Exception as e:
            # Fallback for fatal/unexpected REPL errors
            cprint(f"\nFatal REPL error: {e}", "red")
            break


