"""Output formatting utilities."""

import json
from typing import Dict, Any
from datetime import datetime
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class OutputFormatter:
    """Format monitoring output for display."""

    def __init__(self, format_type: str = "json", verbose: bool = True):
        """Initialize output formatter.
        
        Args:
            format_type: Output format ('json' or 'text')
            verbose: Include verbose details
        """
        self.format_type = format_type.lower()
        self.verbose = verbose
    
    def format(self, results: Dict[str, Any]) -> str:
        """Format results based on configured type.
        
        Args:
            results: Monitoring results dictionary
            
        Returns:
            Formatted output string
        """
        if self.format_type == "json":
            return self._format_json(results)
        else:
            return self._format_text(results)
    
    def _format_json(self, results: Dict[str, Any]) -> str:
        """Format results as JSON.
        
        Args:
            results: Monitoring results
            
        Returns:
            JSON string
        """
        return json.dumps(results, indent=2, default=str)
    
    def _format_text(self, results: Dict[str, Any]) -> str:
        """Format results as human-readable text.
        
        Args:
            results: Monitoring results
            
        Returns:
            Formatted text string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("  DB2 & Kubernetes Monitoring Report")
        lines.append("=" * 60)
        lines.append(f"Timestamp: {results.get('timestamp', 'N/A')}")
        lines.append(f"Overall Status: {self._colorize_status(results.get('overall_status', 'unknown'))}")
        lines.append("")
        
        # DB2 Results
        if 'db2' in results.get('checks', {}):
            lines.append("--- DB2 Health Check ---")
            db2 = results['checks']['db2']
            lines.append(f"  Status: {self._colorize_status(db2.get('status', 'unknown'))}")
            lines.append(f"  Connected: {db2.get('connected', False)}")
            lines.append(f"  Query Executed: {db2.get('query_executed', False)}")
            lines.append(f"  Response Time: {db2.get('response_time_ms', 0)} ms")
            
            if self.verbose:
                lines.append(f"  Details: {db2.get('details', 'N/A')}")
                if db2.get('error'):
                    lines.append(f"  Error: {self._colorize_error(db2['error'])}")
                
                # Display query that was executed
                if db2.get('query'):
                    lines.append(f"\n  Query: {db2['query']}")
                
                # Display query results if available
                if db2.get('query_results'):
                    lines.append(f"\n  Row Count: {db2.get('row_count', len(db2['query_results']))}")
                    lines.append("  Query Results:")
                    lines.append(self._format_query_results(db2['query_results']))
            lines.append("")
        
        # Kubernetes Results
        if 'kubernetes' in results.get('checks', {}):
            lines.append("--- Kubernetes Health Check ---")
            k8s = results['checks']['kubernetes']
            lines.append(f"  Status: {self._colorize_status(k8s.get('status', 'unknown'))}")
            lines.append(f"  Total Pods: {k8s.get('total_pods', 0)}")
            lines.append(f"  Healthy Pods: {k8s.get('healthy_pods', 0)}")
            
            if self.verbose and k8s.get('pods'):
                lines.append("\n  Pod Details:")
                for pod in k8s['pods']:
                    lines.append(f"    - {pod['name']}")
                    lines.append(f"      Phase: {pod['phase']}")
                    lines.append(f"      Ready: {pod['ready']}")
                    lines.append(f"      Restarts: {pod['restart_count']}")
                    lines.append(f"      Node: {pod['node']}")
                    
                    if pod.get('containers'):
                        lines.append("      Containers:")
                        for container in pod['containers']:
                            lines.append(f"        - {container['name']}: {container['state']}")
            
            if self.verbose:
                lines.append(f"\n  Details: {k8s.get('details', 'N/A')}")
                if k8s.get('error'):
                    lines.append(f"  Error: {self._colorize_error(k8s['error'])}")
                if k8s.get('warnings'):
                    lines.append("  Warnings:")
                    for warning in k8s['warnings']:
                        lines.append(f"    - {self._colorize_warning(warning)}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def _colorize_status(self, status: str) -> str:
        """Add color to status string.
        
        Args:
            status: Status string
            
        Returns:
            Colorized status (if colorama available)
        """
        if not COLORAMA_AVAILABLE:
            return status.upper()
        
        status_lower = status.lower()
        if status_lower == 'healthy':
            return f"{Fore.GREEN}{status.upper()}{Style.RESET_ALL}"
        elif status_lower == 'degraded':
            return f"{Fore.YELLOW}{status.upper()}{Style.RESET_ALL}"
        elif status_lower == 'unhealthy':
            return f"{Fore.RED}{status.upper()}{Style.RESET_ALL}"
        else:
            return status.upper()
    
    def _colorize_error(self, error: str) -> str:
        """Add color to error string.
        
        Args:
            error: Error string
            
        Returns:
            Colorized error (if colorama available)
        """
        if not COLORAMA_AVAILABLE:
            return error
        return f"{Fore.RED}{error}{Style.RESET_ALL}"
    
    def _colorize_warning(self, warning: str) -> str:
        """Add color to warning string.
        
        Args:
            warning: Warning string
            
        Returns:
            Colorized warning (if colorama available)
        """
        if not COLORAMA_AVAILABLE:
            return warning
        return f"{Fore.YELLOW}{warning}{Style.RESET_ALL}"
    
    def _format_query_results(self, results: list, max_rows: int = 100) -> str:
        """Format query results as a table.
        
        Args:
            results: List of row dictionaries
            max_rows: Maximum number of rows to display (default 100)
            
        Returns:
            Formatted table string
        """
        if not results:
            return "    (No results)"
        
        lines = []
        
        # Get column names from first row
        columns = list(results[0].keys())
        
        # Calculate column widths (min 10, max 40)
        col_widths = {}
        for col in columns:
            max_width = len(str(col))
            for row in results[:max_rows]:  # Only check rows we'll display
                val_width = len(str(row.get(col, '')))
                max_width = max(max_width, val_width)
            col_widths[col] = min(max(max_width, 10), 40)
        
        # Build header
        header = "    | " + " | ".join(
            str(col).ljust(col_widths[col])[:col_widths[col]] 
            for col in columns
        ) + " |"
        separator = "    +" + "+".join("-" * (col_widths[col] + 2) for col in columns) + "+"
        
        lines.append(separator)
        lines.append(header)
        lines.append(separator)
        
        # Build rows
        display_rows = results[:max_rows]
        for row in display_rows:
            row_str = "    | " + " | ".join(
                str(row.get(col, '')).ljust(col_widths[col])[:col_widths[col]]
                for col in columns
            ) + " |"
            lines.append(row_str)
        
        lines.append(separator)
        
        # Show truncation message if needed
        if len(results) > max_rows:
            lines.append(f"    ... ({len(results) - max_rows} more rows not shown)")
        
        return "\n".join(lines)


def format_output(results: Dict[str, Any], format_type: str = "json", verbose: bool = True) -> str:
    """Convenience function to format output.
    
    Args:
        results: Monitoring results
        format_type: Output format type
        verbose: Include verbose details
        
    Returns:
        Formatted output string
    """
    formatter = OutputFormatter(format_type, verbose)
    return formatter.format(results)
