"""Data models for Enterprise Spring Boot Repo Analysis.

Using dataclasses for type safety and clarity.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum


class AccessType(Enum):
    """Database access types."""
    READ = "Read"
    WRITE = "Write"
    READ_WRITE = "Read/Write"


class FlowType(Enum):
    """Flow communication types."""
    SYNC = "Sync"
    ASYNC = "Async"
    REACTIVE = "Reactive"


class ResilienceType(Enum):
    """Resilience pattern types."""
    RETRY = "Retry"
    CIRCUIT_BREAKER = "Circuit Breaker"
    TIMEOUT = "Timeout"
    FALLBACK = "Fallback"
    RATE_LIMIT = "Rate Limit"


class AuthType(Enum):
    """Authentication types."""
    OAUTH2 = "OAuth2"
    JWT = "JWT"
    BASIC = "Basic Auth"
    API_KEY = "API Key"
    SPRING_SECURITY = "Spring Security"
    NONE = "None"


@dataclass
class RestEndpoint:
    """REST API endpoint information."""
    file_path: str
    method: str  # GET, POST, PUT, DELETE, etc.
    path: str
    path_variables: List[str] = field(default_factory=list)
    query_parameters: List[str] = field(default_factory=list)
    request_body_type: Optional[str] = None
    response_type: Optional[str] = None
    response_status_codes: Set[str] = field(default_factory=set)
    produces: Optional[str] = None
    consumes: Optional[str] = None
    requires_auth: bool = False
    auth_type: AuthType = AuthType.NONE


@dataclass
class Service:
    """Spring Service information."""
    file_path: str
    service_name: str
    service_type: str  # REST Controller, Service, Component, Repository
    endpoints: List[RestEndpoint] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Other services it depends on
    methods: List[str] = field(default_factory=list)
    is_async: bool = False
    is_reactive: bool = False
    health_check_endpoint: Optional[str] = None
    security_config: Optional[str] = None


@dataclass
class KafkaFlow:
    """Kafka event flow information."""
    file_path: str
    topic: str
    direction: str  # Consume or Produce
    implementation: str  # WalmartKafkaListener, KafkaListener, KafkaTemplate
    message_type: Optional[str] = None
    serialization_format: Optional[str] = None  # JSON, Avro, Protobuf
    partition_strategy: Optional[str] = None
    consumer_group: Optional[str] = None
    has_dlt: bool = False
    dlt_topic: Optional[str] = None


@dataclass
class DatabaseConnection:
    """Database connection information."""
    file_path: str
    db_type: str  # PostgreSQL, MySQL, Cassandra, MongoDB, etc.
    access_type: AccessType
    tables: Set[str] = field(default_factory=set)
    entities: Set[str] = field(default_factory=set)
    relationships: Dict[str, List[str]] = field(default_factory=dict)  # Entity -> related entities
    stored_procedures: List[str] = field(default_factory=list)
    has_connection_pooling: bool = False
    pool_size: Optional[int] = None
    query_annotations_found: bool = False


@dataclass
class Configuration:
    """Configuration property information."""
    file_path: str
    property_name: str
    property_key: str  # e.g., 'app.max-retries'
    default_value: Optional[str] = None
    is_required: bool = False
    source: str = "@Value"  # @Value, @ConfigurationProperties, etc.


@dataclass
class ErrorHandler:
    """Error handling configuration."""
    file_path: str
    handler_name: str
    exception_types: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    is_global: bool = False  # @ControllerAdvice vs @ExceptionHandler


@dataclass
class ResiliencePattern:
    """Resilience and fault tolerance pattern."""
    file_path: str
    pattern_type: ResilienceType
    target_service_or_operation: str
    config_details: Dict[str, str] = field(default_factory=dict)  # e.g., max_retries, timeout_ms


@dataclass
class SecurityConfig:
    """Security configuration."""
    file_path: str
    secured_endpoints: List[str] = field(default_factory=list)
    auth_type: AuthType = AuthType.NONE
    roles_required: Set[str] = field(default_factory=set)
    permissions_required: Set[str] = field(default_factory=set)
    has_cors: bool = False
    jwt_secret_ref: Optional[str] = None


@dataclass
class DataModel:
    """Data model (DTO, Entity, etc.) information."""
    file_path: str
    class_name: str
    model_type: str  # DTO, Entity, Request, Response
    fields: Dict[str, str] = field(default_factory=dict)  # field_name -> type
    validations: List[str] = field(default_factory=list)  # @NotNull, @Email, etc.
    is_serializable: bool = False
    has_lombok: bool = False


@dataclass
class ObservabilityConfig:
    """Observability and monitoring configuration."""
    file_path: str
    has_logging: bool = False
    logger_type: Optional[str] = None  # SLF4J, Log4j, etc.
    tracks_correlation_id: bool = False
    has_metrics: bool = False
    metrics_type: Optional[str] = None  # Micrometer, Prometheus, etc.
    has_health_check: bool = False
    health_check_path: Optional[str] = None


@dataclass
class ServiceDependency:
    """Service-to-service dependency."""
    source_service: str
    target_service: str
    flow_type: FlowType  # Sync, Async, Reactive
    source_file: str
    target_file: str
    dependency_type: str  # @Autowired, Constructor Injection, Method Call, etc.
    method_called: Optional[str] = None


@dataclass
class ApiContract:
    """Complete API contract for endpoint."""
    endpoint: RestEndpoint
    request_model: Optional[DataModel] = None
    response_model: Optional[DataModel] = None
    error_responses: List[Dict[str, str]] = field(default_factory=list)  # status_code -> error_type
    rate_limit_config: Optional[Dict[str, str]] = None
    cache_strategy: Optional[str] = None


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    services: List[Service] = field(default_factory=list)
    rest_endpoints: List[RestEndpoint] = field(default_factory=list)
    kafka_flows: List[KafkaFlow] = field(default_factory=list)
    database_connections: List[DatabaseConnection] = field(default_factory=list)
    configurations: List[Configuration] = field(default_factory=list)
    error_handlers: List[ErrorHandler] = field(default_factory=list)
    resilience_patterns: List[ResiliencePattern] = field(default_factory=list)
    security_configs: List[SecurityConfig] = field(default_factory=list)
    data_models: List[DataModel] = field(default_factory=list)
    service_dependencies: List[ServiceDependency] = field(default_factory=list)
    observability_configs: List[ObservabilityConfig] = field(default_factory=list)
    api_contracts: List[ApiContract] = field(default_factory=list)
