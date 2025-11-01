"""
Logging system for AnomRadar v2.

Uses Rich for beautiful console output and file logging.
Supports debug mode with full trace logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback


# Install rich traceback globally
install_rich_traceback(show_locals=True)


# Global logger instance
_logger: Optional[logging.Logger] = None
_console: Optional[Console] = None


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    debug: bool = False
) -> logging.Logger:
    """
    Set up logging with Rich formatting.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Enable console output
        debug: Enable debug mode with full trace
    
    Returns:
        Configured logger instance
    """
    global _logger, _console
    
    if debug:
        level = "DEBUG"
    
    # Create console
    _console = Console(stderr=True)
    
    # Create logger
    logger = logging.getLogger("anomradar")
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers = []  # Clear existing handlers
    
    # Console handler with Rich
    if console_output:
        console_handler = RichHandler(
            console=_console,
            rich_tracebacks=True,
            tracebacks_show_locals=debug,
            show_time=True,
            show_path=debug,
        )
        console_handler.setLevel(getattr(logging, level.upper()))
        console_formatter = logging.Formatter(
            "%(message)s",
            datefmt="[%X]"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """
    Get the global logger instance.
    
    If not initialized, creates a basic logger.
    
    Returns:
        Logger instance
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logging()
    
    return _logger


def get_console() -> Console:
    """
    Get the global Rich console instance.
    
    Returns:
        Console instance
    """
    global _console
    
    if _console is None:
        _console = Console(stderr=True)
    
    return _console
