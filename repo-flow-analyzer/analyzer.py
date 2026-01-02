"""Core repository analyzer orchestrating all extractors.

This module coordinates the analysis of a Spring Boot repository using
all available extractors.
"""

import logging
from pathlib import Path
from typing import List, Dict
from models import (
    AnalysisResult, Service, ServiceDependency, FlowType
)
from extractors import (
    RestEndpointExtractor, ServiceDependencyExtractor, KafkaExtractor,
    DatabaseExtractor, ConfigurationExtractor, ErrorHandlerExtractor,
    ResilienceExtractor, SecurityExtractor, DataModelExtractor,
    ObservabilityExtractor
)


logger = logging.getLogger(__name__)


class RepoAnalyzer:
    """Orchestrates analysis of Spring Boot repository."""

    def __init__(self, repo_root: Path):
        """Initialize analyzer.

        Args:
            repo_root: Root path of the repository to analyze
        """
        self.repo_root = repo_root.resolve()
        self.result = AnalysisResult()
        self.file_to_service_map: Dict[str, str] = {}  # file_path -> service_name

        # Initialize extractors
        self.rest_extractor = RestEndpointExtractor()
        self.dependency_extractor = ServiceDependencyExtractor()
        self.kafka_extractor = KafkaExtractor()
        self.database_extractor = DatabaseExtractor()
        self.config_extractor = ConfigurationExtractor()
        self.error_extractor = ErrorHandlerExtractor()
        self.resilience_extractor = ResilienceExtractor()
        self.security_extractor = SecurityExtractor()
        self.model_extractor = DataModelExtractor()
        self.observability_extractor = ObservabilityExtractor()

    def analyze(self) -> AnalysisResult:
        """Run complete analysis on repository.

        Returns:
            AnalysisResult containing all extracted information
        """
        logger.info(f"Starting analysis of {self.repo_root}")

        # First pass: analyze all Java files
        java_files = list(self.repo_root.rglob("*.java"))
        logger.info(f"Found {len(java_files)} Java files")

        for java_file in java_files:
            self._analyze_file(java_file)

        # Second pass: resolve service dependencies
        self._resolve_service_dependencies()

        # Third pass: enhance analysis with correlations
        self._correlate_services_with_endpoints()
        self._correlate_services_with_kafka()
        self._correlate_services_with_databases()

        logger.info(f"Analysis complete. Found {len(self.result.services)} services")
        return self.result

    def _analyze_file(self, java_file: Path) -> None:
        """Analyze a single Java file.

        Args:
            java_file: Path to Java file to analyze
        """
        try:
            content = java_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"Failed to read {java_file}: {e}")
            return

        # Extract REST endpoints
        endpoints = self.rest_extractor.extract(content, java_file)
        self.result.rest_endpoints.extend(endpoints)

        # Create service entry if REST controller found
        if endpoints:
            service_name = java_file.stem
            self.file_to_service_map[str(java_file)] = service_name
            service = Service(
                file_path=str(java_file),
                service_name=service_name,
                service_type="REST Controller",
                endpoints=endpoints,
            )
            self.result.services.append(service)

        # Extract Kafka flows
        kafka_flows = self.kafka_extractor.extract(content, java_file)
        self.result.kafka_flows.extend(kafka_flows)

        # Extract database connections
        databases = self.database_extractor.extract(content, java_file)
        self.result.database_connections.extend(databases)

        # Extract configurations
        configs = self.config_extractor.extract(content, java_file)
        self.result.configurations.extend(configs)

        # Extract error handlers
        error_handlers = self.error_extractor.extract(content, java_file)
        self.result.error_handlers.extend(error_handlers)

        # Extract resilience patterns
        resilience_patterns = self.resilience_extractor.extract(content, java_file)
        self.result.resilience_patterns.extend(resilience_patterns)

        # Extract security config
        security = self.security_extractor.extract(content, java_file)
        self.result.security_configs.append(security)

        # Extract data models
        models = self.model_extractor.extract(content, java_file)
        self.result.data_models.extend(models)

        # Extract observability
        observability = self.observability_extractor.extract(content, java_file)
        self.result.observability_configs.append(observability)

        # Extract service dependencies
        dependencies = self.dependency_extractor.extract(content, java_file)
        self.result.service_dependencies.extend(dependencies)

    def _resolve_service_dependencies(self) -> None:
        """Resolve service dependencies to actual services."""
        for dep in self.result.service_dependencies:
            # Try to find target service file
            for java_file in self.repo_root.rglob("*Service.java"):
                if dep.target_service.lower() in java_file.name.lower():
                    dep.target_file = str(java_file)
                    break

    def _correlate_services_with_endpoints(self) -> None:
        """Correlate endpoints with services."""
        for service in self.result.services:
            matching_endpoints = [
                ep for ep in self.result.rest_endpoints
                if ep.file_path == service.file_path
            ]
            service.endpoints = matching_endpoints

    def _correlate_services_with_kafka(self) -> None:
        """Correlate Kafka flows with services."""
        # This could be enhanced to determine which service handles which topic
        pass

    def _correlate_services_with_databases(self) -> None:
        """Correlate database connections with services."""
        # This could be enhanced to map services to their databases
        pass

    def get_analysis_summary(self) -> Dict[str, int]:
        """Get summary statistics of analysis.

        Returns:
            Dictionary with counts of various entities
        """
        return {
            "total_services": len(self.result.services),
            "total_endpoints": len(self.result.rest_endpoints),
            "total_kafka_flows": len(self.result.kafka_flows),
            "total_databases": len(self.result.database_connections),
            "total_configurations": len(self.result.configurations),
            "total_error_handlers": len(self.result.error_handlers),
            "total_resilience_patterns": len(self.result.resilience_patterns),
            "total_data_models": len(self.result.data_models),
            "total_dependencies": len(self.result.service_dependencies),
        }
