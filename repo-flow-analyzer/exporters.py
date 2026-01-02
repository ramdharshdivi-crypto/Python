"""Export analysis results to CSV and Markdown formats.

Provides various output formats tailored for developer consumption.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any
from models import AnalysisResult


class CsvExporter:
    """Exports analysis results to CSV files."""

    def __init__(self, output_dir: Path):
        """Initialize exporter.

        Args:
            output_dir: Directory to write CSV files to
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def export_all(self, result: AnalysisResult) -> None:
        """Export all analysis results.

        Args:
            result: AnalysisResult object to export
        """
        self.export_services(result)
        self.export_endpoints(result)
        self.export_kafka(result)
        self.export_databases(result)
        self.export_configurations(result)
        self.export_error_handlers(result)
        self.export_resilience(result)
        self.export_security(result)
        self.export_data_models(result)
        self.export_dependencies(result)
        self.export_observability(result)

    def export_services(self, result: AnalysisResult) -> None:
        """Export services information."""
        rows = []
        for service in result.services:
            rows.append({
                "Service Name": service.service_name,
                "Type": service.service_type,
                "File": service.file_path,
                "Async": "Yes" if service.is_async else "No",
                "Reactive": "Yes" if service.is_reactive else "No",
                "Endpoint Count": len(service.endpoints),
                "Health Check": service.health_check_endpoint or "N/A",
            })
        self._write_csv("01_services.csv", rows)

    def export_endpoints(self, result: AnalysisResult) -> None:
        """Export REST endpoints."""
        rows = []
        for endpoint in result.rest_endpoints:
            rows.append({
                "Method": endpoint.method,
                "Path": endpoint.path,
                "Request Body": endpoint.request_body_type or "None",
                "Response Type": endpoint.response_type or "None",
                "Response Status": ", ".join(endpoint.response_status_codes) if endpoint.response_status_codes else "200",
                "Produces": endpoint.produces or "application/json",
                "Consumes": endpoint.consumes or "application/json",
                "Auth Required": "Yes" if endpoint.requires_auth else "No",
                "Auth Type": endpoint.auth_type.value if endpoint.auth_type else "None",
                "File": endpoint.file_path,
            })
        self._write_csv("02_api_endpoints.csv", rows)

    def export_kafka(self, result: AnalysisResult) -> None:
        """Export Kafka flows."""
        rows = []
        for flow in result.kafka_flows:
            rows.append({
                "Topic": flow.topic,
                "Direction": flow.direction,
                "Implementation": flow.implementation,
                "Message Type": flow.message_type or "Unknown",
                "Serialization": flow.serialization_format or "JSON (default)",
                "Consumer Group": flow.consumer_group or "Default",
                "Has DLT": "Yes" if flow.has_dlt else "No",
                "DLT Topic": flow.dlt_topic or "N/A",
                "File": flow.file_path,
            })
        self._write_csv("03_kafka_flows.csv", rows)

    def export_databases(self, result: AnalysisResult) -> None:
        """Export database connections."""
        rows = []
        for db in result.database_connections:
            rows.append({
                "Database Type": db.db_type,
                "Access Type": db.access_type.value,
                "Tables/Indices": ", ".join(db.tables) if db.tables else ", ".join(db.entities) if db.entities else "Runtime resolved",
                "Connection Pooling": "Yes" if db.has_connection_pooling else "No",
                "Pool Size": db.pool_size or "Default",
                "Has Query Annotations": "Yes" if db.query_annotations_found else "No",
                "Stored Procedures": ", ".join(db.stored_procedures) if db.stored_procedures else "None",
                "File": db.file_path,
            })
        self._write_csv("04_database_connections.csv", rows)

    def export_configurations(self, result: AnalysisResult) -> None:
        """Export configuration properties."""
        rows = []
        for config in result.configurations:
            rows.append({
                "Property Name": config.property_name,
                "Property Key": config.property_key,
                "Default Value": config.default_value or "N/A",
                "Required": "Yes" if config.is_required else "No",
                "Source": config.source,
                "File": config.file_path,
            })
        self._write_csv("05_configurations.csv", rows)

    def export_error_handlers(self, result: AnalysisResult) -> None:
        """Export error handlers."""
        rows = []
        for handler in result.error_handlers:
            rows.append({
                "Handler Name": handler.handler_name,
                "Exception Types": ", ".join(handler.exception_types),
                "Return Type": handler.return_type or "ResponseEntity",
                "Global Handler": "Yes" if handler.is_global else "No",
                "File": handler.file_path,
            })
        self._write_csv("06_error_handlers.csv", rows)

    def export_resilience(self, result: AnalysisResult) -> None:
        """Export resilience patterns."""
        rows = []
        for pattern in result.resilience_patterns:
            rows.append({
                "Pattern Type": pattern.pattern_type.value,
                "Target": pattern.target_service_or_operation,
                "Configuration": ", ".join([f"{k}={v}" for k, v in pattern.config_details.items()]) if pattern.config_details else "Default",
                "File": pattern.file_path,
            })
        self._write_csv("07_resilience_patterns.csv", rows)

    def export_security(self, result: AnalysisResult) -> None:
        """Export security configurations."""
        rows = []
        for config in result.security_configs:
            rows.append({
                "Authentication Type": config.auth_type.value,
                "Secured Endpoints": ", ".join(config.secured_endpoints) if config.secured_endpoints else "None",
                "Roles": ", ".join(config.roles_required) if config.roles_required else "None",
                "Permissions": ", ".join(config.permissions_required) if config.permissions_required else "None",
                "CORS Enabled": "Yes" if config.has_cors else "No",
                "JWT Secret Ref": config.jwt_secret_ref or "N/A",
                "File": config.file_path,
            })
        self._write_csv("08_security_config.csv", rows)

    def export_data_models(self, result: AnalysisResult) -> None:
        """Export data models."""
        rows = []
        for model in result.data_models:
            rows.append({
                "Class Name": model.class_name,
                "Model Type": model.model_type,
                "Serializable": "Yes" if model.is_serializable else "No",
                "Uses Lombok": "Yes" if model.has_lombok else "No",
                "Field Count": len(model.fields),
                "Validations": ", ".join(model.validations) if model.validations else "None",
                "File": model.file_path,
            })
        self._write_csv("09_data_models.csv", rows)

    def export_dependencies(self, result: AnalysisResult) -> None:
        """Export service dependencies."""
        rows = []
        for dep in result.service_dependencies:
            rows.append({
                "Source Service": dep.source_service,
                "Target Service": dep.target_service,
                "Flow Type": dep.flow_type.value,
                "Dependency Type": dep.dependency_type,
                "Method Called": dep.method_called or "N/A",
                "Source File": dep.source_file,
                "Target File": dep.target_file if dep.target_file else "Not found",
            })
        self._write_csv("10_service_dependencies.csv", rows)

    def export_observability(self, result: AnalysisResult) -> None:
        """Export observability configuration."""
        rows = []
        for config in result.observability_configs:
            rows.append({
                "Has Logging": "Yes" if config.has_logging else "No",
                "Logger Type": config.logger_type or "None",
                "Tracks Correlation ID": "Yes" if config.tracks_correlation_id else "No",
                "Has Metrics": "Yes" if config.has_metrics else "No",
                "Metrics Type": config.metrics_type or "None",
                "Has Health Check": "Yes" if config.has_health_check else "No",
                "Health Check Path": config.health_check_path or "N/A",
                "File": config.file_path,
            })
        self._write_csv("11_observability.csv", rows)

    def _write_csv(self, filename: str, rows: List[Dict[str, Any]]) -> None:
        """Write rows to CSV file.

        Args:
            filename: Output filename
            rows: List of dictionaries to write
        """
        if not rows:
            return

        filepath = self.output_dir / filename
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)


