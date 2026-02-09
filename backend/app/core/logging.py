"""
Logging Configuration

Centralized logging setup with structured logging and security audit trails.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    """Setup application logging configuration."""
    
    # Remove default logger
    logger.remove()
    
    # Console logging with colors
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
    )
    
    # File logging for general application logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "app.log",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )
    
    # Security audit log
    logger.add(
        log_dir / "security.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        filter=lambda record: "AUTH_ATTEMPT" in record["message"] or 
                             "PERMISSION_CHECK" in record["message"] or
                             "DATA_ACCESS" in record["message"] or
                             "SECURITY_EVENT" in record["message"],
        rotation="10 MB",
        retention="90 days",  # Keep security logs longer
        compression="zip",
    )
    
    # Error log for debugging
    logger.add(
        log_dir / "errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )
    
    logger.info(f"Logging setup complete with level: {log_level}")


def log_structured(event_type: str, data: Dict[str, Any]) -> None:
    """Log structured data for analytics and monitoring."""
    logger.info(f"STRUCTURED_LOG: type={event_type}, data={data}")