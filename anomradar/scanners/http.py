"""
HTTP scanner using httpx.

Scans HTTP/HTTPS endpoints for:
- Response status
- Headers
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- SSL/TLS information
- Response time
"""

import asyncio
from typing import Any, Dict
from urllib.parse import urlparse

import httpx

from anomradar.core.logging import get_logger
from anomradar.scanners import BaseScanner, Signal, ScanStatus


logger = get_logger()


class HttpScanner(BaseScanner):
    """HTTP/HTTPS endpoint scanner."""
    
    def __init__(self, config: Any = None, cache: Any = None):
        """Initialize HTTP scanner."""
        super().__init__(config, cache)
        
        # Default timeout
        self.timeout = 15
        self.user_agent = "AnomRadar/2.0 (Security Scanner)"
        self.follow_redirects = True
        
        # Apply config if available
        if config and hasattr(config, "http_scanner"):
            self.timeout = config.http_scanner.timeout
            self.user_agent = config.http_scanner.user_agent
            self.follow_redirects = config.http_scanner.follow_redirects
    
    async def scan(self, target: str) -> Dict[str, Any]:
        """
        Scan HTTP/HTTPS endpoint.
        
        Args:
            target: URL or domain to scan
        
        Returns:
            Scan result dictionary
        """
        # Normalize target to URL
        if not target.startswith(("http://", "https://")):
            target = f"https://{target}"
        
        logger.info(f"HTTP scan starting: {target}")
        
        # Check cache
        cache_key = f"http:{target}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"HTTP scan cache hit: {target}")
                return cached
        
        signals = []
        details = {}
        
        try:
            # Perform HTTP request
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=self.follow_redirects,
                verify=True
            ) as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(target, headers=headers)
                
                # Collect basic info
                details["status_code"] = response.status_code
                details["url"] = str(response.url)
                details["headers"] = dict(response.headers)
                details["response_time_ms"] = response.elapsed.total_seconds() * 1000
                details["final_url"] = str(response.url)
                
                # Check for redirects
                if str(response.url) != target:
                    signals.append(Signal(
                        severity="info",
                        message=f"Redirect detected: {target} -> {response.url}",
                        details={"redirect": True}
                    ))
                
                # Check status code
                if response.status_code >= 400:
                    signals.append(Signal(
                        severity="medium",
                        message=f"HTTP error status: {response.status_code}",
                        details={"status_code": response.status_code}
                    ))
                elif response.status_code >= 300:
                    signals.append(Signal(
                        severity="low",
                        message=f"HTTP redirect status: {response.status_code}",
                        details={"status_code": response.status_code}
                    ))
                
                # Check security headers
                security_headers = self._check_security_headers(response.headers)
                details["security_headers"] = security_headers
                
                # Generate signals for missing headers
                for header, status in security_headers.items():
                    if not status["present"]:
                        signals.append(Signal(
                            severity=status["severity"],
                            message=f"Missing security header: {header}",
                            details={"header": header, "recommendation": status["description"]}
                        ))
                
                # Check SSL/TLS (if HTTPS)
                if target.startswith("https://"):
                    ssl_info = self._check_ssl_info(response)
                    details["ssl"] = ssl_info
                
                # Create summary
                summary = f"HTTP scan completed: {response.status_code} status"
                if signals:
                    summary += f", {len(signals)} findings"
                
                result = self.create_result(
                    status=ScanStatus.SUCCESS,
                    signals=signals,
                    summary=summary,
                    details=details
                )
                
                # Cache result
                if self.cache:
                    self.cache.set(cache_key, result)
                
                logger.info(f"HTTP scan completed: {target}")
                return result
        
        except httpx.TimeoutException as e:
            logger.warning(f"HTTP scan timeout: {target} - {e}")
            return self.create_degraded_result(e, {"timeout": True})
        
        except httpx.ConnectError as e:
            logger.warning(f"HTTP scan connection error: {target} - {e}")
            return self.create_degraded_result(e, {"connection_error": True})
        
        except Exception as e:
            logger.error(f"HTTP scan failed: {target} - {e}")
            return self.create_failed_result(e)
    
    def _check_security_headers(self, headers: httpx.Headers) -> Dict[str, Dict[str, Any]]:
        """
        Check for security headers.
        
        Args:
            headers: Response headers
        
        Returns:
            Dictionary of security header status
        """
        security_checks = {
            "strict-transport-security": {
                "description": "HSTS header enforces HTTPS",
                "severity": "medium"
            },
            "x-frame-options": {
                "description": "Protects against clickjacking",
                "severity": "low"
            },
            "x-content-type-options": {
                "description": "Prevents MIME sniffing",
                "severity": "low"
            },
            "content-security-policy": {
                "description": "Mitigates XSS attacks",
                "severity": "medium"
            },
            "x-xss-protection": {
                "description": "Legacy XSS protection",
                "severity": "low"
            },
            "referrer-policy": {
                "description": "Controls referrer information",
                "severity": "low"
            }
        }
        
        results = {}
        for header, info in security_checks.items():
            present = header in headers
            results[header] = {
                "present": present,
                "value": headers.get(header, None),
                "description": info["description"],
                "severity": info["severity"]
            }
        
        return results
    
    def _check_ssl_info(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Extract SSL/TLS information from response.
        
        Args:
            response: HTTP response
        
        Returns:
            SSL information dictionary
        """
        # Basic SSL info from httpx
        return {
            "enabled": True,
            "protocol": "TLS",  # httpx always uses TLS
            "note": "Use SSL scanner for detailed certificate analysis"
        }