class MarkdownExporter:
    """Exports analysis results to Markdown files."""

    def __init__(self, output_dir: Path):
        """Initialize exporter.

        Args:
            output_dir: Directory to write markdown files to
        """
        self.output_dir = output_dir

    def export_summary(self, result: AnalysisResult, summary: Dict[str, int]) -> None:
        """Export analysis summary.

        Args:
            result: AnalysisResult object
            summary: Summary statistics
        """
        md_file = self.output_dir / "README.md"

        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# Repository Analysis Report\n\n")
            f.write("## Summary Statistics\n\n")
            f.write("| Metric | Count |\n")
            f.write("|--------|-------|\n")
            for key, value in summary.items():
                readable_key = key.replace("_", " ").title()
                f.write(f"| {readable_key} | {value} |\n")

            f.write("\n## Services\n\n")
            for service in result.services:
                f.write(f"### {service.service_name}\n\n")
                f.write(f"- **Type**: {service.service_type}\n")
                f.write(f"- **File**: `{service.file_path}`\n")
                f.write(f"- **Async**: {'Yes' if service.is_async else 'No'}\n")
                f.write(f"- **Reactive**: {'Yes' if service.is_reactive else 'No'}\n")
                f.write(f"- **Endpoints**: {len(service.endpoints)}\n")
                f.write("\n")

            f.write("## API Endpoints\n\n")
            for endpoint in result.rest_endpoints:
                f.write(f"### {endpoint.method} {endpoint.path}\n\n")
                f.write(f"- **File**: `{endpoint.file_path}`\n")
                f.write(f"- **Auth Required**: {'Yes' if endpoint.requires_auth else 'No'}\n")
                f.write(f"- **Request**: {endpoint.request_body_type or 'None'}\n")
                f.write(f"- **Response**: {endpoint.response_type or 'None'}\n")
                f.write("\n")

            f.write("## Kafka Flows\n\n")
            for flow in result.kafka_flows:
                f.write(f"### {flow.direction} - {flow.topic}\n\n")
                f.write(f"- **Implementation**: {flow.implementation}\n")
                f.write(f"- **Serialization**: {flow.serialization_format or 'JSON (default)'}\n")
                f.write(f"- **DLT**: {'Yes' if flow.has_dlt else 'No'}\n")
                f.write(f"- **File**: `{flow.file_path}`\n")
                f.write("\n")

            f.write("## Database Connections\n\n")
            for db in result.database_connections:
                f.write(f"### {db.db_type}\n\n")
                f.write(f"- **Access Type**: {db.access_type.value}\n")
                f.write(f"- **Tables/Entities**: {', '.join(db.tables or db.entities) or 'Runtime resolved'}\n")
                f.write(f"- **Connection Pooling**: {'Yes' if db.has_connection_pooling else 'No'}\n")
                f.write(f"- **File**: `{db.file_path}`\n")
                f.write("\n")

            f.write("## Security Configuration\n\n")
            for config in result.security_configs:
                if config.auth_type.value != "None":
                    f.write(f"- **Auth Type**: {config.auth_type.value}\n")
                    if config.secured_endpoints:
                        f.write(f"  - **Endpoints**: {', '.join(config.secured_endpoints)}\n")
                    if config.roles_required:
                        f.write(f"  - **Roles**: {', '.join(config.roles_required)}\n")
                    f.write(f"  - **File**: `{config.file_path}`\n")
                f.write("\n")
