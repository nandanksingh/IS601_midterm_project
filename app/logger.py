# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 10/16/2025
# Midterm Project: Enhanced Calculator (Logger)
# ----------------------------------------------------------
# Description:
# Implements centralized logging setup and observer integration
# for the Enhanced Calculator. Supports .env configuration
# for log directory and file naming.
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
        log_dir = os.getenv("CALCULATOR_LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_filename = os.getenv(
            "CALCULATOR_LOG_FILE",
            f"calculator_{datetime.now().strftime('%Y_%m_%d')}.log"
        )
        log_path = os.path.join(log_dir, log_filename)

        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info("Logger initialized successfully.")

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
        message = (
            f"Operation: {calculation.operation}, "
            f"Operands: {calculation.operand_a}, {calculation.operand_b}, "
            f"Result: {calculation.result}"
        )
        self.logger.log_info(message)
