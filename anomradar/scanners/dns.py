"""DNS scanner module with graceful degradation"""

import logging
from typing import Dict, Any, List
from datetime import datetime

try:
    import dns.resolver
    import dns.exception
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

from anomradar.core.config import Config

logger = logging.getLogger("anomradar.scanners.dns")


def scan_dns(target: str, config: Config) -> Dict[str, Any]:
    """Scan DNS records with graceful degradation
    
    Returns structured dictionary with DNS records.
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
                "A": list,
                "AAAA": list,
                "MX": list,
                "TXT": list,
                "NS": list,
                "SOA": dict,
                "CNAME": list
            }
        }
    """
    if not DNS_AVAILABLE:
        return {
            "success": False,
            "message": "dnspython library not available",
            "error": "missing_dependency",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "target": target
        }
    
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
        logger.info(f"Scanning DNS records: {target}")
        
        # Configure resolver
        resolver = dns.resolver.Resolver()
        resolver.timeout = config.timeout if hasattr(config, 'timeout') else 30
        resolver.lifetime = config.timeout if hasattr(config, 'timeout') else 30
        
        # Define record types to query
        record_types = ["A", "AAAA", "MX", "TXT", "NS", "SOA", "CNAME"]
        records_found = {}
        errors = {}
        
        # Query each record type
        for record_type in record_types:
            try:
                answers = resolver.resolve(target, record_type)
                records = []
                
                if record_type == "MX":
                    records = [
                        {"preference": rdata.preference, "exchange": str(rdata.exchange)}
                        for rdata in answers
                    ]
                elif record_type == "SOA":
                    # SOA returns single record
                    soa = answers[0]
                    records_found["SOA"] = {
                        "mname": str(soa.mname),
                        "rname": str(soa.rname),
                        "serial": soa.serial,
                        "refresh": soa.refresh,
                        "retry": soa.retry,
                        "expire": soa.expire,
                        "minimum": soa.minimum
                    }
                    continue
                else:
                    records = [str(rdata) for rdata in answers]
                
                records_found[record_type] = records
                logger.debug(f"Found {len(records)} {record_type} records for {target}")
                
            except dns.resolver.NoAnswer:
                logger.debug(f"No {record_type} records for {target}")
                errors[record_type] = "no_answer"
            except dns.resolver.NXDOMAIN:
                logger.warning(f"Domain not found: {target}")
                errors[record_type] = "nxdomain"
            except dns.exception.Timeout:
                logger.warning(f"DNS timeout for {record_type} on {target}")
                errors[record_type] = "timeout"
            except Exception as e:
                logger.debug(f"Error querying {record_type} for {target}: {e}")
                errors[record_type] = str(e)
        
        # Determine success
        if records_found:
            result["success"] = True
            result["message"] = f"DNS scan completed ({len(records_found)} record types found)"
            result["data"] = records_found
            if errors:
                result["partial_errors"] = errors
            logger.info(f"DNS scan successful for {target}")
        else:
            result["message"] = "No DNS records found"
            result["error"] = "no_records"
            result["errors"] = errors
            
    except dns.resolver.NXDOMAIN:
        logger.warning(f"Domain not found: {target}")
        result["message"] = "Domain does not exist"
        result["error"] = "nxdomain"
        
    except dns.exception.Timeout:
        logger.warning(f"DNS timeout for {target}")
        result["message"] = "DNS query timeout"
        result["error"] = "timeout"
        
    except Exception as e:
        logger.error(f"DNS scan error for {target}: {e}", exc_info=True)
        result["message"] = f"Scan error: {str(e)}"
        result["error"] = "unknown_error"
        result["error_type"] = type(e).__name__
    
    return result
