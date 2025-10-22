# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/17/2025
# Midterm Project: Enhanced Calculator (Configuration Management)
# ----------------------------------------------------------
# Description:
# This module defines the CalculatorConfig class responsible for
# loading, validating, and managing configuration parameters for
# the enhanced calculator application.
#
# Features:
# - Loads configuration from environment variables (.env file)
# - Uses python-dotenv for flexible setup
# - Provides safe defaults for all parameters
# - Validates numeric and directory constraints
#
# Environment Variables Supported:
#   CALCULATOR_BASE_DIR
#   CALCULATOR_LOG_DIR
#   CALCULATOR_HISTORY_DIR
#   CALCULATOR_LOG_FILE
#   CALCULATOR_HISTORY_FILE
#   CALCULATOR_MAX_HISTORY_SIZE
#   CALCULATOR_AUTO_SAVE
#   CALCULATOR_PRECISION
#   CALCULATOR_MAX_INPUT_VALUE
#   CALCULATOR_DEFAULT_ENCODING
# ----------------------------------------------------------

from dataclasses import dataclass
from decimal import Decimal
from numbers import Number
from pathlib import Path
import os
from typing import Optional
from dotenv import load_dotenv

from app.exceptions import ConfigurationError

# ----------------------------------------------------------
# Load environment variables from the .env file (if present)
# ----------------------------------------------------------
load_dotenv()


# ----------------------------------------------------------
# Utility Function
# ----------------------------------------------------------
def get_project_root() -> Path:
    """
    Determine the project root directory.

    This function resolves the project root dynamically by navigating
    two levels up from the current file’s location.

    Returns:
        Path: The absolute path to the project root directory.
    """
    return Path(__file__).resolve().parent.parent


# ----------------------------------------------------------
# Calculator Configuration Class
# ----------------------------------------------------------
@dataclass
class CalculatorConfig:
    """
    Configuration class for the calculator application.

    Handles environment-based configuration management, directory setup,
    and parameter validation for calculation precision, history size,
    auto-save, and encoding preferences.
    """

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        max_history_size: Optional[int] = None,
        auto_save: Optional[bool] = None,
        precision: Optional[int] = None,
        max_input_value: Optional[Number] = None,
        default_encoding: Optional[str] = None,
    ):
        """
        Initialize configuration parameters using environment variables
        or provided argument values.
        """
        # Determine project root or use provided base directory
        project_root = get_project_root()
        self.base_dir = base_dir or Path(
            os.getenv("CALCULATOR_BASE_DIR", str(project_root))
        ).resolve()

        # -------------------------------
        # History Management Settings
        # -------------------------------
        self.max_history_size = max_history_size or int(
            os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "1000")
        )

        # Auto-save flag (convert from string)
        auto_save_env = os.getenv("CALCULATOR_AUTO_SAVE", "true").lower()
        self.auto_save = auto_save if auto_save is not None else (
            auto_save_env == "true" or auto_save_env == "1"
        )

        # -------------------------------
        # Calculation Settings
        # -------------------------------
        self.precision = precision or int(
            os.getenv("CALCULATOR_PRECISION", "10")
        )

        self.max_input_value = max_input_value or Decimal(
            os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e999")
        )

        self.default_encoding = default_encoding or os.getenv(
            "CALCULATOR_DEFAULT_ENCODING", "utf-8"
        )

    # ------------------------------------------------------
    # Directory and File Path Properties
    # ------------------------------------------------------

    @property
    def log_dir(self) -> Path:
        """Return the directory where log files will be stored."""
        return Path(
            os.getenv("CALCULATOR_LOG_DIR", str(self.base_dir / "logs"))
        ).resolve()

    @property
    def history_dir(self) -> Path:
        """Return the directory where history files will be stored."""
        return Path(
            os.getenv("CALCULATOR_HISTORY_DIR", str(self.base_dir / "history"))
        ).resolve()

    @property
    def history_file(self) -> Path:
        """Return the path to the CSV file storing calculation history."""
        return Path(
            os.getenv(
                "CALCULATOR_HISTORY_FILE",
                str(self.history_dir / "calculator_history.csv"),
            )
        ).resolve()

    @property
    def log_file(self) -> Path:
        """Return the path to the log file."""
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
        """
        Validate all configuration parameters.

        Ensures correctness of numeric parameters and verifies
        directories exist or can be created.
        """
        # Numeric validations
        if self.max_history_size <= 0:
            raise ConfigurationError("max_history_size must be positive")
        if self.precision <= 0:
            raise ConfigurationError("precision must be positive")
        if self.max_input_value <= 0:
            raise ConfigurationError("max_input_value must be positive")

        # Directory checks
        for directory in [self.log_dir, self.history_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Encoding validation
        try:
            "".encode(self.default_encoding)
        except LookupError:
            raise ConfigurationError(
                f"Unsupported encoding: {self.default_encoding}"
            )

    def __repr__(self):
        """Provide a readable string summary for debugging and logs."""
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
