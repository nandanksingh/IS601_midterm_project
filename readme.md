# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/21/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# ----------------------------------------------------------

## Overview

The **Enhanced Calculator** is a command-line application developed in Python that demonstrates the practical use of **object-oriented programming (OOP)** and **software design patterns**.
This project extends a simple calculator into a full-featured, modular, and interactive program capable of performing a wide range of mathematical operations with data persistence and automated testing.

It incorporates several core design patterns — **Factory**, **Memento**, and **Observer** — to manage operations, history, and state changes efficiently.
Additionally, it includes two advanced enhancements that make the program both dynamic and user-friendly:

1. A **Dynamic Help Menu** using the **Decorator Pattern**, and
2. **Color-Coded Output** using the **Colorama** library.

Together, these features provide a professional and maintainable foundation for Python application development with CI/CD integration and full unit testing.

---

## Key Features

### Core Functionalities

* **Factory Pattern:** Dynamically generates operation objects (Add, Subtract, Multiply, etc.) without changing the calculator logic.
* **Memento Pattern:** Enables Undo and Redo capabilities by saving and restoring the calculator’s state.
* **Observer Pattern:** Triggers actions automatically — such as logging and saving history — when a new calculation occurs.
* **History Management:** Saves, loads, and clears calculation history using pandas for CSV persistence.
* **Error Handling:** Provides meaningful error messages for invalid inputs, division by zero, or unexpected runtime issues.
* **Logging:** Automatically logs every calculation and error event for traceability and debugging.
* **CI/CD Pipeline:** Integrated with GitHub Actions to automatically test every push and enforce 90% coverage.

---

## Supported Operations

| Command                         | Description                       |
| ------------------------------- | --------------------------------- |
| add, subtract, multiply, divide | Perform arithmetic operations     |
| power, root, modulus            | Perform advanced calculations     |
| int_divide, percent, abs_diff   | Perform extended calculations     |
| undo / redo                     | Undo or redo the last operation   |
| history                         | Show calculation history          |
| save / load                     | Save or load history using pandas |
| clear                           | Clear calculation history         |
| help                            | Show dynamic help menu            |
| exit                            | Exit the program                  |

---

## Advanced Features

### Dynamic Help Menu (Decorator Pattern)

The **Dynamic Help Menu** is implemented using the **Decorator Design Pattern**.
Each command in the REPL interface is registered dynamically through decorators.
This means whenever a new operation is added, it automatically appears in the help menu — without changing any other part of the code.

This approach simplifies maintenance and ensures that the help documentation is always synchronized with the actual available commands.
It’s a clean example of extensibility — one of the most valuable concepts in software design.

---

### Color-Coded Output (Colorama)

To make the REPL interface more readable and visually appealing, the program uses **Colorama** for color-coded terminal output:

***Green** → Successful results or confirmations
***Yellow** → Informational or warning messages
***Red** → Errors or invalid inputs

Example:
```python
from colorama import Fore, Style
print(Fore.GREEN + "Result: 25" + Style.RESET_ALL)
print(Fore.RED + "Error: Division by zero!" + Style.RESET_ALL)
```
Color feedback enhances usability, helps users quickly recognize results or errors, and gives the calculator a polished, professional feel.

---
## Setup Instructions

### Create and Activate a Virtual Environment
```bash
python3 -m venv venv
venv\Scripts\activate          
```
### Install Required Packages
```bash
pip install -r requirements.txt
```
### Run the Application
```bash
python main.py
```
If the setup is correct, you’ll see:
```
=== Starting Enhanced Calculator ===
Type 'help' to see available commands.
>
```

## Environment Configuration

Create a `.env` file in the root folder and include:
```
CALCULATOR_LOG_DIR=logs
CALCULATOR_HISTORY_DIR=history
CALCULATOR_MAX_HISTORY_SIZE=10
CALCULATOR_AUTO_SAVE=True
CALCULATOR_PRECISION=9
CALCULATOR_MAX_INPUT_VALUE=100000
CALCULATOR_DEFAULT_ENCODING=utf-8
```
These settings control log storage, history limits, precision, and general behavior.

---

## Using the Calculator

Once running, type commands directly in the REPL prompt:

| Command     | Example Input   | Description                         |
| ----------- | --------------- | ----------------------------------- |
| add         | `add 5 3`       | Adds two numbers                    |
| divide      | `divide 10 2`   | Divides first number by second      |
| power       | `power 2 4`     | Raises 2 to the power of 4          |
| percent     | `percent 45 50` | Finds percentage (90%)              |
| undo / redo | -               | Undo or redo last action            |
| history     | -               | Show stored calculations            |
| clear       | -               | Clear all saved history             |
| help        | -               | Show available commands dynamically |
| exit        | -               | Exit gracefully                     |

---

## Testing and Coverage

Run all tests with:
```bash
pytest -v
```
Generate coverage:
```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

**Expected Output:**
```
TOTAL 703 statements — 100% coverage
190 passed, 0 failed
```
To view detailed coverage results:
```
htmlcov/index.html
```
This ensures all code paths, including exception handling and decorators, are validated.

---

## Continuous Integration (CI/CD)

The project uses **GitHub Actions** to automatically run tests and check coverage on every push or pull request.
The workflow performs the following steps:

1. Check out repository code
2. Set up Python environment
3. Install dependencies
4. Run pytest with coverage
5. Enforce 100% coverage threshold

Workflow file:
```
.github/workflows/tests.yml
```
If coverage falls below 100%, the pipeline fails — ensuring complete test validation and maintaining the highest standard of software quality.

---
## Logging and Data Storage

* Every calculation and result is logged using Python’s built-in logging module.
* Each calculation (operation, operands, result, timestamp) is stored in a CSV file using pandas.
* History and log files are managed via `.env` paths, ensuring separation of data and logic.

Example log entry:
```
2025-10-21 18:42:05,613 - INFO - Performed operation: Addition(2, 3) = 5
```

---
## Reflection and Learning

Working on this project was an insightful experience.
I learned how applying **design patterns** like Factory, Observer, and Memento can transform a basic script into a modular, scalable system.
Building a dynamic help system through decorators taught me the power of extensibility, and adding **color-coded terminal feedback** helped me focus on user experience.

I also gained hands-on experience with **pytest**, **mock testing**, and **GitHub Actions** for CI/CD automation.
Achieving **100% code coverage** was especially rewarding — it demonstrated the value of testing in maintaining software reliability.
Most importantly, this project helped me connect theoretical software engineering concepts with real-world application design.

---

## Conclusion

The **Enhanced Calculator** represents more than a math tool — it is a demonstration of clean software architecture, modular design, and automated testing in Python.
It showcases how careful planning, reusable design patterns, and strong testing practices can produce software that is not only functional but also maintainable, user-friendly, and professional.

---

