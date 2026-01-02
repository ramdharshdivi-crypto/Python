"""Individual extractors for different analysis types.

Each extractor focuses on a specific aspect of the codebase.
"""

import re
from pathlib import Path
from typing import List, Set, Dict, Optional, Tuple
from models import (
    Service, RestEndpoint, KafkaFlow, DatabaseConnection, Configuration,
    ErrorHandler, ResiliencePattern, SecurityConfig, DataModel,
    ObservabilityConfig, ServiceDependency, FlowType, AuthType, AccessType,
    ResilienceType
)
from patterns import get_patterns


class BaseExtractor:
    """Base extractor class with common utilities."""

    def __init__(self):
        self.patterns = get_patterns()

    def extract_text_in_parentheses(self, text: str, start: int) -> Optional[str]:
        """Extract balanced parentheses content."""
        depth = 0
        in_quotes = False
        for i in range(start, len(text)):
            if text[i] == '"' and (i == 0 or text[i-1] != '\\'):
                in_quotes = not in_quotes
            elif not in_quotes:
                if text[i] == '(':
                    depth += 1
                elif text[i] == ')':
                    depth -= 1
                    if depth == 0:
                        return text[start+1:i]
        return None


class RestEndpointExtractor(BaseExtractor):
    """Extracts REST endpoint information."""

    def extract(self, content: str, file_path: str) -> List[RestEndpoint]:
        """Extract all REST endpoints from file."""
        endpoints = []

        if not self.patterns.REST_CONTROLLER.search(content):
            return endpoints

        # Extract base path if RequestMapping exists at class level
        class_mapping = self.patterns.REQUEST_MAPPING.search(content)
        base_path = class_mapping.group(2) if class_mapping else ""

        for match in self.patterns.REQUEST_MAPPING.finditer(content):
            method = match.group(1)
            path = match.group(2)
            full_path = base_path + path

            # Map annotation to HTTP method
            http_method = self._map_to_http_method(method)

            endpoint = RestEndpoint(
                file_path=str(file_path),
                method=http_method,
                path=full_path,
                produces=self._extract_attribute(content, match.start(), "produces"),
                consumes=self._extract_attribute(content, match.start(), "consumes"),
            )

            endpoints.append(endpoint)

        return endpoints

    def _map_to_http_method(self, annotation: str) -> str:
        """Map Spring annotation to HTTP method."""
        mapping = {
            "GetMapping": "GET",
            "PostMapping": "POST",
            "PutMapping": "PUT",
            "DeleteMapping": "DELETE",
            "PatchMapping": "PATCH",
            "RequestMapping": "ALL",
        }
        return mapping.get(annotation, "GET")

    def _extract_attribute(self, content: str, start: int, attr: str) -> Optional[str]:
        """Extract attribute value from annotation."""
        pattern = re.compile(rf"{attr}\s*=\s*\"([^\"]+)\"")
        match = pattern.search(content, start, min(start + 500, len(content)))
        return match.group(1) if match else None


class ServiceDependencyExtractor(BaseExtractor):
    """Extracts service-to-service dependencies."""

    def extract(self, content: str, file_path: str) -> List[ServiceDependency]:
        """Extract all service dependencies."""
        dependencies = []

        # Find @Autowired dependencies
        for match in self.patterns.AUTOWIRED.finditer(content):
            # Try to extract the field type and name after @Autowired
            end_pos = match.end()
            line_end = content.find("\n", end_pos)
            field_decl = content[end_pos:line_end]
            field_match = re.search(r"(\w+Service|\w+Client)\s+(\w+)", field_decl)

            if field_match:
                service_type = field_match.group(1)
                dep = ServiceDependency(
                    source_service=Path(file_path).stem,
                    target_service=service_type,
                    flow_type=FlowType.SYNC,
                    source_file=str(file_path),
                    target_file="",  # Will be resolved later
                    dependency_type="@Autowired",
                )
                dependencies.append(dep)

        # Find service method calls
        for match in self.patterns.SERVICE_CALL.finditer(content):
            service_name = match.group(1)
            method_name = match.group(2)
            dep = ServiceDependency(
                source_service=Path(file_path).stem,
                target_service=service_name,
                flow_type=FlowType.SYNC,
                source_file=str(file_path),
                target_file="",
                dependency_type="Method Call",
                method_called=method_name,
            )
            dependencies.append(dep)

        return dependencies


