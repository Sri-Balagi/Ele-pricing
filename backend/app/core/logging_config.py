"""
Logging configuration for the Elevator Configuration Engine.

Sets up:
  - Console handler (stdout)
  - Rotating file handler → LOG_DIR/app.log
  - Root logger level from Settings

Call setup_logging() once at application startup (inside create_app()).
All subsequent modules use logging.getLogger(__name__) — no other setup needed.
"""

import logging
import logging.config
import logging.handlers
from pathlib import Path

from app.core.constants import LOG_DATE_FORMAT, LOG_FORMAT


def setup_logging(
    log_level: str,
    log_dir: str,
    max_bytes: int,
    backup_count: int,
) -> None:
    """
    Configure structured application logging via dictConfig.

    Args:
        log_level: Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_dir: Directory where rotating log files are stored.
        max_bytes: Maximum bytes per log file before rotation.
        backup_count: Number of rotated backup files to keep.
    """
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)
    log_file = log_dir_path / "app.log"

    config: dict = {
        "version": 1,
        "disable_existing_loggers": False,  # preserve third-party loggers
        "formatters": {
            "standard": {
                "format": LOG_FORMAT,
                "datefmt": LOG_DATE_FORMAT,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "standard",
                "filename": str(log_file),
                "maxBytes": max_bytes,
                "backupCount": backup_count,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "rotating_file"],
        },
        # Quieten noisy third-party loggers that spam at INFO/DEBUG
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "propagate": True,
            },
            "uvicorn.access": {
                "level": "WARNING",
                "propagate": True,
            },
            "httpx": {
                "level": "WARNING",
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(config)
