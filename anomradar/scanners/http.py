"""HTTP scanner module with graceful degradation"""

import logging
from typing import Dict, Any
from datetime import datetime

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from anomradar.core.config import Config

logger = logging.getLogger("anomradar.scanners.http")


def scan_http(target: str, config: Config) -> Dict[str, Any]:
    """Scan HTTP/HTTPS endpoint with graceful degradation
    
    Returns structured dictionary with scan results.
    Degrades gracefully on errors.
    
    Args:
        target: Domain or URL to scan
        config: Configuration object
        
    Returns:
        Dictionary with scan results:
        {
            "success": bool,
            "message": str,
            "timestamp": str,
            "target": str,
            "data": {
                "status_code": int,
                "headers": dict,
                "redirect_chain": list,
                "response_time_ms": float,
                "server": str,
                "content_type": str,
                "security_headers": dict
            }
        }
    """
    if not HTTPX_AVAILABLE:
        return {
            "success": False,
            "message": "httpx library not available",
            "error": "missing_dependency",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "target": target
        }
    
    # Ensure target has scheme
    if not target.startswith(("http://", "https://")):
        target = f"https://{target}"
    
    result = {
        "success": False,
        "message": "",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "target": target,
        "data": {}
    }
    
    try:
        logger.info(f"Scanning HTTP endpoint: {target}")
        
        timeout = config.timeout if hasattr(config, 'timeout') else 30
        user_agent = config.user_agent if hasattr(config, 'user_agent') else "AnomRadar/2.0"
        
        # Perform HTTP request
        with httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": user_agent}
        ) as client:
            start_time = datetime.now()
            response = client.get(target)
            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Extract headers
        headers = dict(response.headers)
        
        # Check security headers
        security_headers = {
            "strict_transport_security": headers.get("strict-transport-security"),
            "content_security_policy": headers.get("content-security-policy"),
            "x_frame_options": headers.get("x-frame-options"),
            "x_content_type_options": headers.get("x-content-type-options"),
            "x_xss_protection": headers.get("x-xss-protection"),
        }
        
        # Build redirect chain
        redirect_chain = []
        if hasattr(response, 'history') and response.history:
            redirect_chain = [str(r.url) for r in response.history]
        
        result["success"] = True
        result["message"] = f"HTTP scan completed (status: {response.status_code})"
        result["data"] = {
            "status_code": response.status_code,
            "headers": headers,
            "redirect_chain": redirect_chain,
            "response_time_ms": round(response_time_ms, 2),
            "server": headers.get("server", "Unknown"),
            "content_type": headers.get("content-type", "Unknown"),
            "security_headers": security_headers,
            "final_url": str(response.url)
        }
        
        logger.info(f"HTTP scan successful for {target}: {response.status_code}")
        
    except httpx.TimeoutException as e:
        logger.warning(f"HTTP scan timeout for {target}: {e}")
        result["message"] = "Request timeout"
        result["error"] = "timeout"
        
    except httpx.ConnectError as e:
        logger.warning(f"HTTP connection error for {target}: {e}")
        result["message"] = "Connection failed"
        result["error"] = "connection_error"
        
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP status error for {target}: {e}")
        result["message"] = f"HTTP error: {e.response.status_code}"
        result["error"] = "http_error"
        result["data"]["status_code"] = e.response.status_code
        
    except Exception as e:
        logger.error(f"HTTP scan error for {target}: {e}", exc_info=True)
        result["message"] = f"Scan error: {str(e)}"
        result["error"] = "unknown_error"
        result["error_type"] = type(e).__name__
    
    return result
