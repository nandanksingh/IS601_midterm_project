# Assignment 5 – Enhanced Calculator (REPL with Design Patterns)

## Overview

This project is an enhanced **command-line calculator** built in Python using advanced **Object-Oriented Programming (OOP)** principles and multiple **software design patterns**.
It extends the earlier calculator assignments by introducing persistent history, undo/redo functionality, configuration management, and an interactive **REPL (Read-Eval-Print Loop)** interface.

Key features:

* **Arithmetic operations:** addition, subtraction, multiplication, division, power, and root
* **Design patterns:** Factory, Strategy, Memento, Observer, and Facade
* **History management:** view, save, and load calculation history using `pandas`
* **Undo/Redo support:** implemented through the Memento pattern
* **Configuration handling:** manages log and history paths through environment settings
* **Error handling:** detects invalid inputs, handles exceptions gracefully
* **Testing and coverage:** unit and parameterized tests with 96–100 % coverage enforced via GitHub Actions

---

## Setup

1. **Clone the repository**

   git clone <repo-url>
   cd IS601_Assignment5

2. **Create and activate a virtual environment**

   python -m venv venv
   venv\Scripts\activate    # Windows
   
3. **Install dependencies**

   pip install -r requirements.txt

---

## Usage Instructions

1. **Run the calculator**

   python -m app.calculator_repl

   * Enter commands like `add`, `subtract`, `multiply`, `divide`, `power`, or `root`.
   * Use `history`, `undo`, `redo`, `save`, `load`, `clear`, and `exit` commands inside the REPL.
   * Press `Ctrl + C` or type `exit` to quit safely.

2. **Run tests**

   pytest -v --disable-warnings --cov=app --cov-report=term-missing
   
3. **View coverage report**

   coverage html
   

   Open `htmlcov/index.html` in a browser to see detailed results.

---

## Continuous Integration (CI)

Automated testing is set up using **GitHub Actions**.
Every push or pull request to the `main` branch automatically runs all tests and enforces 100 % coverage.

**Workflow location:**
`.github/workflows/tests.yml`

If coverage drops below 100 %, the build fails — ensuring code quality and testing discipline on every commit.

---

## Reflection

This assignment helped me move beyond basic OOP toward professional-level software design.
By implementing patterns like Factory, Strategy, Observer, Memento, and Facade, I learned how to structure modular and scalable applications.
Integrating `pandas` for data management and `pytest` for comprehensive testing enhanced the calculator’s reliability and real-world usefulness.

I also gained practical experience in CI/CD through GitHub Actions and coverage enforcement, which reflects how modern development teams maintain code quality.
Overall, this project strengthened my understanding of design patterns, testing strategies, and automation — key skills for developing robust Python applications.

