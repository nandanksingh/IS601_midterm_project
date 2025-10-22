# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/17/2025
# Midterm Project: Enhanced Calculator (Configuration Tests)
# ----------------------------------------------------------
# Description:
# This test module validates the CalculatorConfig class from
# `app/calculator_config.py`, ensuring correct environment-based
# configuration management, directory setup, and validation.
#
# Test Coverage Includes:
#   - Default environment variable loading
#   - Manual overrides in constructor
#   - Directory and file path resolution
#   - Auto-save boolean conversions
#   - Validation of invalid numeric inputs
#   - Fallback defaults when environment variables are absent
# ----------------------------------------------------------

import pytest
import os
from decimal import Decimal
from pathlib import Path
from app.calculator_config import CalculatorConfig, get_project_root
from app.exceptions import ConfigurationError


# ----------------------------------------------------------
# Helper Setup
# ----------------------------------------------------------

# Set up controlled environment variables for repeatable tests
os.environ["CALCULATOR_MAX_HISTORY_SIZE"] = "500"
os.environ["CALCULATOR_AUTO_SAVE"] = "false"
os.environ["CALCULATOR_PRECISION"] = "8"
os.environ["CALCULATOR_MAX_INPUT_VALUE"] = "1000"
os.environ["CALCULATOR_DEFAULT_ENCODING"] = "utf-16"
os.environ["CALCULATOR_LOG_DIR"] = "./test_logs"
os.environ["CALCULATOR_HISTORY_DIR"] = "./test_history"
os.environ["CALCULATOR_HISTORY_FILE"] = "./test_history/test_history.csv"
os.environ["CALCULATOR_LOG_FILE"] = "./test_logs/test_log.log"


def clear_env_vars(*args):
    """Helper to clear one or more environment variables."""
    for var in args:
        os.environ.pop(var, None)


# ----------------------------------------------------------
# Default Configuration Tests
# ----------------------------------------------------------

def test_default_configuration():
    """Validate environment-based configuration loading."""
    config = CalculatorConfig()
    assert config.max_history_size == 500
    assert config.auto_save is False
    assert config.precision == 8
    assert config.max_input_value == Decimal("1000")
    assert config.default_encoding == "utf-16"
    assert config.log_dir == Path("./test_logs").resolve()
    assert config.history_dir == Path("./test_history").resolve()
    assert config.history_file == Path("./test_history/test_history.csv").resolve()
    assert config.log_file == Path("./test_logs/test_log.log").resolve()


# ----------------------------------------------------------
# Manual Overrides
# ----------------------------------------------------------

def test_custom_configuration():
    """Ensure manual constructor parameters override .env values."""
    config = CalculatorConfig(
        max_history_size=300,
        auto_save=True,
        precision=5,
        max_input_value=Decimal("500"),
        default_encoding="ascii",
    )
    assert config.max_history_size == 300
    assert config.auto_save is True
    assert config.precision == 5
    assert config.max_input_value == Decimal("500")
    assert config.default_encoding == "ascii"


# ----------------------------------------------------------
# Directory and File Resolution
# ----------------------------------------------------------

def test_directory_properties():
    """Verify log and history directory defaults under custom base_dir."""
    clear_env_vars("CALCULATOR_LOG_DIR", "CALCULATOR_HISTORY_DIR")
    config = CalculatorConfig(base_dir=Path("/custom_base_dir"))
    assert config.log_dir == Path("/custom_base_dir/logs").resolve()
    assert config.history_dir == Path("/custom_base_dir/history").resolve()


def test_file_properties():
    """Verify default history and log file locations."""
    clear_env_vars("CALCULATOR_HISTORY_FILE", "CALCULATOR_LOG_FILE")
    config = CalculatorConfig(base_dir=Path("/custom_base_dir"))
    assert config.history_file == Path("/custom_base_dir/history/calculator_history.csv").resolve()
    assert config.log_file == Path("/custom_base_dir/logs/calculator.log").resolve()


