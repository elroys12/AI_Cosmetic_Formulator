# app/utils/logger.py

import logging
import sys
from app.config.settings import get_settings

settings = get_settings()


def get_logger(name: str) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)

    # Avoid duplicate handlers on re-import
    if not logger.handlers:
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

        # Console handler
        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