class KafkaExtractor(BaseExtractor):
    """Extracts Kafka event information."""

    def extract(self, content: str, file_path: str) -> List[KafkaFlow]:
        """Extract all Kafka event flows."""
        flows = []

        # Kafka consumers - WalmartKafkaListener
        for block in self.patterns.WALMART_KAFKA_LISTENER.findall(content):
            topic = self.patterns.TOPIC_EXTRACTOR.search(block)
            flows.append(KafkaFlow(
                file_path=str(file_path),
                topic=topic.group(1) if topic else "Unknown",
                direction="Consume",
                implementation="WalmartKafkaListener",
                has_dlt=self.patterns.DLT_LISTENER.search(block) is not None,
            ))

        # Kafka consumers - KafkaListener
        for block in self.patterns.SPRING_KAFKA_LISTENER.findall(content):
            topic = self.patterns.TOPIC_EXTRACTOR.search(block)
            flows.append(KafkaFlow(
                file_path=str(file_path),
                topic=topic.group(1) if topic else "Pattern/Unknown",
                direction="Consume",
                implementation="KafkaListener",
                has_dlt=self.patterns.DLT_LISTENER.search(block) is not None,
            ))

        # Kafka producers - KafkaTemplate
        if self.patterns.KAFKA_TEMPLATE_SEND.search(content):
            flows.append(KafkaFlow(
                file_path=str(file_path),
                topic="Resolved at runtime",
                direction="Produce",
                implementation="KafkaTemplate",
            ))

        return flows


class DatabaseExtractor(BaseExtractor):
    """Extracts database connection information."""

    def extract(self, content: str, file_path: str) -> List[DatabaseConnection]:
        """Extract all database connections."""
        connections = []

        # JDBC Template
        if self.patterns.JDBC_TEMPLATE.search(content):
            ops = set(m[0].upper() for m in self.patterns.SQL_OPERATION.findall(content))
            tables = {t for g in self.patterns.TABLE_EXTRACTOR.findall(content) for t in g if t}
            access = AccessType.READ_WRITE if {"INSERT", "UPDATE", "DELETE"} & ops else AccessType.READ

            connections.append(DatabaseConnection(
                file_path=str(file_path),
                db_type=self._detect_db_type(content, file_path),
                access_type=access,
                tables=tables,
                has_connection_pooling=bool(re.search(r"(HikariCP|c3p0|dbcp)", content)),
            ))

        # JPA/Hibernate
        for entity_match in self.patterns.JPA_ENTITY.finditer(content):
            entity_name = entity_match.group(1)
            connections.append(DatabaseConnection(
                file_path=str(file_path),
                db_type="JPA/Hibernate",
                access_type=AccessType.READ_WRITE,
                entities={entity_name},
                query_annotations_found=bool(self.patterns.QUERY_ANNOTATION.search(content)),
            ))

        # Elasticsearch
        if self.patterns.ELASTIC_CLIENT.search(content) or self.patterns.ELASTIC_INDEX.search(content):
            indices = self.patterns.ELASTIC_INDEX.findall(content)
            ops = self.patterns.ELASTIC_OPERATION.findall(content)
            access = AccessType.READ_WRITE if {"IndexRequest", "UpdateRequest", "DeleteRequest"} & set(ops) else AccessType.READ

            connections.append(DatabaseConnection(
                file_path=str(file_path),
                db_type="Elasticsearch",
                access_type=access,
                tables=set(indices),
            ))

        # Cassandra
        if self.patterns.CASSANDRA_DRIVER.search(content):
            ops = self._extract_cassandra_ops(content)
            access = AccessType.READ_WRITE if {"INSERT", "UPDATE", "DELETE"} & ops else AccessType.READ

            connections.append(DatabaseConnection(
                file_path=str(file_path),
                db_type="Cassandra",
                access_type=access,
            ))

        return connections

    def _detect_db_type(self, content: str, file_path: str) -> str:
        """Detect database type from content and file path."""
        combined = (content + " " + str(file_path)).lower()
        for db, indicators in self.patterns.DB_TYPE_INDICATORS.items():
            for ind in indicators:
                if ind in combined:
                    return db
        return "Unknown"

    def _extract_cassandra_ops(self, content: str) -> Set[str]:
        """Extract Cassandra operations."""
        ops = set()
        if re.search(r"insertInto", content, re.IGNORECASE):
            ops.add("INSERT")
        if re.search(r"selectFrom", content, re.IGNORECASE):
            ops.add("SELECT")
        if re.search(r"\bupdate\b", content, re.IGNORECASE):
            ops.add("UPDATE")
        if re.search(r"deleteFrom", content, re.IGNORECASE):
            ops.add("DELETE")
        return ops


class ConfigurationExtractor(BaseExtractor):
    """Extracts configuration properties."""

    def extract(self, content: str, file_path: str) -> List[Configuration]:
        """Extract all configuration properties."""
        configs = []

        # @Value annotations
        for match in self.patterns.VALUE_ANNOTATION.finditer(content):
            prop_key = match.group(1)
            configs.append(Configuration(
                file_path=str(file_path),
                property_name=prop_key.split(".")[-1],
                property_key=prop_key,
                source="@Value",
            ))

        # @ConfigurationProperties
        for match in self.patterns.CONFIG_PROPERTIES.finditer(content):
            prefix = match.group(1)
            configs.append(Configuration(
                file_path=str(file_path),
                property_name=prefix,
                property_key=prefix,
                source="@ConfigurationProperties",
            ))

        return configs


