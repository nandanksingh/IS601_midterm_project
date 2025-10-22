# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/21/2025
# Midterm Project: Enhanced Calculator Command-Line Application
# ----------------------------------------------------------

### **Project Overview**

This project is an enhanced version of a command-line calculator application developed using **Object-Oriented Programming principles** and **design patterns**.
The goal of the project is to create a modular, maintainable, and testable Python program that demonstrates real-world software engineering practices.

The calculator can perform a variety of mathematical operations, maintain calculation history, support undo/redo functionality, and persist data using CSV files.
The application also includes **color-coded terminal output** for better readability and **automated testing with GitHub Actions** to ensure continuous integration.

---

### **Installation Instructions**

1. **Repository**

   ```bash
      cd IS601_midterm_project
   ```

2. **Create and Activate Virtual Environment**

   ```bash
   python -m venv venv
   python3 -m venv venv
   source venv/bin/activate        
   ```

3. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

---

### **Configuration Setup**

Create a `.env` file in the project’s root directory and add the following variables:

```
LOG_DIR=logs
HISTORY_DIR=data
HISTORY_FILE=data/history.csv
AUTO_SAVE=true
MAX_HISTORY_SIZE=100
```

* `LOG_DIR` → Folder to store log files
* `HISTORY_FILE` → File path where calculator history is saved
* `AUTO_SAVE` → Automatically save calculation history after every operation
* `MAX_HISTORY_SIZE` → Maximum number of history entries to keep in memory

---

### **How to Run the Application**

Run the calculator from the terminal using:

```bash
python main.py
```

You will see:

```
Calculator started. Type 'help' for commands.
```

Type any command (like `add`, `subtract`, or `history`) and follow the prompts.
All outputs are color-coded for better visibility.

---

### **Supported Commands**

| Command                                                  | Description                               |
| -------------------------------------------------------- | ----------------------------------------- |
| `add`, `subtract`, `multiply`, `divide`, `power`, `root` | Perform basic operations                  |
| `modulus`, `int_divide`, `percent`, `abs_diff`           | Perform advanced operations               |
| `history`                                                | Display the list of previous calculations |
| `clear`                                                  | Clear calculator history                  |
| `undo`, `redo`                                           | Undo or redo the last operation           |
| `save`, `load`                                           | Save or load history from a CSV file      |
| `help`                                                   | Show all available commands               |
| `exit`                                                   | Exit the calculator safely                |

---

### **Testing Instructions**

All tests are written using **pytest** with coverage reporting enabled.

Run all tests:

```bash
pytest
```

Run tests with coverage report:

```bash
pytest --cov=app --cov-report=term-missing
```

To ensure high code quality, the CI/CD workflow enforces at least **90% test coverage**.

---

### **CI/CD Workflow (GitHub Actions)**

The GitHub Actions workflow automatically runs whenever you push code to the `main` branch or open a pull request.

**Workflow steps include:**

1. Checking out the code repository
2. Setting up Python environment
3. Installing dependencies
4. Running all tests using `pytest`
5. Failing the build if test coverage drops below 90%

This ensures that every code change is validated automatically before merging.

---

### **Code Design and Patterns Used**

| Design Pattern           | Role in Project                                                 |
| ------------------------ | --------------------------------------------------------------- |
| **Factory**              | Dynamically creates operation objects (e.g., Add, Divide, Root) |
| **Strategy**             | Allows operations to be executed independently                  |
| **Observer**             | Updates log and auto-save behavior automatically                |
| **Memento**              | Enables undo and redo features                                  |
| **Decorator (optional)** | Can generate a dynamic help menu                                |
| **Colorama**             | Adds color to console output for clarity                        |

---

### **Logging and History Management**

All calculator activities are logged automatically in the `logs/` folder.
Every calculation, undo, redo, or load/save event is recorded with timestamps.

Example log entry:

```
2025-10-16 14:32:10 - INFO - Performed operation: Addition(2, 3) = 5
```

Calculation history is stored in a CSV file (`data/history.csv`), which can be viewed or reloaded during later sessions.

---

### **Best Practices Followed**

* **DRY Principle:** Avoided repetitive code through modular design.
* **Modular Structure:** Each feature is placed in a dedicated file for clarity.
* **Error Handling:** Custom exception classes for safe and readable error messages.
* **Logging:** Centralized log configuration ensures full traceability.
* **CI/CD:** Continuous testing with GitHub Actions ensures reliability.

---

### **Project Folder Structure**

```
IS601_midterm_project/
│
├── app/
│   ├── calculator.py
│   ├── calculation.py
│   ├── operations.py
│   ├── calculator_repl.py
│   ├── calculator_config.py
│   ├── calculator_memento.py
│   ├── input_validators.py
│   ├── exceptions.py
│   ├── logger.py
│   └── history.py
│
├── tests/
│   ├── test_calculator.py
│   ├── test_calculator_repl.py
│   └── test_operations.py
│
├── .github/workflows/python-app.yml
├── requirements.txt
├── .env
├── main.py
└── README.md
```

---

### **Conclusion**

This project helped me apply advanced Python concepts such as design patterns, modular architecture, and continuous integration.
Through this assignment, I gained a deeper understanding of how to structure complex applications, manage code testing, and automate validation using GitHub Actions.

It was a valuable learning experience in both software engineering and collaborative development workflows.

---
