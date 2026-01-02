#!/usr/bin/env python3
"""Enterprise Spring Boot Repository Analyzer.

A comprehensive tool for analyzing Spring Boot repositories and extracting
architectural, dependency, and configuration information.

Usage:
    python main.py --repo /path/to/repo --out analysis-output
"""

import sys
import logging
import argparse
from pathlib import Path
import os

# Fix: Add the script's directory to Python path for imports
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))
os.chdir(script_dir)  # Change to script directory

from analyzer import RepoAnalyzer
from exporters import CsvExporter, MarkdownExporter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enterprise Spring Boot Repository Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a repository
  python main.py --repo /path/to/spring-boot-repo
  
  # Analyze and specify output directory
  python main.py --repo /path/to/repo --out my-analysis
  
  # Analyze with detailed logging
  python main.py --repo /path/to/repo --verbose
        """
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Path to local Git repository to analyze"
    )

    parser.add_argument(
        "--out",
        default="repo-analysis-output",
        help="Output directory for analysis results (default: repo-analysis-output)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--no-md",
        action="store_true",
        help="Skip markdown summary generation"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Validate repo path
    repo_root = Path(args.repo).resolve()
    if not repo_root.exists():
        logger.error(f"Repository path does not exist: {repo_root}")
        sys.exit(1)

    if not repo_root.is_dir():
        logger.error(f"Path is not a directory: {repo_root}")
        sys.exit(1)

    # Check for Java files
    java_files = list(repo_root.rglob("*.java"))
    if not java_files:
        logger.warning(f"No Java files found in {repo_root}")

    logger.info(f"Starting analysis of {repo_root}")
    logger.info(f"Found {len(java_files)} Java files")

    # Setup output directory
    output_dir = repo_root / args.out
    logger.info(f"Output directory: {output_dir}")

    try:
        # Run analysis
        analyzer = RepoAnalyzer(repo_root)
        result = analyzer.analyze()
        summary = analyzer.get_analysis_summary()

        logger.info("Analysis complete!")
        logger.info(f"Summary: {summary}")

        # Export to CSV
        logger.info("Exporting to CSV...")
        csv_exporter = CsvExporter(output_dir)
        csv_exporter.export_all(result)
        logger.info("CSV export complete")

        # Export to Markdown
        if not args.no_md:
            logger.info("Exporting to Markdown...")
            md_exporter = MarkdownExporter(output_dir)
            md_exporter.export_summary(result, summary)
            logger.info("Markdown export complete")

        # Print summary
        print("\n" + "="*60)
        print("[OK] ANALYSIS COMPLETE!")
        print("="*60)
        print(f"\nResults saved to: {output_dir}\n")
        print("[SUMMARY] Statistics:")
        for key, value in summary.items():
            readable_key = key.replace("_", " ").title()
            print(f"  {readable_key}: {value}")
        print("\n[OUTPUT] Files:")
        print("  01_services.csv - All detected services")
        print("  02_api_endpoints.csv - REST API endpoints")
        print("  03_kafka_flows.csv - Kafka topics and flows")
        print("  04_database_connections.csv - Database connections")
        print("  05_configurations.csv - Configuration properties")
        print("  06_error_handlers.csv - Error handling setup")
        print("  07_resilience_patterns.csv - Retry, circuit breaker, etc.")
        print("  08_security_config.csv - Authentication & authorization")
        print("  09_data_models.csv - DTOs, Entities, Models")
        print("  10_service_dependencies.csv - Service dependencies")
        print("  11_observability.csv - Logging, metrics, health checks")
        print("  README.md - Summary report (if not skipped)")
        print("\n" + "="*60 + "\n")

        return 0

    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        print(f"\n❌ ERROR: Analysis failed - {e}\n", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
