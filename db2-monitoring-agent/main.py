#!/usr/bin/env python3
"""Main entry point for DB2 and Kubernetes monitoring agent."""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_loader import load_config
from db2_checker import check_db2_health, is_db2_available, get_db2_driver_info
from k8s_checker import check_k8s_health
from output_formatter import format_output


def setup_logging(log_file: str = None, verbose: bool = False) -> None:
    """Set up logging configuration.
    
    Args:
        log_file: Path to log file (optional)
        verbose: Enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )


def run_checks(config: Dict[str, Any], check_type: str = 'all', batch_id: str = None) -> Dict[str, Any]:
    """Run monitoring checks.
    
    Args:
        config: Configuration dictionary
        check_type: Type of check to run ('all', 'db2', 'k8s')
        batch_id: Optional batch ID to substitute in DB2 query placeholder {batch_id}
        
    Returns:
        Results dictionary
    """
    results = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'checks': {},
        'overall_status': 'healthy'
    }
    
    # Run DB2 check
    if check_type in ['all', 'db2'] and 'db2' in config:
        if not is_db2_available():
            logging.warning("DB2 driver not available - skipping DB2 check")
            driver_info = get_db2_driver_info()
            results['checks']['db2'] = {
                'status': 'skipped',
                'error': 'No DB2 driver available',
                'details': (
                    'Please install one of:\n'
                    '  1. ibm_db (requires IBM Data Server Driver)\n'
                    '  2. pyodbc (with DB2 ODBC driver configured)\n'
                    'See README.md for installation instructions.'
                ),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        else:
            logging.info("Running DB2 health check...")
            try:
                # Make a copy of db2 config to avoid modifying original
                db2_config = config['db2'].copy()
                
                # Substitute {batch_id} placeholder in query if batch_id provided
                if batch_id and 'query' in db2_config:
                    original_query = db2_config['query']
                    db2_config['query'] = original_query.replace('{batch_id}', batch_id)
                    logging.info(f"Using batch_id: {batch_id}")
                    logging.debug(f"Query after substitution: {db2_config['query']}")
                elif '{batch_id}' in db2_config.get('query', ''):
                    logging.warning("Query contains {batch_id} placeholder but no --batch-id argument provided!")
                
                db2_result = check_db2_health(db2_config)
                results['checks']['db2'] = db2_result
                
                if db2_result['status'] not in ['healthy', 'skipped']:
                    results['overall_status'] = 'unhealthy'
                
                logging.info(f"DB2 check completed: {db2_result['status']}")
            except Exception as e:
                logging.error(f"DB2 check failed: {str(e)}")
                results['checks']['db2'] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                results['overall_status'] = 'unhealthy'
    
    # Run Kubernetes check
    if check_type in ['all', 'k8s'] and 'kubernetes' in config:
        logging.info("Running Kubernetes health check...")
        try:
            # Merge alert config if available
            k8s_config = config['kubernetes'].copy()
            if 'monitoring' in config and 'alert' in config['monitoring']:
                k8s_config['alert'] = config['monitoring']['alert']
            
            k8s_result = check_k8s_health(k8s_config)
            results['checks']['kubernetes'] = k8s_result
            
            if k8s_result['status'] in ['unhealthy', 'degraded']:
                results['overall_status'] = k8s_result['status']
            
            logging.info(f"Kubernetes check completed: {k8s_result['status']}")
        except Exception as e:
            logging.error(f"Kubernetes check failed: {str(e)}")
            results['checks']['kubernetes'] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            results['overall_status'] = 'unhealthy'
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Monitor DB2 database and Kubernetes pods',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all checks with default config
  python main.py
  
  # Use custom config file
  python main.py --config /path/to/config.yaml
  
  # Check only DB2 with a specific batch ID
  python main.py --check db2 --batch-id 368451
  
  # Check only Kubernetes
  python main.py --check k8s
  
  # Output as text instead of JSON
  python main.py --format text
  
  # Run DB2 check with batch ID and verbose output
  python main.py --check db2 --batch-id 123456 --verbose
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--check',
        type=str,
        choices=['all', 'db2', 'k8s'],
        default='all',
        help='Type of check to run (default: all)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'text'],
        default=None,
        help='Output format (default: from config or json)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output and logging'
    )
    
    parser.add_argument(
        '--check-drivers',
        action='store_true',
        help='Check DB2 driver availability and exit'
    )
    
    parser.add_argument(
        '--batch-id',
        type=str,
        default=None,
        help='Batch ID to use in the DB2 query (replaces {batch_id} placeholder in config)'
    )
    
    args = parser.parse_args()
    
    # Check drivers if requested
    if args.check_drivers:
        driver_info = get_db2_driver_info()
        print("\n=== DB2 Driver Status ===")
        print(f"Available: {driver_info['available']}")
        print(f"Driver Type: {driver_info['driver_type'] or 'None'}")
        print(f"Driver Module: {driver_info['driver_module'] or 'None'}")
        print("\nInstallation Instructions:")
        print("  Option 1 - IBM DB2 Driver (ibm_db):")
        print("    1. Download IBM Data Server Driver from IBM website")
        print("    2. Install the driver package")
        print("    3. Run: pip install ibm_db")
        print("\n  Option 2 - ODBC Driver (pyodbc):")
        print("    1. Install DB2 ODBC driver on your system")
        print("    2. Configure ODBC data source")
        print("    3. Run: pip install pyodbc")
        print("\nSee README.md for detailed instructions.\n")
        return 0 if driver_info['available'] else 1
    
    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return 1
    
    # Setup logging
    log_file = config.get('output', {}).get('log_file')
    verbose = args.verbose or config.get('output', {}).get('verbose', False)
    setup_logging(log_file, verbose)
    
    logging.info("Starting monitoring agent...")
    
    # Run checks
    results = run_checks(config, args.check, batch_id=args.batch_id)
    
    # Format output
    output_format = args.format or config.get('output', {}).get('format', 'json')
    output = format_output(results, output_format, verbose)
    
    # Print output
    print(output)
    
    # Return exit code based on overall status
    if results['overall_status'] == 'healthy':
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
