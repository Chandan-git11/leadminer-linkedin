"""Logging configuration module."""
import sys
from pathlib import Path
from loguru import logger

from config import Config


def setup_logging() -> None:
    """Configure loguru logging."""
    # Remove default handler
    logger.remove()

    # Ensure log directory exists
    log_dir = Config.ensure_log_dir()

    # Console handler
    logger.add(
        sys.stderr,
        level=Config.LOG_LEVEL,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # File handler
    log_file = log_dir / "linkedin_extractor.log"
    logger.add(
        str(log_file),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="500 MB",
        retention="7 days",
    )

    logger.info(f"Logging initialized. Log level: {Config.LOG_LEVEL}")


def get_logger(name: str) -> logger:
    """Get logger instance."""
    return logger.bind(name=name)
