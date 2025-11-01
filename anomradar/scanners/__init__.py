"""Scanner package initialization and utilities"""

from typing import Dict, List, Optional, Any
import logging

from anomradar.core.cache import FileCache
from anomradar.core.config import Config

logger = logging.getLogger("anomradar.scanners")


def get_available_scanners() -> List[str]:
    """Get list of available scanner names"""
    return ["http", "dns", "ssl"]


def run_scan(
    target: str,
    scanner_names: Optional[List[str]] = None,
    config: Optional[Config] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """Run scanners on target and return results
    
    Args:
        target: Target domain or IP to scan
        scanner_names: List of scanner names to run (None = all)
        config: Configuration object
        use_cache: Whether to use cached results
        
    Returns:
        Dictionary mapping scanner names to their results
    """
    if config is None:
        config = Config.load()
    
    # Initialize cache
    cache = None
    if use_cache and config.cache_enabled:
        cache = FileCache(config.cache_dir, config.cache_ttl)
    
    # Determine which scanners to run
    if scanner_names is None:
        scanner_names = get_available_scanners()
    
    results = {}
    
    # Import and run each scanner
    for scanner_name in scanner_names:
        logger.info(f"Running {scanner_name} scanner on {target}")
        
        # Check cache first
        cache_key = f"scan:{scanner_name}:{target}"
        if cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Using cached result for {scanner_name}")
                results[scanner_name] = cached_result
                continue
        
        # Run scanner
        try:
            if scanner_name == "http":
                from anomradar.scanners.http import scan_http
                result = scan_http(target, config)
            elif scanner_name == "dns":
                from anomradar.scanners.dns import scan_dns
                result = scan_dns(target, config)
            elif scanner_name == "ssl":
                from anomradar.scanners.ssl import scan_ssl
                result = scan_ssl(target, config)
            else:
                result = {
                    "success": False,
                    "message": f"Unknown scanner: {scanner_name}",
                    "error": "scanner_not_found"
                }
            
            # Cache successful results
            if cache and result.get("success"):
                cache.set(cache_key, result)
            
            results[scanner_name] = result
            
        except Exception as e:
            logger.error(f"Scanner {scanner_name} failed: {e}", exc_info=True)
            results[scanner_name] = {
                "success": False,
                "message": f"Scanner error: {str(e)}",
                "error": "scanner_exception",
                "error_type": type(e).__name__
            }
    
    return results
