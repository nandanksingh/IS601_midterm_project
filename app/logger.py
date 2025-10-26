# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator (Logger)
# File: app/logger.py
# ----------------------------------------------------------
# Description:
# Implements centralized logging setup and observer integration
# for the Enhanced Calculator. Supports .env configuration
# for log directory, file naming, and dynamic log level.
# ----------------------------------------------------------

import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Logger:
    """Handles logging setup and provides methods for info and error messages."""
    def __init__(self):
        # ------------------------------------------------------
        # Log Directory and File Setup
        # ------------------------------------------------------
        log_dir = os.getenv("CALCULATOR_LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_filename = os.getenv(
            "CALCULATOR_LOG_FILE",
            f"calculator_{datetime.now().strftime('%Y_%m_%d')}.log"
        )
        log_path = os.path.join(log_dir, log_filename)

        # ------------------------------------------------------
        # Basic Logging Configuration
        # ------------------------------------------------------
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Create logger instance
        self.logger = logging.getLogger(__name__)

        # ------------------------------------------------------
        # Dynamic Log Level Support via .env
        # ------------------------------------------------------
        # Allows CALCULATOR_LOG_LEVEL in .env (e.g., DEBUG, INFO, WARNING, ERROR)
        self.logger.setLevel(logging.INFO)
        level = os.getenv("CALCULATOR_LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, level, logging.INFO))

        # Confirm initialization
        self.logger.info("Logger initialized successfully.")

    # ----------------------------------------------------------
    # Logging Helper Methods
    # ----------------------------------------------------------
    def log_info(self, message: str):
        """Log informational messages."""
        self.logger.info(message)

    def log_error(self, message: str):
        """Log error messages."""
        self.logger.error(message)


# ------------------------------------------------------------------
# Observer Pattern Implementation
# ------------------------------------------------------------------

class Observer:
    """Base class for all observers that react to calculator events."""
    def update(self, calculation):
        raise NotImplementedError("Subclass must implement update() method.")


class LoggingObserver(Observer):
    """
    Observer that logs every calculation event to a file.
    It receives updates from the Calculator (Subject).
    """
    def __init__(self, logger: Logger):
        self.logger = logger

    def update(self, calculation):
        """
        Log the details of a completed calculation.
        Expected attributes on 'calculation': operation, operand_a, operand_b, result.
        """
        message = (
            f"Operation: {calculation.operation}, "
            f"Operands: {calculation.operand_a}, {calculation.operand_b}, "
            f"Result: {calculation.result}"
        )
        self.logger.log_info(message)
