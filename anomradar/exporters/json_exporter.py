"""
JSON exporter using orjson for high-performance serialization.

Exports scan results to JSON format with pretty printing and metadata.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import orjson

from anomradar.core.logging import get_logger


logger = get_logger()


class JsonExporter:
    """Export scan results to JSON format."""
    
    def __init__(self, output_dir: str = "~/.anomradar/reports"):
        """
        Initialize JSON exporter.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(
        self,
        scan_results: Dict[str, Any],
        filename: str = None,
        pretty: bool = True
    ) -> Path:
        """
        Export scan results to JSON file.
        
        Args:
            scan_results: Dictionary of scan results
            filename: Output filename (auto-generated if None)
            pretty: Enable pretty printing
        
        Returns:
            Path to exported file
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target = scan_results.get("target", "unknown")
            # Sanitize target for filename
            safe_target = "".join(c if c.isalnum() else "_" for c in target)
            filename = f"anomradar_{safe_target}_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"
        
        output_path = self.output_dir / filename
        
        # Add metadata
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "AnomRadar v2",
                "format_version": "1.0"
            },
            "scan_results": scan_results
        }
        
        try:
            # Use orjson for fast serialization
            if pretty:
                json_bytes = orjson.dumps(
                    export_data,
                    option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
                )
            else:
                json_bytes = orjson.dumps(export_data)
            
            # Write to file
            with open(output_path, "wb") as f:
                f.write(json_bytes)
            
            logger.info(f"JSON report exported: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Failed to export JSON report: {e}")
            raise
    
    def export_multiple(
        self,
        scan_results_list: List[Dict[str, Any]],
        filename: str = None
    ) -> Path:
        """
        Export multiple scan results to a single JSON file.
        
        Args:
            scan_results_list: List of scan result dictionaries
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to exported file
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"anomradar_batch_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"
        
        output_path = self.output_dir / filename
        
        # Add metadata
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "AnomRadar v2",
                "format_version": "1.0",
                "scan_count": len(scan_results_list)
            },
            "scans": scan_results_list
        }
        
        try:
            # Use orjson for fast serialization
            json_bytes = orjson.dumps(
                export_data,
                option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
            )
            
            # Write to file
            with open(output_path, "wb") as f:
                f.write(json_bytes)
            
            logger.info(f"JSON batch report exported: {output_path} ({len(scan_results_list)} scans)")
            return output_path
        
        except Exception as e:
            logger.error(f"Failed to export JSON batch report: {e}")
            raise
