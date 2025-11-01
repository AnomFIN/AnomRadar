"""AnomRadar v2 - Production-Ready Security Scanner Toolkit

A resilient CLI/TUI security scanning toolkit with graceful degradation,
structured output, and professional reporting.
"""

__version__ = "2.0.0"
__author__ = "AnomFIN"
__license__ = "MIT"

from anomradar.core.config import Config
from anomradar.core.logging import get_logger

__all__ = ["Config", "get_logger", "__version__"]
