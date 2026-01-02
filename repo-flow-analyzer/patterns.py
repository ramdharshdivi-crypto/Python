"""Regex patterns for Enterprise Spring Boot Repo Analysis.

Organized by category for easy maintenance and reuse.
"""

import re
from dataclasses import dataclass
from typing import Pattern


@dataclass
class PatternRegistry:
    """Central registry of all regex patterns used in analysis."""

    # ============= SPRING CORE =============
    REST_CONTROLLER: Pattern = re.compile(r"@RestController")
    SERVICE_ANNOTATION: Pattern = re.compile(r"@(Service|Component)")
    REPOSITORY_ANNOTATION: Pattern = re.compile(r"@Repository")
    CONFIG_ANNOTATION: Pattern = re.compile(r"@Configuration")
    BEAN_ANNOTATION: Pattern = re.compile(r"@Bean")

    # ============= REST MAPPINGS =============
    REQUEST_MAPPING: Pattern = re.compile(
        r"@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\(\"([^\"]*)\""
    )
    PRODUCES_CONSUMES: Pattern = re.compile(
        r"(produces|consumes)\s*=\s*\"([^\"]+)\""
    )
    PATH_VARIABLE: Pattern = re.compile(r"@PathVariable\s+([\w\s]+)\s+(\w+)")
    REQUEST_PARAM: Pattern = re.compile(r"@RequestParam\s+([\w\s]+)\s+(\w+)")
    REQUEST_BODY: Pattern = re.compile(r"@RequestBody\s+([\w<>,\s]+)")
    RESPONSE_STATUS: Pattern = re.compile(r"@ResponseStatus\s*\(\s*HttpStatus\.(\w+)")

    # ============= DEPENDENCY INJECTION =============
    AUTOWIRED: Pattern = re.compile(r"@(Autowired|Inject)")
    AUTOWIRED_WITH_NAME: Pattern = re.compile(
        r"@(Autowired|Inject)\s+(?:private|protected|public)?\s+([\w<>,\s]+)\s+(\w+)"
    )
    CONSTRUCTOR_INJECTION: Pattern = re.compile(
        r"public\s+\w+\s*\(([^)]+)\)"
    )
    SERVICE_CALL: Pattern = re.compile(r"\b(\w+Service)\s*\.\s*(\w+)\s*\(")

    # ============= KAFKA =============
    WALMART_KAFKA_LISTENER: Pattern = re.compile(
        r"@WalmartKafkaListener\s*\((.*?)\)",
        re.DOTALL
    )
    SPRING_KAFKA_LISTENER: Pattern = re.compile(
        r"@KafkaListener\s*\((.*?)\)",
        re.DOTALL
    )
    TOPIC_EXTRACTOR: Pattern = re.compile(
        r"topics\s*=\s*\{?\"([^\"]+)\""
    )
    KAFKA_TEMPLATE_SEND: Pattern = re.compile(
        r"\b(\w*KafkaTemplate)\s*\.\s*send\s*\(",
        re.DOTALL
    )
    KAFKA_MESSAGE_FORMAT: Pattern = re.compile(
        r"@KafkaListener.*?\(([^)]+)\)"
    )
    DLT_LISTENER: Pattern = re.compile(r"@DltHandler|dltStrategy|deadLetterTopic")

    # ============= DATABASES - JDBC =============
    JDBC_TEMPLATE: Pattern = re.compile(
        r"(JdbcTemplate|NamedParameterJdbcTemplate)"
    )
    SQL_OPERATION: Pattern = re.compile(
        r"\b(SELECT|INSERT|UPDATE|DELETE)\b",
        re.IGNORECASE
    )
    TABLE_EXTRACTOR: Pattern = re.compile(
        r"\bFROM\s+([A-Z0-9_\.]+)|" +
        r"\bINTO\s+([A-Z0-9_\.]+)|" +
        r"\bUPDATE\s+([A-Z0-9_\.]+)",
        re.IGNORECASE
    )
    STORED_PROCEDURE: Pattern = re.compile(
        r"(SimpleJdbcCall|StoredProcedure|call\s+\w+)"
    )

    # ============= DATABASES - JPA =============
    JPA_ENTITY: Pattern = re.compile(r"@Entity\s*(?:class|public)\s+(\w+)")
    JPA_REPOSITORY: Pattern = re.compile(
        r"extends\s+(?:Crud|Jpa|Paging)Repository<([^,]+),"
    )
    RELATIONSHIP_ANNOTATION: Pattern = re.compile(
        r"@(OneToOne|OneToMany|ManyToOne|ManyToMany)\s*(?:\([^)]*\))?.*?\n.*?private\s+([\w<>,\s]+)\s+(\w+)"
    )
    QUERY_ANNOTATION: Pattern = re.compile(
        r"@Query\s*\(\"([^\"]+)\""
    )
    TRANSACTIONAL: Pattern = re.compile(r"@Transactional")

    # ============= DATABASES - ELASTICSEARCH =============
    ELASTIC_CLIENT: Pattern = re.compile(
        r"(RestHighLevelClient|ElasticsearchClient|ElasticsearchOperations)"
    )
    ELASTIC_INDEX: Pattern = re.compile(
        r"@Document\s*\(\s*indexName\s*=\s*\"([^\"]+)\""
    )
    ELASTIC_OPERATION: Pattern = re.compile(
        r"(IndexRequest|UpdateRequest|DeleteRequest|SearchRequest)"
    )
    ELASTIC_REPOSITORY: Pattern = re.compile(
        r"extends\s+ElasticsearchRepository<([^,]+),"
    )

    # ============= DATABASES - CASSANDRA =============
    CASSANDRA_DRIVER: Pattern = re.compile(
        r"com\.datastax\.oss\.driver\.api",
        re.IGNORECASE
    )
    CASSANDRA_QUERY_BUILDER: Pattern = re.compile(
        r"QueryBuilder\.(insertInto|selectFrom|update|deleteFrom)",
        re.IGNORECASE
    )
    CASSANDRA_TABLE: Pattern = re.compile(
        r"insertInto\s*\(\s*\"([^\"]+)\"|" +
        r"from\s*\(\s*\"([^\"]+)\"",
        re.IGNORECASE
    )

    # ============= CONFIGURATION =============
    VALUE_ANNOTATION: Pattern = re.compile(
        r"@Value\s*\(\s*\"([^\"]+)\""
    )
    CONFIG_PROPERTIES: Pattern = re.compile(
        r"@ConfigurationProperties\s*\(\s*prefix\s*=\s*\"([^\"]+)\""
    )
    ENV_VARIABLE: Pattern = re.compile(
        r"System\.getenv\([\"']([^\"']+)[\"']\)"
    )
    PROPERTY_SOURCE: Pattern = re.compile(
        r"@PropertySource\s*\(\s*\"([^\"]+)\""
    )

    # ============= ERROR HANDLING =============
    EXCEPTION_HANDLER: Pattern = re.compile(
        r"@ExceptionHandler\s*\(\s*([^)]+)\s*\)"
    )
    CONTROL_ADVICE: Pattern = re.compile(r"@RestControllerAdvice|@ControllerAdvice")
    TRY_CATCH: Pattern = re.compile(r"try\s*\{|catch\s*\([^)]+\)")
    THROWS_CLAUSE: Pattern = re.compile(r"throws\s+([^{]+)\{")

    # ============= RESILIENCE & RETRY =============
    RETRY_ANNOTATION: Pattern = re.compile(r"@Retryable|@Retry")
    CIRCUIT_BREAKER: Pattern = re.compile(
        r"@CircuitBreaker|CircuitBreakerFactory|resilience4j"
    )
    TIMEOUT: Pattern = re.compile(
        r"@Timeout|Timeout\s*\(|timeout\s*=\s*(\d+)"
    )
    FALLBACK: Pattern = re.compile(r"@Fallback|fallback|fallbackFactory")
    RATE_LIMIT: Pattern = re.compile(r"@RateLimiter|RateLimiter|rateLimiter")

    # ============= SECURITY =============
    SECURED_ANNOTATION: Pattern = re.compile(r"@Secured\s*\(\s*([^)]+)\s*\)")
    PRE_AUTHORIZE: Pattern = re.compile(
        r"@PreAuthorize\s*\(\s*\"([^\"]+)\""
    )
    OAUTH2_ANNOTATION: Pattern = re.compile(r"@OAuth2\w+|OAuth2RestTemplate")
    JWT_TOKEN: Pattern = re.compile(
        r"(JwtTokenProvider|JwtTokenValidator|JwtAuthenticationFilter|JwtAuthenticationProvider)"
    )
    SPRING_SECURITY: Pattern = re.compile(
        r"(SecurityContextHolder|SecurityContext|Authentication|Principal)"
    )

    # ============= ASYNC & REACTIVE =============
    ASYNC_ANNOTATION: Pattern = re.compile(r"@Async")
    COMPLETABLE_FUTURE: Pattern = re.compile(r"CompletableFuture<")
    MONO_FLUX: Pattern = re.compile(r"\b(Mono|Flux)<")
    OBSERVABLE: Pattern = re.compile(r"\b(Observable|Single|Maybe)<")
    CALLABLE: Pattern = re.compile(r"\bCallable<")
    SCHEDULED: Pattern = re.compile(r"@Scheduled|ScheduledExecutorService")

    # ============= CACHING =============
    CACHEABLE: Pattern = re.compile(r"@Cacheable|@CachePut|@CacheEvict")
    REDIS_CLIENT: Pattern = re.compile(
        r"(RedisTemplate|StringRedisTemplate|RedisConnectionFactory)"
    )
    CACHE_MANAGER: Pattern = re.compile(r"CacheManager|@EnableCaching")
    CACHE_CONFIG: Pattern = re.compile(r"cache\.ttl|cache\.size")

    # ============= LOGGING & OBSERVABILITY =============
    LOGGER_DECLARATION: Pattern = re.compile(
        r"(private\s+static\s+final\s+Logger|@Slf4j|private\s+static\s+final\s+log4j)"
    )
    SLF4J_LOGGER: Pattern = re.compile(r"@Slf4j|LoggerFactory\.getLogger")
    LOG_STATEMENT: Pattern = re.compile(
        r"\b(log|logger|log4j|slf4j)\.(debug|info|warn|error)\("
    )
    CORRELATION_ID: Pattern = re.compile(
        r"(correlationId|traceId|spanId|requestId)"
    )
    HEALTH_CHECK: Pattern = re.compile(
        r"@HealthIndicator|HealthIndicator|/actuator/health"
    )
    METRICS: Pattern = re.compile(
        r"(MeterRegistry|@Timed|@Counted|prometheus|micrometer)"
    )

    # ============= DATA MODELS =============
    DTO_CLASS: Pattern = re.compile(
        r"(?:public|private)\s+class\s+(\w*(?:DTO|Request|Response|Model|Entity))\s*\{"
    )
    LOMBOK_DATA: Pattern = re.compile(r"@Data|@Getter|@Setter|@NoArgsConstructor")
    SERIALIZATION: Pattern = re.compile(
        r"(Serializable|@JsonSerialize|@JsonDeserialize|@XmlElement)"
    )
    VALIDATION: Pattern = re.compile(
        r"(@NotNull|@NotBlank|@Valid|@Validated|@Pattern|@Min|@Max|@Email)"
    )

    # ============= DATABASE TYPES =============
    DB_TYPE_INDICATORS = {
        "DB2": ["db2", "jdbc:db2", "com.ibm.db2"],
        "PostgreSQL": ["postgres", "jdbc:postgresql", "org.postgresql"],
        "AzureSQL": ["azure", "jdbc:sqlserver", "com.microsoft.sqlserver"],
        "MySQL": ["mysql", "jdbc:mysql", "com.mysql.jdbc"],
        "Oracle": ["oracle", "jdbc:oracle", "com.oracle.jdbc"],
        "MongoDB": ["mongodb", "MongoTemplate", "MongoRepository"],
        "Cassandra": ["com.datastax", "Cluster", "Session"],
        "Redis": ["redis", "RedisTemplate", "LettuceConnectionFactory"],
    }


def get_patterns() -> PatternRegistry:
    """Factory function to get pattern registry."""
    return PatternRegistry()
