"""
HTML exporter using Jinja2 templating.

Exports scan results to branded HTML reports with fallback support.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound

from anomradar.core.logging import get_logger


logger = get_logger()


class HtmlExporter:
    """Export scan results to HTML format."""
    
    def __init__(self, output_dir: str = "~/.anomradar/reports", template_dir: str = None):
        """
        Initialize HTML exporter.
        
        Args:
            output_dir: Directory to save reports
            template_dir: Directory containing templates (auto-detected if None)
        """
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find template directory
        if template_dir is None:
            # Try package location
            template_dir = Path(__file__).parent.parent / "reports"
        
        self.template_dir = Path(template_dir)
        
        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def export(
        self,
        scan_results: Dict[str, Any],
        filename: str = None,
        template_name: str = "html_template.html"
    ) -> Path:
        """
        Export scan results to HTML file.
        
        Args:
            scan_results: Dictionary of scan results
            filename: Output filename (auto-generated if None)
            template_name: Template filename to use
        
        Returns:
            Path to exported file
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target = scan_results.get("target", "unknown")
            # Sanitize target for filename
            safe_target = "".join(c if c.isalnum() else "_" for c in target)
            filename = f"anomradar_{safe_target}_{timestamp}.html"
        
        # Ensure .html extension
        if not filename.endswith(".html"):
            filename += ".html"
        
        output_path = self.output_dir / filename
        
        try:
            # Load template
            try:
                template = self.env.get_template(template_name)
            except TemplateNotFound:
                logger.warning(f"Template {template_name} not found, using fallback")
                template = self.env.get_template("html_template_fallback.html")
            
            # Prepare template context
            context = {
                "target": scan_results.get("target", "Unknown"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "results": scan_results.get("results", {}),
                "metadata": scan_results.get("metadata", {})
            }
            
            # Render template
            html_content = template.render(**context)
            
            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"HTML report exported: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Failed to export HTML report: {e}")
            # Try to create a minimal fallback report
            try:
                return self._create_minimal_report(scan_results, output_path)
            except Exception as fallback_error:
                logger.error(f"Failed to create fallback report: {fallback_error}")
                raise
    
    def _create_minimal_report(self, scan_results: Dict[str, Any], output_path: Path) -> Path:
        """
        Create a minimal HTML report without template.
        
        Args:
            scan_results: Dictionary of scan results
            output_path: Path to output file
        
        Returns:
            Path to exported file
        """
        target = scan_results.get("target", "Unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AnomRadar Report - {target}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; }}
        h1 {{ color: #667eea; }}
        pre {{ background: #f0f0f0; padding: 15px; overflow: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AnomRadar Security Report</h1>
        <p><strong>Target:</strong> {target}</p>
        <p><strong>Generated:</strong> {timestamp}</p>
        <h2>Scan Results</h2>
        <pre>{scan_results}</pre>
    </div>
</body>
</html>"""
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        logger.info(f"Minimal HTML report created: {output_path}")
        return output_path
