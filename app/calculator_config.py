# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/17/2025
# Midterm Project: Enhanced Calculator (Configuration Management)
# File: app/calculator_config.py
# ----------------------------------------------------------
# Description:
# Defines the CalculatorConfig dataclass that manages all
# configuration parameters for the Enhanced Calculator.
# Features:
#   • Loads settings from .env using python-dotenv
#   • Provides safe defaults when environment variables are missing
#   • Allows constructor arguments to override environment variables
#   • Validates numeric and directory settings
# ----------------------------------------------------------

from dataclasses import dataclass
from decimal import Decimal
from numbers import Number
from pathlib import Path
import os
from typing import Optional
from dotenv import load_dotenv

from app.exceptions import ConfigError

# ----------------------------------------------------------
# Load environment variables from .env (if present)
# ----------------------------------------------------------
load_dotenv()


# ----------------------------------------------------------
# Utility Function
# ----------------------------------------------------------
def get_project_root() -> Path:
    """Return the project root directory path."""
    return Path(__file__).resolve().parent.parent


# ----------------------------------------------------------
# Calculator Configuration Class
# ----------------------------------------------------------
@dataclass
class CalculatorConfig:
    """
    Manages configuration for the Enhanced Calculator.

    Loads environment variables via python-dotenv and provides
    defaults for missing values. Constructor arguments always
    override environment values.
    """

    base_dir: Optional[Path] = None
    max_history_size: Optional[int] = None
    auto_save: Optional[bool] = None
    precision: Optional[int] = None
    max_input_value: Optional[Number] = None
    default_encoding: Optional[str] = None

    # ------------------------------------------------------
    # Initialization
    # ------------------------------------------------------
    def __init__(
        self,
        base_dir: Optional[Path] = None,
        max_history_size: Optional[int] = None,
        auto_save: Optional[bool] = None,
        precision: Optional[int] = None,
        max_input_value: Optional[Number] = None,
        default_encoding: Optional[str] = None,
    ):
        project_root = get_project_root()
        self.base_dir = base_dir or Path(
            os.getenv("CALCULATOR_BASE_DIR", str(project_root))
        ).resolve()

        # -------------------------------
        # History and Auto-Save Settings
        # -------------------------------
        self.max_history_size = int(
            max_history_size
            if max_history_size is not None
            else os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "1000")
        )

        if auto_save is not None:
            self.auto_save = bool(auto_save)
        else:
            auto_save_env = os.getenv("CALCULATOR_AUTO_SAVE", "true").lower()
            self.auto_save = auto_save_env in ("true", "1", "yes")

        # -------------------------------
        # Calculation Settings
        # -------------------------------
        self.precision = int(
            precision
            if precision is not None
            else os.getenv("CALCULATOR_PRECISION", "10")
        )

        self.max_input_value = Decimal(
            str(max_input_value)
            if max_input_value is not None
            else os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e999")
        )

        self.default_encoding = (
            default_encoding
            if default_encoding is not None
            else os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")
        )

    # ------------------------------------------------------
    # Directory and File Path Properties
    # ------------------------------------------------------
    @property
    def log_dir(self) -> Path:
        """Return the directory for log files."""
        return Path(
            os.getenv("CALCULATOR_LOG_DIR", str(self.base_dir / "logs"))
        ).resolve()

    @property
    def history_dir(self) -> Path:
        """Return the directory for history CSV files."""
        return Path(
            os.getenv("CALCULATOR_HISTORY_DIR", str(self.base_dir / "history"))
        ).resolve()

    @property
    def history_file(self) -> Path:
        """Return the path to the calculator history CSV file."""
        return Path(
            os.getenv(
                "CALCULATOR_HISTORY_FILE",
                str(self.history_dir / "calculator_history.csv"),
            )
        ).resolve()

    @property
    def log_file(self) -> Path:
        """Return the path to the calculator log file."""
        return Path(
            os.getenv(
                "CALCULATOR_LOG_FILE",
                str(self.log_dir / "calculator.log"),
            )
        ).resolve()

    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------
    def validate(self) -> None:
        """Validate all configuration parameters."""
        if self.max_history_size <= 0:
            raise ConfigError("max_history_size must be positive")
        if self.precision <= 0:
            raise ConfigError("precision must be positive")
        if self.max_input_value <= 0:
            raise ConfigError("max_input_value must be positive")

        # Ensure required directories exist
        for directory in [self.log_dir, self.history_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Validate encoding
        try:
            "".encode(self.default_encoding)
        except LookupError:
            raise ConfigError(f"Unsupported encoding: {self.default_encoding}")

    # ------------------------------------------------------
    # Representation
    # ------------------------------------------------------
    def __repr__(self):
        """Return a formatted string for debugging."""
        return (
            f"CalculatorConfig("
            f"log_dir={self.log_dir}, "
            f"history_dir={self.history_dir}, "
            f"max_history_size={self.max_history_size}, "
            f"auto_save={self.auto_save}, "
            f"precision={self.precision}, "
            f"max_input_value={self.max_input_value}, "
            f"default_encoding='{self.default_encoding}')"
        )