class ErrorHandlerExtractor(BaseExtractor):
    """Extracts error handling configuration."""

    def extract(self, content: str, file_path: str) -> List[ErrorHandler]:
        """Extract all error handlers."""
        handlers = []
        is_global = self.patterns.CONTROL_ADVICE.search(content) is not None

        for match in self.patterns.EXCEPTION_HANDLER.finditer(content):
            exceptions = match.group(1).split(",")
            handlers.append(ErrorHandler(
                file_path=str(file_path),
                handler_name="ExceptionHandler",
                exception_types=[e.strip() for e in exceptions],
                is_global=is_global,
            ))

        return handlers


class ResilienceExtractor(BaseExtractor):
    """Extracts resilience and fault tolerance patterns."""

    def extract(self, content: str, file_path: str) -> List[ResiliencePattern]:
        """Extract all resilience patterns."""
        patterns = []

        # Retry
        if self.patterns.RETRY_ANNOTATION.search(content):
            patterns.append(ResiliencePattern(
                file_path=str(file_path),
                pattern_type=ResilienceType.RETRY,
                target_service_or_operation="Generic",
            ))

        # Circuit Breaker
        if self.patterns.CIRCUIT_BREAKER.search(content):
            patterns.append(ResiliencePattern(
                file_path=str(file_path),
                pattern_type=ResilienceType.CIRCUIT_BREAKER,
                target_service_or_operation="Generic",
            ))

        # Timeout
        for match in self.patterns.TIMEOUT.finditer(content):
            patterns.append(ResiliencePattern(
                file_path=str(file_path),
                pattern_type=ResilienceType.TIMEOUT,
                target_service_or_operation="Generic",
                config_details={"timeout_ms": match.group(1) if match.lastindex and match.group(1) else "Unknown"},
            ))

        # Fallback
        if self.patterns.FALLBACK.search(content):
            patterns.append(ResiliencePattern(
                file_path=str(file_path),
                pattern_type=ResilienceType.FALLBACK,
                target_service_or_operation="Generic",
            ))

        # Rate Limit
        if self.patterns.RATE_LIMIT.search(content):
            patterns.append(ResiliencePattern(
                file_path=str(file_path),
                pattern_type=ResilienceType.RATE_LIMIT,
                target_service_or_operation="Generic",
            ))

        return patterns


class SecurityExtractor(BaseExtractor):
    """Extracts security configurations."""

    def extract(self, content: str, file_path: str) -> SecurityConfig:
        """Extract security configuration."""
        config = SecurityConfig(file_path=str(file_path))

        # Detect auth type
        if self.patterns.JWT_TOKEN.search(content):
            config.auth_type = AuthType.JWT
        elif self.patterns.OAUTH2_ANNOTATION.search(content):
            config.auth_type = AuthType.OAUTH2
        elif self.patterns.SPRING_SECURITY.search(content):
            config.auth_type = AuthType.SPRING_SECURITY

        # Extract secured endpoints
        for match in self.patterns.SECURED_ANNOTATION.finditer(content):
            roles = match.group(1).split(",")
            config.secured_endpoints.extend([r.strip() for r in roles])

        # Extract permissions from @PreAuthorize
        for match in self.patterns.PRE_AUTHORIZE.finditer(content):
            perms = match.group(1)
            config.permissions_required.add(perms)

        return config


class DataModelExtractor(BaseExtractor):
    """Extracts data models (DTOs, Entities, etc.)."""

    def extract(self, content: str, file_path: str) -> List[DataModel]:
        """Extract all data models."""
        models = []
        has_lombok = self.patterns.LOMBOK_DATA.search(content) is not None

        for match in self.patterns.DTO_CLASS.finditer(content):
            class_name = match.group(1)
            model_type = self._infer_model_type(class_name)

            model = DataModel(
                file_path=str(file_path),
                class_name=class_name,
                model_type=model_type,
                is_serializable=self.patterns.SERIALIZATION.search(content) is not None,
                has_lombok=has_lombok,
            )

            # Extract validations
            if self.patterns.VALIDATION.search(content):
                model.validations = self.patterns.VALIDATION.findall(content)

            models.append(model)

        return models

    def _infer_model_type(self, class_name: str) -> str:
        """Infer model type from class name."""
        if "DTO" in class_name:
            return "DTO"
        elif "Request" in class_name:
            return "Request"
        elif "Response" in class_name:
            return "Response"
        elif "Entity" in class_name:
            return "Entity"
        return "Model"


class ObservabilityExtractor(BaseExtractor):
    """Extracts observability and monitoring configuration."""

    def extract(self, content: str, file_path: str) -> ObservabilityConfig:
        """Extract observability configuration."""
        config = ObservabilityConfig(file_path=str(file_path))

        # Logging
        if self.patterns.SLF4J_LOGGER.search(content):
            config.has_logging = True
            config.logger_type = "SLF4J"
        elif self.patterns.LOGGER_DECLARATION.search(content):
            config.has_logging = True
            config.logger_type = "Log4j"

        # Correlation ID
        config.tracks_correlation_id = self.patterns.CORRELATION_ID.search(content) is not None

        # Metrics
        if self.patterns.METRICS.search(content):
            config.has_metrics = True
            config.metrics_type = "Micrometer"

        # Health check
        if self.patterns.HEALTH_CHECK.search(content):
            config.has_health_check = True
            config.health_check_path = "/actuator/health"

        return config
