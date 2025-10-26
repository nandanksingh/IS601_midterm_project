# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/17/2025
# Midterm Project: Enhanced Calculator 
# File: tests/test_config.py
# ----------------------------------------------------------
# Description:
# This test module validates the CalculatorConfig class from
# `app/calculator_config.py`, ensuring correct environment-based
# configuration management, directory setup, and validation.
#
# Test Coverage Includes:
#   - Default environment variable loading
#   - Manual overrides in dataclass instantiation
#   - Directory and file path resolution
#   - Auto-save boolean conversions
#   - Validation of invalid numeric inputs
#   - Fallback defaults when environment variables are absent
#   - Validation of invalid encoding
#   - Repr coverage
# ----------------------------------------------------------

import pytest
import os
from decimal import Decimal
from pathlib import Path
from app.calculator_config import CalculatorConfig, get_project_root
from app.exceptions import ConfigError

# ----------------------------------------------------------
# Helper Setup
# ----------------------------------------------------------

# Preload environment variables for predictable test behavior
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
    """Helper function to clear specified environment variables."""
    for var in args:
        os.environ.pop(var, None)


# ----------------------------------------------------------
# Default Configuration Tests
# ----------------------------------------------------------

def test_default_configuration_loads_from_env():
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

def test_manual_overrides_take_precedence():
    """Ensure manually provided arguments override environment variables."""
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

def test_directory_paths_resolve_correctly():
    """Verify log and history directory defaults under a custom base_dir."""
    clear_env_vars("CALCULATOR_LOG_DIR", "CALCULATOR_HISTORY_DIR")
    config = CalculatorConfig(base_dir=Path("/custom_base_dir"))
    assert config.log_dir == Path("/custom_base_dir/logs").resolve()
    assert config.history_dir == Path("/custom_base_dir/history").resolve()


def test_file_paths_resolve_correctly():
    """Verify default history and log file locations."""
    clear_env_vars("CALCULATOR_HISTORY_FILE", "CALCULATOR_LOG_FILE")
    config = CalculatorConfig(base_dir=Path("/custom_base_dir"))
    assert config.history_file == Path("/custom_base_dir/history/calculator_history.csv").resolve()
    assert config.log_file == Path("/custom_base_dir/logs/calculator.log").resolve()


# ----------------------------------------------------------
# Validation Tests
# ----------------------------------------------------------

def test_invalid_max_history_size_raises():
    """Ensure invalid max_history_size raises ConfigError."""
    config = CalculatorConfig(max_history_size=-1)
    with pytest.raises(ConfigError, match="max_history_size must be positive"):
        config.validate()


def test_invalid_precision_raises():
    """Ensure invalid precision raises ConfigError."""
    config = CalculatorConfig(precision=-5)
    with pytest.raises(ConfigError, match="precision must be positive"):
        config.validate()


def test_invalid_max_input_value_raises():
    """Ensure invalid max_input_value raises ConfigError."""
    config = CalculatorConfig(max_input_value=Decimal("-1"))
    with pytest.raises(ConfigError, match="max_input_value must be positive"):
        config.validate()


# ----------------------------------------------------------
# Boolean Conversion Tests (auto_save)
# ----------------------------------------------------------

@pytest.mark.parametrize("env_value, expected", [
    ("true", True),
    ("1", True),
    ("false", False),
    ("0", False),
])
def test_auto_save_boolean_conversion(env_value, expected):
    """Verify CALCULATOR_AUTO_SAVE environment parsing to boolean."""
    os.environ["CALCULATOR_AUTO_SAVE"] = env_value
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is expected


# ----------------------------------------------------------
# Fallback Defaults
# ----------------------------------------------------------

def test_defaults_apply_when_env_missing():
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

def test_get_project_root_points_to_parent():
    """Verify that get_project_root() returns a valid directory."""
    root_path = get_project_root()
    assert root_path.exists()
    assert isinstance(root_path, Path)


# ----------------------------------------------------------
# Path Property Validation
# ----------------------------------------------------------

def test_log_dir_defaults_to_logs_folder():
    """Ensure log_dir defaults to logs folder inside base_dir."""
    clear_env_vars("CALCULATOR_LOG_DIR")
    config = CalculatorConfig(base_dir=Path("/new_base_dir"))
    assert config.log_dir == Path("/new_base_dir/logs").resolve()


def test_history_dir_defaults_to_history_folder():
    """Ensure history_dir defaults to history folder inside base_dir."""
    clear_env_vars("CALCULATOR_HISTORY_DIR")
    config = CalculatorConfig(base_dir=Path("/new_base_dir"))
    assert config.history_dir == Path("/new_base_dir/history").resolve()


def test_log_file_defaults_to_calculator_log():
    """Ensure log_file defaults correctly."""
    clear_env_vars("CALCULATOR_LOG_FILE")
    config = CalculatorConfig(base_dir=Path("/new_base_dir"))
    assert config.log_file == Path("/new_base_dir/logs/calculator.log").resolve()


def test_history_file_defaults_to_calculator_history_csv():
    """Ensure history_file defaults correctly."""
    clear_env_vars("CALCULATOR_HISTORY_FILE")
    config = CalculatorConfig(base_dir=Path("/new_base_dir"))
    assert config.history_file == Path("/new_base_dir/history/calculator_history.csv").resolve()


# ----------------------------------------------------------
# Coverage Tests (Encoding + Repr)
# ----------------------------------------------------------

def test_invalid_encoding_raises_configerror():
    """Trigger LookupError in validate() for unsupported encoding."""
    config = CalculatorConfig(default_encoding="fake-encoding")
    with pytest.raises(ConfigError, match="Unsupported encoding"):
        config.validate()


def test_repr_includes_key_fields():
    """Ensure __repr__() covers final branch."""
    config = CalculatorConfig()
    rep = repr(config)
    assert "CalculatorConfig" in rep
    assert "precision" in rep
    assert "auto_save" in rep
