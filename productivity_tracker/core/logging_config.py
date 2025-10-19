"""Logging configuration for the application."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

from productivity_tracker.core.settings import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        "grey": "\x1b[38;21m",
        "blue": "\x1b[38;5;39m",
        "cyan": "\x1b[38;5;51m",
        "yellow": "\x1b[38;5;226m",
        "orange": "\x1b[38;5;208m",
        "red": "\x1b[38;5;196m",
        "bold_red": "\x1b[31;1m",
        "magenta": "\x1b[38;5;213m",
        "green": "\x1b[38;5;46m",
        "reset": "\x1b[0m",
    }

    # Level-specific colors
    LEVEL_COLORS = {
        logging.DEBUG: "grey",
        logging.INFO: "green",
        logging.WARNING: "orange",
        logging.ERROR: "red",
        logging.CRITICAL: "bold_red",
    }

    def __init__(self, fmt: str, datefmt: str = "%Y-%m-%d %H:%M:%S"):
        """Initialize formatter."""
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with component-specific colors."""
        # Get level color
        level_color = self.COLORS[self.LEVEL_COLORS.get(record.levelno, "grey")]

        # Format timestamp (cyan)
        timestamp = self.formatTime(record, self.datefmt)
        colored_timestamp = f"{self.COLORS['cyan']}{timestamp}{self.COLORS['reset']}"

        # Format level (level-specific color)
        colored_level = f"{level_color}{record.levelname}{self.COLORS['reset']}"

        # Format logger name (magenta)
        colored_name = f"{self.COLORS['magenta']}{record.name}{self.COLORS['reset']}"

        # Format message (blue for normal, yellow for warnings, red for errors)
        message_color = level_color if record.levelno >= logging.WARNING else self.COLORS["blue"]
        colored_message = f"{message_color}{record.getMessage()}{self.COLORS['reset']}"

        # Assemble the final log line
        return f"{colored_timestamp} | {colored_level:8s} | {colored_name} | {colored_message}"


def setup_logging(
    log_level: str | None = None, console_only: bool = True, enable_file_logging: bool = False
) -> None:
    """Configure application logging with proper handlers and formatters.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   If None, uses DEBUG if settings.DEBUG else INFO.
        console_only: If True, only log to console (default for development).
        enable_file_logging: If True, attempt to enable file logging.
                            Requires console_only=False.
    """
    # Skip file logging during tests if PYTEST_CURRENT_TEST is set
    is_testing = os.getenv("PYTEST_CURRENT_TEST") is not None

    # Force console-only mode during tests
    if is_testing:
        console_only = True
        enable_file_logging = False

    # Determine log level
    if log_level is None:
        level = logging.DEBUG if settings.DEBUG else logging.INFO
    else:
        level = getattr(logging, log_level.upper(), logging.INFO)

    # Console format (with colors in debug mode)
    console_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    # File format (more detailed)
    file_format = "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(funcName)s | %(message)s"

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()  # Clear any existing handlers

    # Console Handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if settings.DEBUG:
        # Use colored output in debug mode (now optimized)
        console_handler.setFormatter(ColoredFormatter(console_format))
    else:
        console_handler.setFormatter(logging.Formatter(console_format, datefmt="%Y-%m-%d %H:%M:%S"))

    root_logger.addHandler(console_handler)

    # File Handlers (optional, only if explicitly enabled)
    if not console_only and enable_file_logging:
        _setup_file_handlers(root_logger, level, file_format)

    # Configure third-party loggers
    configure_third_party_loggers()

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")
    logger.info(f"Log level: {logging.getLevelName(level)}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Console only: {console_only}")
    if enable_file_logging and not console_only:
        logger.info("File logging: enabled")


def _setup_file_handlers(root_logger: logging.Logger, level: int, file_format: str) -> None:
    """Set up file handlers for logging.

    Args:
        root_logger: Root logger instance
        level: Logging level
        file_format: Format string for file logs
    """
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Check if directory is writable
        if not os.access(log_dir, os.W_OK):
            root_logger.warning(
                f"Log directory '{log_dir}' is not writable. Skipping file logging."
            )
            return

        # Application logs (rotating by size)
        app_file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        app_file_handler.setLevel(logging.INFO)
        app_file_handler.setFormatter(logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S"))
        root_logger.addHandler(app_file_handler)

        # Error logs (daily rotation)
        error_file_handler = TimedRotatingFileHandler(
            log_dir / "error.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S"))
        root_logger.addHandler(error_file_handler)

        root_logger.info(f"File logging enabled in directory: {log_dir.absolute()}")

    except (PermissionError, OSError) as e:
        root_logger.warning(f"Could not set up file logging: {e}. Using console only.")


def configure_third_party_loggers() -> None:
    """Configure log levels for third-party libraries to reduce noise."""

    # SQLAlchemy - reduce verbosity
    if settings.DEBUG:
        # Show SQL queries but not connection pool details
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