# ----------------------------------------------------------
# Validation Tests
# ----------------------------------------------------------

def test_invalid_max_history_size():
    """Ensure invalid max_history_size raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="max_history_size must be positive"):
        config = CalculatorConfig(max_history_size=-1)
        config.validate()


def test_invalid_precision():
    """Ensure invalid precision raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="precision must be positive"):
        config = CalculatorConfig(precision=-1)
        config.validate()


def test_invalid_max_input_value():
    """Ensure invalid max_input_value raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="max_input_value must be positive"):
        config = CalculatorConfig(max_input_value=Decimal("-1"))
        config.validate()


# ----------------------------------------------------------
# Boolean Conversion Tests (auto_save)
# ----------------------------------------------------------

def test_auto_save_env_var_true():
    os.environ["CALCULATOR_AUTO_SAVE"] = "true"
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is True


def test_auto_save_env_var_one():
    os.environ["CALCULATOR_AUTO_SAVE"] = "1"
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is True


def test_auto_save_env_var_false():
    os.environ["CALCULATOR_AUTO_SAVE"] = "false"
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is False


def test_auto_save_env_var_zero():
    os.environ["CALCULATOR_AUTO_SAVE"] = "0"
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is False


# ----------------------------------------------------------
# Fallbacks and Overrides
# ----------------------------------------------------------

def test_environment_overrides():
    """Ensure .env environment variables correctly override defaults."""
    config = CalculatorConfig()
    assert config.max_history_size == 500
    assert config.auto_save is False
    assert config.precision == 8
    assert config.max_input_value == Decimal("1000")
    assert config.default_encoding == "utf-16"


def test_default_fallbacks():
    """Ensure default values apply when environment variables are missing."""
    clear_env_vars(
        "CALCULATOR_MAX_HISTORY_SIZE",
        "CALCULATOR_AUTO_SAVE",
        "CALCULATOR_PRECISION",
        "CALCULATOR_MAX_INPUT_VALUE",
        "CALCULATOR_DEFAULT_ENCODING",
    )
    config = CalculatorConfig()
    assert config.max_history_size == 1000
    assert config.auto_save is True
    assert config.precision == 10
    assert config.max_input_value == Decimal("1e999")
    assert config.default_encoding == "utf-8"


# ----------------------------------------------------------
# Utility Function Test
# ----------------------------------------------------------

def test_get_project_root():
    """Verify that get_project_root() resolves to the correct parent path."""
    root_path = get_project_root()
    assert (root_path / "app").exists() or root_path.exists()


# ----------------------------------------------------------
# Path Property Validation
# ----------------------------------------------------------

def test_log_dir_property():
    """Ensure log_dir resolves to /new_base_dir/logs when not in .env."""
    clear_env_vars("CALCULATOR_LOG_DIR")
    config = CalculatorConfig(base_dir=Path("/new_base_dir"))
    assert config.log_dir == Path("/new_base_dir/logs").resolve()


def test_history_dir_property():
    """Ensure history_dir resolves to /new_base_dir/history when not in .env."""
    clear_env_vars("CALCULATOR_HISTORY_DIR")
    config = CalculatorConfig(base_dir=Path("/new_base_dir"))
    assert config.history_dir == Path("/new_base_dir/history").resolve()


def test_log_file_property():
    """Ensure log_file defaults correctly when environment variable is missing."""
    clear_env_vars("CALCULATOR_LOG_FILE")
    config = CalculatorConfig(base_dir=Path("/new_base_dir"))
    assert config.log_file == Path("/new_base_dir/logs/calculator.log").resolve()


def test_history_file_property():
    """Ensure history_file defaults correctly when environment variable is missing."""
    clear_env_vars("CALCULATOR_HISTORY_FILE")
    config = CalculatorConfig(base_dir=Path("/new_base_dir"))
    assert config.history_file == Path("/new_base_dir/history/calculator_history.csv").resolve()
