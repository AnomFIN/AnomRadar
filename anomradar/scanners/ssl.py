"""SSL/TLS scanner module with graceful degradation"""

import logging
import socket
import ssl
from typing import Dict, Any
from datetime import datetime

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

from anomradar.core.config import Config

logger = logging.getLogger("anomradar.scanners.ssl")


def scan_ssl(target: str, config: Config) -> Dict[str, Any]:
    """Scan SSL/TLS certificate with graceful degradation
    
    Returns structured dictionary with certificate information.
    Degrades gracefully on errors.
    
    Args:
        target: Domain to scan
        config: Configuration object
        
    Returns:
        Dictionary with scan results:
        {
            "success": bool,
            "message": str,
            "timestamp": str,
            "target": str,
            "data": {
                "version": str,
                "cipher": str,
                "issuer": str,
                "subject": str,
                "not_before": str,
                "not_after": str,
                "days_until_expiry": int,
                "san": list,
                "serial_number": str,
                "is_expired": bool
            }
        }
    """
    # Remove protocol if present
    target = target.replace("https://", "").replace("http://", "").split("/")[0]
    
    result = {
        "success": False,
        "message": "",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "target": target,
        "data": {}
    }
    
    try:
        logger.info(f"Scanning SSL certificate: {target}")
        
        timeout = config.timeout if hasattr(config, 'timeout') else 30
        port = 443
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect and get certificate
        with socket.create_connection((target, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                # Get certificate in DER format
                cert_der = ssock.getpeercert(binary_form=True)
                
                # Get SSL/TLS version and cipher
                ssl_version = ssock.version()
                cipher = ssock.cipher()
                
                if not CRYPTOGRAPHY_AVAILABLE:
                    # Basic info without cryptography library
                    result["success"] = True
                    result["message"] = "SSL scan completed (limited info - cryptography library not available)"
                    result["data"] = {
                        "version": ssl_version,
                        "cipher": cipher[0] if cipher else "Unknown",
                        "cipher_bits": cipher[2] if cipher else 0
                    }
                    result["warning"] = "Install cryptography library for detailed certificate information"
                    return result
                
                # Parse certificate with cryptography library
                cert = x509.load_der_x509_certificate(cert_der, default_backend())
                
                # Extract certificate details
                issuer = cert.issuer.rfc4514_string()
                subject = cert.subject.rfc4514_string()
                not_before = cert.not_valid_before
                not_after = cert.not_valid_after
                
                # Calculate days until expiry
                now = datetime.utcnow()
                days_until_expiry = (not_after - now).days
                is_expired = days_until_expiry < 0
                
                # Extract SAN (Subject Alternative Names)
                san = []
                try:
                    san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                    san = [name.value for name in san_ext.value]
                except x509.ExtensionNotFound:
                    pass
                
                result["success"] = True
                result["message"] = "SSL scan completed"
                result["data"] = {
                    "version": ssl_version,
                    "cipher": cipher[0] if cipher else "Unknown",
                    "cipher_bits": cipher[2] if cipher else 0,
                    "issuer": issuer,
                    "subject": subject,
                    "not_before": not_before.isoformat() + "Z",
                    "not_after": not_after.isoformat() + "Z",
                    "days_until_expiry": days_until_expiry,
                    "san": san,
                    "serial_number": str(cert.serial_number),
                    "is_expired": is_expired
                }
                
                if is_expired:
                    result["warning"] = "Certificate has expired!"
                elif days_until_expiry < 30:
                    result["warning"] = f"Certificate expires in {days_until_expiry} days"
                
                logger.info(f"SSL scan successful for {target} (expires in {days_until_expiry} days)")
                
    except socket.gaierror as e:
        logger.warning(f"SSL scan DNS error for {target}: {e}")
        result["message"] = "DNS resolution failed"
        result["error"] = "dns_error"
        
    except socket.timeout:
        logger.warning(f"SSL scan timeout for {target}")
        result["message"] = "Connection timeout"
        result["error"] = "timeout"
        
    except ssl.SSLError as e:
        logger.warning(f"SSL error for {target}: {e}")
        result["message"] = f"SSL error: {str(e)}"
        result["error"] = "ssl_error"
        
    except ConnectionRefusedError:
        logger.warning(f"Connection refused for {target}:443")
        result["message"] = "Connection refused (port 443)"
        result["error"] = "connection_refused"
        
    except Exception as e:
        logger.error(f"SSL scan error for {target}: {e}", exc_info=True)
        result["message"] = f"Scan error: {str(e)}"
        result["error"] = "unknown_error"
        result["error_type"] = type(e).__name__
    
    return result
