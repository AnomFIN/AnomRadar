"""
AnomRadar v2 - Production-ready security scanner toolkit.

A resilient CLI/TUI scanner with modular architecture, intelligent caching,
and brand-grade reporting capabilities.
"""

__version__ = "2.0.0"
__author__ = "AnomFIN"
__license__ = "MIT"

from anomradar.core.config import Config, get_config
from anomradar.core.logging import get_logger

__all__ = ["Config", "get_config", "get_logger", "__version__"]
