"""Logging utilities for Phone Shamer application."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(config=None, name: str = "phone_shamer") -> logging.Logger:
    """
    Setup and configure logger.

    Args:
        config: Config object with logging settings. If None, uses defaults.
        name: Logger name.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Get log level and file from config or use defaults
    if config and hasattr(config, 'logging'):
        log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
        log_file = config.logging.file
    else:
        log_level = logging.INFO
        log_file = "phone_shamer.log"

    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler for {log_file}: {e}")

    return logger


def get_logger(name: str = "phone_shamer") -> logging.Logger:
    """
    Get existing logger or create a new one.

    Args:
        name: Logger name.

    Returns:
        Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger = setup_logger(name=name)
    return logger
