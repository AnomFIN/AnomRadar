"""Structured logging for AnomRadar v2"""

import logging
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format: [LEVEL] timestamp - message
        formatted = f"{color}[{record.levelname}]{reset} {datetime.now().strftime('%H:%M:%S')} - {record.getMessage()}"
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def get_logger(
    name: str = "anomradar",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    json_format: bool = False
) -> logging.Logger:
    """Get configured logger instance
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        json_format: Use JSON formatting (useful for production)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler with colored output (if not JSON format)
    console_handler = logging.StreamHandler(sys.stdout)
    if json_format:
        console_handler.setFormatter(JsonFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # File handler with JSON format if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
    
    return logger


def setup_logging(config: Any) -> logging.Logger:
    """Setup logging from configuration
    
    Args:
        config: Configuration object with logging settings
        
    Returns:
        Configured logger instance
    """
    log_level = config.log_level if hasattr(config, 'log_level') else "INFO"
    
    # Check for nested logging config
    if hasattr(config, 'logging') and config.logging:
        log_level = config.logging.level
        log_file = Path(config.logging.output).expanduser()
        json_format = config.logging.format == "json"
    else:
        log_file = None
        json_format = False
    
    return get_logger(
        name="anomradar",
        level=log_level,
        log_file=log_file,
        json_format=json_format
    )
