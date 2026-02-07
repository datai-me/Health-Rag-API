"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Any

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """
    Configure application-wide logging.
    
    Sets up structured logging with appropriate formatters
    based on the environment configuration.
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=get_log_format(),
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("fastapi").setLevel(log_level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={settings.log_level}, "
        f"format={settings.log_format}, environment={settings.environment}"
    )


def get_log_format() -> str:
    """
    Get the appropriate log format based on settings.
    
    Returns:
        Log format string
    """
    if settings.log_format == "json":
        # In production, you might want to use a proper JSON formatter
        return "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        return "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class LoggerMixin:
    """Mixin to add logger to classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for the class."""
        return logging.getLogger(self.__class__.__name__)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
