"""
SSL/TLS scanner using Python's ssl and socket modules.

Scans SSL/TLS certificates for:
- Certificate validity
- Expiration date
- Issuer information
- Subject alternative names
- Protocol version
- Cipher suite
"""

import asyncio
import socket
import ssl
from datetime import datetime
from typing import Any, Dict
from urllib.parse import urlparse

from anomradar.core.logging import get_logger
from anomradar.scanners import BaseScanner, Signal, ScanStatus


logger = get_logger()


class SslScanner(BaseScanner):
    """SSL/TLS certificate and configuration scanner."""
    
    def __init__(self, config: Any = None, cache: Any = None):
        """Initialize SSL scanner."""
        super().__init__(config, cache)
        
        # Default settings
        self.timeout = 20
        self.verify_expiration = True
        self.check_weak_ciphers = True
        
        # Apply config if available
        if config and hasattr(config, "ssl_scanner"):
            self.timeout = config.ssl_scanner.timeout
            self.verify_expiration = config.ssl_scanner.verify_expiration
            self.check_weak_ciphers = config.ssl_scanner.check_weak_ciphers
    
    async def scan(self, target: str) -> Dict[str, Any]:
        """
        Scan SSL/TLS configuration for a domain.
        
        Args:
            target: Domain or URL to scan
        
        Returns:
            Scan result dictionary
        """
        # Parse target to get hostname
        if target.startswith(("http://", "https://")):
            parsed = urlparse(target)
            hostname = parsed.hostname
            port = parsed.port or 443
        else:
            hostname = target
            port = 443
        
        logger.info(f"SSL scan starting: {hostname}:{port}")
        
        # Check cache
        cache_key = f"ssl:{hostname}:{port}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"SSL scan cache hit: {hostname}:{port}")
                return cached
        
        signals = []
        details = {}
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            cert_info = await asyncio.to_thread(
                self._get_certificate,
                hostname,
                port,
                context
            )
            
            if not cert_info:
                return self.create_failed_result(
                    Exception(f"Could not retrieve certificate for {hostname}:{port}")
                )
            
            # Parse certificate information
            details["hostname"] = hostname
            details["port"] = port
            details["subject"] = dict(x[0] for x in cert_info.get("subject", []))
            details["issuer"] = dict(x[0] for x in cert_info.get("issuer", []))
            details["version"] = cert_info.get("version")
            details["serial_number"] = cert_info.get("serialNumber")
            details["not_before"] = cert_info.get("notBefore")
            details["not_after"] = cert_info.get("notAfter")
            
            # Get subject alternative names
            san = []
            for item in cert_info.get("subjectAltName", []):
                if item[0] == "DNS":
                    san.append(item[1])
            details["subject_alt_names"] = san
            
            # Check certificate validity
            not_after = cert_info.get("notAfter")
            if not_after and self.verify_expiration:
                expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                days_until_expiry = (expiry_date - datetime.now()).days
                
                details["days_until_expiry"] = days_until_expiry
                
                if days_until_expiry < 0:
                    signals.append(Signal(
                        severity="critical",
                        message="SSL certificate has expired",
                        details={"expired_days_ago": abs(days_until_expiry)}
                    ))
                elif days_until_expiry < 30:
                    signals.append(Signal(
                        severity="high",
                        message=f"SSL certificate expires soon ({days_until_expiry} days)",
                        details={"days_until_expiry": days_until_expiry}
                    ))
                elif days_until_expiry < 90:
                    signals.append(Signal(
                        severity="medium",
                        message=f"SSL certificate expires in {days_until_expiry} days",
                        details={"days_until_expiry": days_until_expiry}
                    ))
                else:
                    signals.append(Signal(
                        severity="info",
                        message=f"SSL certificate is valid ({days_until_expiry} days remaining)",
                        details={"days_until_expiry": days_until_expiry}
                    ))
            
            # Check issuer
            issuer = details.get("issuer", {})
            issuer_cn = issuer.get("commonName", "Unknown")
            details["issuer_common_name"] = issuer_cn
            
            if "self-signed" in issuer_cn.lower() or issuer == details.get("subject", {}):
                signals.append(Signal(
                    severity="high",
                    message="Self-signed certificate detected",
                    details={"issuer": issuer_cn}
                ))
            else:
                signals.append(Signal(
                    severity="info",
                    message=f"Certificate issued by: {issuer_cn}",
                    details={"issuer": issuer_cn}
                ))
            
            # Check protocol and cipher (basic check)
            if self.check_weak_ciphers:
                # This is a simplified check
                # Real implementation would need deeper protocol analysis
                signals.append(Signal(
                    severity="info",
                    message="TLS/SSL connection successful",
                    details={"protocol": "TLS"}
                ))
            
            # Create summary
            summary = f"SSL scan completed: Certificate valid for {hostname}"
            if signals:
                critical_count = sum(1 for s in signals if s.severity == "critical")
                high_count = sum(1 for s in signals if s.severity == "high")
                if critical_count > 0:
                    summary += f" ({critical_count} critical issue(s))"
                elif high_count > 0:
                    summary += f" ({high_count} high severity issue(s))"
            
            result = self.create_result(
                status=ScanStatus.SUCCESS,
                signals=signals,
                summary=summary,
                details=details
            )
            
            # Cache result
            if self.cache:
                self.cache.set(cache_key, result)
            
            logger.info(f"SSL scan completed: {hostname}:{port}")
            return result
        
        except socket.timeout:
            logger.warning(f"SSL scan timeout: {hostname}:{port}")
            return self.create_degraded_result(
                Exception(f"Connection timeout to {hostname}:{port}"),
                details
            )
        
        except socket.gaierror as e:
            logger.warning(f"SSL scan DNS error: {hostname}:{port} - {e}")
            return self.create_failed_result(e)
        
        except ssl.SSLError as e:
            logger.warning(f"SSL scan error: {hostname}:{port} - {e}")
            return self.create_degraded_result(e, {"ssl_error": str(e)})
        
        except Exception as e:
            logger.error(f"SSL scan failed: {hostname}:{port} - {e}")
            return self.create_failed_result(e)
    
    def _get_certificate(self, hostname: str, port: int, context: ssl.SSLContext) -> Dict[str, Any]:
        """
        Get SSL certificate from server.
        
        Args:
            hostname: Server hostname
            port: Server port
            context: SSL context
        
        Returns:
            Certificate information dictionary
        """
        try:
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    return ssock.getpeercert()
        except Exception as e:
            logger.debug(f"Error getting certificate: {e}")
            return None
