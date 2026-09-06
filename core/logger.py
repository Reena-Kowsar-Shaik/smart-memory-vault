"""
Centralized Application Logger
Role: Member 1
Configures rotating file logs and console logging for debugging and audit trails.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "app.log")


def setup_logger(name: str = "MemoryVault") -> logging.Logger:
    """Configures and returns a logger instance with file and console handlers."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Format: timestamp - level - module - message
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Rotating file handler (max 2MB per file, keeps 3 backups)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    return logger


# Global logger instance
app_logger = setup_logger()
