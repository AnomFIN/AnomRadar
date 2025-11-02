"""
Scanner base classes and common functionality.

All scanners return structured dictionaries with:
- status: "success", "partial", "failed"
- signals: List of findings/alerts
- summary: Human-readable summary
- details: Additional scan details
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from enum import Enum


class ScanStatus(str, Enum):
    """Scan result status."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class Signal:
    """Represents a finding or alert from a scan."""
    
    def __init__(
        self,
        severity: str,
        message: str,
        details: Dict[str, Any] = None
    ):
        """
        Initialize a signal.
        
        Args:
            severity: Severity level (info, low, medium, high, critical)
            message: Signal message
            details: Additional details
        """
        self.severity = severity
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary."""
        return {
            "severity": self.severity,
            "message": self.message,
            "details": self.details
        }


class BaseScanner(ABC):
    """
    Abstract base class for all scanners.
    
    Scanners must implement the scan() method and handle errors gracefully,
    returning degraded results rather than crashing.
    """
    
    def __init__(self, config: Any = None, cache: Any = None):
        """
        Initialize scanner.
        
        Args:
            config: Configuration object
            cache: Cache instance
        """
        self.config = config
        self.cache = cache
    
    @abstractmethod
    async def scan(self, target: str) -> Dict[str, Any]:
        """
        Perform scan on target.
        
        Args:
            target: Target to scan (domain, URL, etc.)
        
        Returns:
            Scan result dictionary with status, signals, summary, and details
        """
        pass
    
    def create_result(
        self,
        status: ScanStatus,
        signals: List[Signal],
        summary: str,
        details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create standardized scan result.
        
        Args:
            status: Scan status
            signals: List of signals/findings
            summary: Human-readable summary
            details: Additional details
        
        Returns:
            Standardized result dictionary
        """
        return {
            "status": status.value,
            "signals": [s.to_dict() for s in signals],
            "summary": summary,
            "details": details or {}
        }
    
    def create_degraded_result(self, error: Exception, partial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create degraded result when scan partially fails.
        
        Args:
            error: Exception that caused the degradation
            partial_data: Any data that was successfully collected
        
        Returns:
            Degraded result dictionary
        """
        signals = [
            Signal(
                severity="info",
                message=f"Scan completed with errors: {str(error)}",
                details={"error_type": type(error).__name__}
            )
        ]
        
        return {
            "status": ScanStatus.PARTIAL.value,
            "signals": [s.to_dict() for s in signals],
            "summary": f"Partial scan completed (error: {type(error).__name__})",
            "details": partial_data or {},
            "error": str(error)
        }
    
    def create_failed_result(self, error: Exception) -> Dict[str, Any]:
        """
        Create failed result when scan completely fails.
        
        Args:
            error: Exception that caused the failure
        
        Returns:
            Failed result dictionary
        """
        signals = [
            Signal(
                severity="info",
                message=f"Scan failed: {str(error)}",
                details={"error_type": type(error).__name__}
            )
        ]
        
        return {
            "status": ScanStatus.FAILED.value,
            "signals": [s.to_dict() for s in signals],
            "summary": f"Scan failed: {type(error).__name__}",
            "details": {},
            "error": str(error)
        }


__all__ = ["BaseScanner", "Signal", "ScanStatus"]
