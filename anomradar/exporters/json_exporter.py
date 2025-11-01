"""JSON exporter using orjson for fast, pretty JSON output"""

import logging
from pathlib import Path
from typing import Any, Dict

try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    import json
    ORJSON_AVAILABLE = False

logger = logging.getLogger("anomradar.exporters.json")


def export_json(data: Dict[str, Any], output_path: Path, pretty: bool = True) -> None:
    """Export scan results to JSON file
    
    Uses orjson for fast serialization with fallback to standard json.
    
    Args:
        data: Scan results dictionary
        output_path: Path to output JSON file
        pretty: Whether to pretty-print the JSON (default: True)
    """
    logger.info(f"Exporting JSON to {output_path}")
    
    try:
        if ORJSON_AVAILABLE:
            # Use orjson for fast serialization
            options = orjson.OPT_INDENT_2 if pretty else 0
            json_bytes = orjson.dumps(data, option=options)
            
            with open(output_path, 'wb') as f:
                f.write(json_bytes)
        else:
            # Fallback to standard json
            with open(output_path, 'w') as f:
                if pretty:
                    json.dump(data, f, indent=2)
                else:
                    json.dump(data, f)
        
        logger.info(f"JSON export completed: {output_path}")
        
    except Exception as e:
        logger.error(f"JSON export failed: {e}", exc_info=True)
        raise
