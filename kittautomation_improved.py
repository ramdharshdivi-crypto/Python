#!/usr/bin/env python3
"""KITT Automation Tool - Improved Version

Multi-country KITT configuration templating and deployment automation.
This version includes improved error handling, type hints, and architecture.
"""

import os
import sys
import argparse
import subprocess
import logging
import json
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Optional, List, Dict, Any
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

# ================= CONSTANTS =================
BACKUP_DIR = ".kitt-backup"
CELL_PLACEHOLDER = "cell000"
COUNTRY_LABEL_KEY = "ccm.country"
DEFAULT_TASK_NAME = "deployApp"
DEFAULT_EXEC_SCOPE = "child"
CREATED_FILES_MANIFEST = "created-files.json"

# ================= LOGGING =================
def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging with optional verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    return logging.getLogger(__name__)


logger = setup_logging()

# ================= MAIN CLASS =================
class KITTAutomation:
    """KITT configuration automation manager."""

    def __init__(self, repo_path: str, backup_dir: str = BACKUP_DIR):
        """Initialize KITT automation.
        
        Args:
            repo_path: Path to the repository to process
            backup_dir: Directory for backups (relative to repo)
        """
        self.repo_path = Path(repo_path)
        self.backup_dir = self.repo_path / backup_dir
        self.change_report: List[Dict[str, Any]] = []
        self.created_files: List[str] = []
        
        # Setup YAML parser
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        
        self._validate_repo()

    def _validate_repo(self) -> None:
        """Validate repository path exists."""
        if not self.repo_path.is_dir():
            raise ValueError(f"Repository path does not exist: {self.repo_path}")
        logger.debug(f"Repository validated: {self.repo_path}")

    def ensure_dir(self, path: Path) -> None:
        """Ensure directory exists."""
        path.mkdir(parents=True, exist_ok=True)

    def backup_file(self, file_path: Path) -> None:
        """Backup a file before modification.
        
        Args:
            file_path: Path to file to backup
        """
        rel = file_path.relative_to(self.repo_path)
        backup_path = self.backup_dir / (str(rel) + ".bak")
        
        if backup_path.exists():
            logger.debug(f"Backup already exists: {backup_path}")
            return
        
        try:
            self.ensure_dir(backup_path.parent)
            shutil.copy2(file_path, backup_path)
            logger.debug(f"File backed up: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup {file_path}: {e}")
            raise

    def record_change(self, file: str, field: str, old: Any, new: Any) -> None:
        """Record a configuration change.
        
        Args:
            file: File where change occurred
            field: Field name that changed
            old: Old value
            new: New value
        """
        self.change_report.append({
            "file": file,
            "field": field,
            "old": str(old),
            "new": str(new)
        })

    def load_yaml(self, path: Path) -> CommentedMap:
        """Load and parse YAML file.
        
        Args:
            path: Path to YAML file
            
        Returns:
            Parsed YAML as CommentedMap
            
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        try:
            with open(path, "r") as f:
                return self.yaml.load(f) or CommentedMap()
        except FileNotFoundError:
            logger.error(f"YAML file not found: {path}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse YAML {path}: {e}")
            raise

    def write_yaml(self, path: Path, data: Any, dry_run: bool = False) -> None:
        """Write YAML to file with backup.
        
        Args:
            path: Path to write to
            data: Data to write
            dry_run: If True, don't actually write
        """
        if dry_run:
            logger.info(f"[DRY-RUN] Would write {path}")
            return
        
        try:
            self.backup_file(path)
            with open(path, "w") as f:
                self.yaml.dump(data, f)
            logger.debug(f"Written: {path}")
        except Exception as e:
            logger.error(f"Failed to write YAML {path}: {e}")
            raise

    # ================= FIX FUNCTIONS =================

    def fix_cluster_id(self, node: Any, cluster_id: str, file: str) -> None:
        """Recursively fix cluster_id fields.
        
        Args:
            node: Current node in YAML tree
            cluster_id: New cluster ID value
            file: File being processed (for logging)
        """
        if isinstance(node, dict):
            # Create list of keys to avoid mutation during iteration
            keys = list(node.keys())
            for k in keys:
                v = node[k]
                if k == "cluster_id":
                    old = v
                    seq = CommentedSeq([str(cluster_id)])
                    seq.fa.set_flow_style()  # Inline list format
                    node[k] = seq
                    self.record_change(file, "cluster_id", old, seq)
                else:
                    self.fix_cluster_id(v, cluster_id, file)
        elif isinstance(node, list):
            for i in node:
                self.fix_cluster_id(i, cluster_id, file)

    def fix_namespace(self, node: Any, namespace: str, file: str) -> None:
        """Recursively fix namespace fields.
        
        Args:
            node: Current node in YAML tree
            namespace: New namespace value
            file: File being processed (for logging)
        """
        if isinstance(node, dict):
            keys = list(node.keys())
            for k in keys:
                v = node[k]
                if k == "namespace":
                    old = v
                    node[k] = namespace
                    self.record_change(file, "namespace", old, namespace)
                else:
                    self.fix_namespace(v, namespace, file)
        elif isinstance(node, list):
            for i in node:
                self.fix_namespace(i, namespace, file)

    def fix_country(self, node: Any, country: str, file: str) -> None:
        """Recursively fix country labels.
        
        Args:
            node: Current node in YAML tree
            country: Country code
            file: File being processed (for logging)
        """
        if isinstance(node, dict):
            keys = list(node.keys())
            for k in keys:
                v = node[k]
                if k == "labels" and isinstance(v, dict):
                    if COUNTRY_LABEL_KEY in v:
                        old = v[COUNTRY_LABEL_KEY]
                        v[COUNTRY_LABEL_KEY] = country
                        self.record_change(file, COUNTRY_LABEL_KEY, old, country)
                self.fix_country(v, country, file)
        elif isinstance(node, list):
            for i in node:
                self.fix_country(i, country, file)

    def fix_cnames(self, node: Any, country: str, file: str) -> None:
        """Recursively fix CNAMEs with cell placeholder.
        
        Args:
            node: Current node in YAML tree
            country: Country code to replace cell000 with
            file: File being processed (for logging)
        """
        if isinstance(node, dict):
            keys = list(node.keys())
            for k in keys:
                v = node[k]
                if k == "cnames" and isinstance(v, list):
                    for idx, c in enumerate(v):
                        if CELL_PLACEHOLDER in c:
                            old = c
                            v[idx] = c.replace(CELL_PLACEHOLDER, country)
                            self.record_change(file, "cnames", old, v[idx])
                self.fix_cnames(v, country, file)
        elif isinstance(node, list):
            for i in node:
                self.fix_cnames(i, country, file)

    # ================= TEMPLATE FUNCTIONS =================

    def discover_templates(self, directory: Path) -> List[str]:
        """Discover KITT template files in directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of template filenames
        """
        if not directory.is_dir():
            return []
        
        templates = [
            f.name for f in directory.iterdir()
            if f.is_file() and f.name.startswith("kitt")
            and f.name.endswith(".yml")
            and (
                "primary" in f.name
                or "secondary" in f.name
                or f.name in ("kitt.primary.yml", "kitt.secondary.yml")
                or CELL_PLACEHOLDER in f.name
            )
        ]
        
        logger.debug(f"Discovered {len(templates)} templates in {directory}")
        return templates

    def create_country_files(
        self,
        directory: Path,
        countries: List[str],
        cluster_id: str,
        namespace: str,
        dry_run: bool = False
    ) -> List[str]:
        """Create country-specific KITT configuration files.
        
        Args:
            directory: Directory containing templates
            countries: List of country codes
            cluster_id: Cluster ID value
            namespace: Kubernetes namespace
            dry_run: If True, don't write files
            
        Returns:
            List of created filenames
        """
        created = []
        templates = self.discover_templates(directory)
        
        for tpl in templates:
            src_path = directory / tpl
            
            try:
                base = self.load_yaml(src_path)
            except Exception as e:
                logger.error(f"Failed to load template {tpl}: {e}")
                continue

            for country in countries:
                # Generate destination filename
                dest = tpl.replace(CELL_PLACEHOLDER, country)\
                           .replace("us-wm", country)
                if dest == tpl:
                    dest = f"kitt.{country}.{tpl.replace('kitt.', '')}"

                dest_path = directory / dest
                
                # Skip if already exists
                if dest_path.exists():
                    logger.debug(f"File already exists, skipping: {dest_path}")
                    continue

                # Apply transformations
                data = deepcopy(base)
                self.fix_cluster_id(data, cluster_id, dest)
                self.fix_namespace(data, namespace, dest)
                self.fix_country(data, country, dest)
                self.fix_cnames(data, country, dest)

                # Write file
                if not dry_run:
                    try:
                        # Use O_EXCL to prevent race conditions
                        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                        fd = os.open(str(dest_path), flags, 0o644)
                        with os.fdopen(fd, 'w') as f:
                            self.yaml.dump(data, f)
                        
                        rel_path = dest_path.relative_to(self.repo_path)
                        self.created_files.append(str(rel_path))
                        created.append(dest)
                        logger.info(f"Created {dest}")
                    except FileExistsError:
                        logger.warning(f"File already exists (race condition?): {dest_path}")
                    except Exception as e:
                        logger.error(f"Failed to create {dest}: {e}")
                        raise
                else:
                    logger.info(f"[DRY-RUN] Would create {dest}")
                    created.append(dest)

        return created

    # ================= PIPELINE FUNCTIONS =================

    def update_pipeline(
        self,
        directory: Path,
        created_files: List[str],
        dry_run: bool = False
    ) -> None:
        """Update KITT pipeline with newly created files.
        
        Args:
            directory: Directory containing kitt.yml
            created_files: List of created filenames
            dry_run: If True, don't write changes
        """
        if not created_files:
            return
        
        kitt_path = directory / "kitt.yml"
        if not kitt_path.exists():
            logger.debug(f"No kitt.yml found in {directory}")
            return

        try:
            data = self.load_yaml(kitt_path)
        except Exception as e:
            logger.error(f"Failed to load {kitt_path}: {e}")
            return

        post = data.get("build", {}).get("postBuild")
        if not isinstance(post, list):
            logger.warning(
                f"No postBuild list found in {kitt_path}. "
                "Skipping pipeline update."
            )
            return

        dir_name = directory.name
        for f in created_files:
            post.append(CommentedMap({
                "task": CommentedMap({
                    "name": DEFAULT_TASK_NAME,
                    "kittFilePath": f"{dir_name}/{f}",
                    "sha": DQ("{{$.kitt.build.commitEvent.commitId}}"),
                    "branch":DQ("{{$.kitt.build.commitEvent.currentBranch}}"),
                    "sync": False,
                    "executionScope": DEFAULT_EXEC_SCOPE
                })
            }))

        self.write_yaml(kitt_path, data, dry_run)
        logger.info(f"Updated pipeline in {directory}")

    # ================= MAIN PROCESSING =================

    def process(
        self,
        countries: List[str],
        cluster_id: str,
        namespace: str,
        dry_run: bool = False
    ) -> None:
        """Process entire repository.
        
        Args:
            countries: List of country codes
            cluster_id: Cluster ID value
            namespace: Kubernetes namespace
            dry_run: If True, don't write changes
        """
        logger.info(f"Processing repository: {self.repo_path}")
        logger.info(f"Countries: {countries}")
        logger.info(f"Cluster ID: {cluster_id}")
        logger.info(f"Namespace: {namespace}")
        
        # Walk repository
        for root, _, files in os.walk(self.repo_path):
            root_path = Path(root)
            
            # Check if this directory has KITT files
            if not any(f.startswith("kitt") for f in files):
                continue
            
            logger.debug(f"Processing directory: {root}")
            
            # Create country files
            created = self.create_country_files(
                root_path, countries, cluster_id, namespace, dry_run
            )
            
            # Update pipeline if files were created
            if created:
                self.update_pipeline(root_path, created, dry_run)

    def persist_state(self) -> None:
        """Save created files manifest and change report."""
        # Save created files manifest
        if self.created_files:
            manifest_path = self.backup_dir / CREATED_FILES_MANIFEST
            try:
                self.ensure_dir(manifest_path.parent)
                with open(manifest_path, "w") as f:
                    json.dump(self.created_files, f, indent=2)
                logger.info(f"Manifest saved: {manifest_path}")
            except Exception as e:
                logger.error(f"Failed to save manifest: {e}")
                raise

    def generate_report(self, output_path: str) -> None:
        """Generate and save change report.
        
        Args:
            output_path: Path to save report
        """
        if not self.change_report:
            logger.info("No changes to report")
            return
        
        try:
            with open(output_path, "w") as f:
                json.dump(self.change_report, f, indent=2)
            logger.info(f"Change report written to {output_path}")
        except Exception as e:
            logger.error(f"Failed to write report: {e}")
            raise

    # ================= ROLLBACK =================

    def rollback(self) -> None:
        """Rollback all changes made by process().
        
        Raises:
            ValueError: If no backup directory found
        """
        if not self.backup_dir.exists():
            raise ValueError(f"No backup directory found: {self.backup_dir}")
        
        logger.info("Starting rollback...")
        
        # Restore backed up files
        for backup_file in self.backup_dir.rglob("*.bak"):
            original_path = self.repo_path / backup_file.relative_to(self.backup_dir).with_suffix('')
            
            try:
                self.ensure_dir(original_path.parent)
                shutil.copy2(backup_file, original_path)
                logger.info(f"Restored {original_path}")
            except Exception as e:
                logger.error(f"Failed to restore {original_path}: {e}")
                raise

        # Delete created files
        manifest_path = self.backup_dir / CREATED_FILES_MANIFEST
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    created_files = json.load(f)

                for rel_path in created_files:
                    abs_path = self.repo_path / rel_path
                    if abs_path.exists():
                        abs_path.unlink()
                        logger.info(f"Deleted {abs_path}")
            except Exception as e:
                logger.error(f"Failed to delete created files: {e}")
                raise

        logger.info("Rollback completed successfully")


# ================= CLI =================
def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="KITT multi-country configuration automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process repository
  python kittautomation.py --repo . --countries us,uk --cluster-id primary --namespace prod
  
  # Dry run
  python kittautomation.py --repo . --countries us,uk --cluster-id primary --namespace prod --dry-run
  
  # Rollback changes
  python kittautomation.py --repo . --rollback
        """
    )
    
    parser.add_argument("--repo", required=True, help="Repository path")
    parser.add_argument("--countries", help="Comma-separated country codes")
    parser.add_argument("--cluster-id", help="Cluster ID value")
    parser.add_argument("--namespace", help="Kubernetes namespace")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--rollback", action="store_true", help="Rollback changes")
    parser.add_argument(
        "--report",
        default="kitt-change-report.json",
        help="Change report output path"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        automation = KITTAutomation(args.repo)
        
        if args.rollback:
            automation.rollback()
            return
        
        # Validate required arguments
        if not args.countries or not args.cluster_id or not args.namespace:
            parser.error(
                "--countries, --cluster-id, and --namespace are required "
                "(unless using --rollback)"
            )
        
        # Process repository
        countries = [c.strip() for c in args.countries.split(",")]
        automation.process(
            countries,
            args.cluster_id,
            args.namespace,
            args.dry_run
        )
        
        automation.persist_state()
        automation.generate_report(args.report)
        
        # Show git diff
        if not args.dry_run:
            subprocess.run(["git", "diff"], cwd=args.repo)
        
        logger.info("Completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
