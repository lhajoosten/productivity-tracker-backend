"""Logging configuration for the application."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

from productivity_tracker.core.settings import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging():
    """Configure application logging with proper handlers and formatters."""

    # Skip file logging during tests if PYTEST_CURRENT_TEST is set
    is_testing = os.getenv("PYTEST_CURRENT_TEST") is not None

    # Determine log level based on environment
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Console format (with colors in debug mode)
    console_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    # File format (more detailed)
    file_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s | %(message)s"

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # Clear any existing handlers

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if settings.DEBUG:
        # Use colored output in debug mode
        console_handler.setFormatter(ColoredFormatter(console_format))
    else:
        console_handler.setFormatter(logging.Formatter(console_format, datefmt="%Y-%m-%d %H:%M:%S"))

    root_logger.addHandler(console_handler)

    # Only add file handlers if not testing
    if not is_testing:
        try:
            # Create logs directory if it doesn't exist
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            # Ensure the directory is writable
            if not os.access(log_dir, os.W_OK):
                # If not writable, just use console logging
                root_logger.warning(
                    f"Log directory {log_dir} is not writable, skipping file logging"
                )
                configure_third_party_loggers()
                return

            # File Handler - Application logs (rotating by size)
            app_file_handler = RotatingFileHandler(
                log_dir / "app.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            app_file_handler.setLevel(logging.INFO)
            app_file_handler.setFormatter(
                logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
            )
            root_logger.addHandler(app_file_handler)

            # File Handler - Error logs (daily rotation)
            error_file_handler = TimedRotatingFileHandler(
                log_dir / "error.log",
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8",
            )
            error_file_handler.setLevel(logging.ERROR)
            error_file_handler.setFormatter(
                logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
            )
            root_logger.addHandler(error_file_handler)
        except (PermissionError, OSError) as e:
            # If we can't create file handlers, just log to console
            root_logger.warning(f"Could not set up file logging: {e}. Using console only.")

    # Configure third-party loggers
    configure_third_party_loggers()

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    logger.info(f"Debug mode: {settings.DEBUG}")


def configure_third_party_loggers():
    """Configure log levels for third-party libraries."""

    # SQLAlchemy - reduce verbosity
    if settings.DEBUG:
        # Show SQL queries but not all the connection pool details
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)
    else:
        # In production, only show warnings and errors
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    # Uvicorn - reduce verbosity
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    # FastAPI
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Alembic
    logging.getLogger("alembic").setLevel(logging.INFO)

    # Watchfiles (file reloader)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Name of the logger (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
