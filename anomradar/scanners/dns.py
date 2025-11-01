"""
DNS scanner using dnspython.

Scans DNS records for:
- A/AAAA records
- MX records (mail servers)
- TXT records (SPF, DMARC, etc.)
- NS records (nameservers)
- SOA record
"""

import asyncio
from typing import Any, Dict

import dns.resolver
import dns.exception

from anomradar.core.logging import get_logger
from anomradar.scanners import BaseScanner, Signal, ScanStatus


logger = get_logger()


class DnsScanner(BaseScanner):
    """DNS record scanner."""
    
    def __init__(self, config: Any = None, cache: Any = None):
        """Initialize DNS scanner."""
        super().__init__(config, cache)
        
        # Default settings
        self.nameservers = ["8.8.8.8", "1.1.1.1"]
        self.timeout = 10
        
        # Apply config if available
        if config and hasattr(config, "dns_scanner"):
            self.nameservers = config.dns_scanner.nameservers_list
            self.timeout = config.dns_scanner.timeout
        
        # Configure resolver
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = self.nameservers
        self.resolver.timeout = self.timeout
        self.resolver.lifetime = self.timeout
    
    async def scan(self, target: str) -> Dict[str, Any]:
        """
        Scan DNS records for a domain.
        
        Args:
            target: Domain name to scan
        
        Returns:
            Scan result dictionary
        """
        # Normalize domain (remove http://, https://, trailing slash)
        domain = target.replace("http://", "").replace("https://", "").rstrip("/")
        if "/" in domain:
            domain = domain.split("/")[0]
        
        logger.info(f"DNS scan starting: {domain}")
        
        # Check cache
        cache_key = f"dns:{domain}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"DNS scan cache hit: {domain}")
                return cached
        
        signals = []
        details = {}
        record_types = ["A", "AAAA", "MX", "TXT", "NS", "SOA"]
        
        try:
            # Query each record type
            for record_type in record_types:
                try:
                    answers = await asyncio.to_thread(
                        self.resolver.resolve,
                        domain,
                        record_type
                    )
                    
                    records = []
                    for rdata in answers:
                        if record_type == "MX":
                            records.append({
                                "preference": rdata.preference,
                                "exchange": str(rdata.exchange)
                            })
                        elif record_type == "SOA":
                            records.append({
                                "mname": str(rdata.mname),
                                "rname": str(rdata.rname),
                                "serial": rdata.serial,
                                "refresh": rdata.refresh,
                                "retry": rdata.retry,
                                "expire": rdata.expire,
                                "minimum": rdata.minimum
                            })
                        else:
                            records.append(str(rdata))
                    
                    details[record_type.lower()] = records
                    
                    # Generate signals for findings
                    if record_type == "A" and records:
                        signals.append(Signal(
                            severity="info",
                            message=f"Found {len(records)} A record(s)",
                            details={"records": records}
                        ))
                    
                    if record_type == "MX":
                        if not records:
                            signals.append(Signal(
                                severity="low",
                                message="No MX records found (email may not work)",
                                details={"record_type": "MX"}
                            ))
                        else:
                            signals.append(Signal(
                                severity="info",
                                message=f"Found {len(records)} MX record(s)",
                                details={"records": records}
                            ))
                
                except dns.resolver.NoAnswer:
                    details[record_type.lower()] = []
                    logger.debug(f"No {record_type} records for {domain}")
                
                except dns.resolver.NXDOMAIN:
                    logger.warning(f"Domain does not exist: {domain}")
                    return self.create_failed_result(
                        Exception(f"Domain does not exist: {domain}")
                    )
                
                except Exception as e:
                    logger.debug(f"Error querying {record_type} for {domain}: {e}")
                    details[record_type.lower()] = []
            
            # Check for SPF record
            txt_records = details.get("txt", [])
            spf_found = any("spf" in record.lower() for record in txt_records)
            if not spf_found:
                signals.append(Signal(
                    severity="medium",
                    message="No SPF record found (email security risk)",
                    details={"recommendation": "Add SPF record to prevent email spoofing"}
                ))
            else:
                signals.append(Signal(
                    severity="info",
                    message="SPF record found",
                    details={"spf": True}
                ))
            
            # Check for DMARC record
            dmarc_found = any("dmarc" in record.lower() for record in txt_records)
            if not dmarc_found:
                signals.append(Signal(
                    severity="medium",
                    message="No DMARC record found (email security risk)",
                    details={"recommendation": "Add DMARC record for email authentication"}
                ))
            else:
                signals.append(Signal(
                    severity="info",
                    message="DMARC record found",
                    details={"dmarc": True}
                ))
            
            # Create summary
            record_count = sum(
                len(v) if isinstance(v, list) else 0
                for v in details.values()
            )
            summary = f"DNS scan completed: {record_count} total records found"
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
            
            logger.info(f"DNS scan completed: {domain}")
            return result
        
        except dns.exception.Timeout as e:
            logger.warning(f"DNS scan timeout: {domain} - {e}")
            return self.create_degraded_result(e, details)
        
        except Exception as e:
            logger.error(f"DNS scan failed: {domain} - {e}")
            return self.create_failed_result(e)
