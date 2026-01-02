# 🐕 Enterprise Spring Boot Repository Analyzer

A comprehensive, modular Python tool for analyzing Spring Boot repositories and extracting architectural, dependency, and configuration information. Perfect for developers who need to understand their codebase architecture quickly.

## 🎯 Features

This analyzer extracts detailed information across **11 major categories**:

### 1. **Services** 📦
- REST Controllers, Spring Services, Components
- Async/Reactive patterns
- Health check endpoints
- Security configuration

### 2. **REST API Endpoints** 🔌
- HTTP methods and paths
- Request/Response models
- Status codes
- Authentication requirements
- Content types

### 3. **Kafka Event Flows** 🎯
- Topic subscriptions and publications
- Message serialization formats
- Consumer groups
- Dead Letter Topic (DLT) handling
- Implementation types

### 4. **Database Connections** 🗄️
- Database types (PostgreSQL, MySQL, MongoDB, Cassandra, Elasticsearch, etc.)
- Access patterns (Read/Write)
- Tables and entities
- Relationships
- Connection pooling
- Query annotations

### 5. **Configuration Properties** ⚙️
- @Value annotations
- @ConfigurationProperties
- Environment variables
- Default values
- Required vs optional configs

### 6. **Error Handling** 🛡️
- @ExceptionHandler mappings
- Global error handlers (@ControllerAdvice)
- Exception types
- Error response models

### 7. **Resilience Patterns** 🔄
- Retry configurations
- Circuit breaker setup
- Timeout configurations
- Fallback strategies
- Rate limiting

### 8. **Security Configuration** 🔐
- Authentication types (OAuth2, JWT, Spring Security)
- Secured endpoints
- Roles and permissions
- CORS configuration
- Token management

### 9. **Data Models** 📋
- DTOs, Entities, Requests, Responses
- Serialization settings
- Validation annotations
- Lombok usage
- Field definitions

### 10. **Service Dependencies** 🔗
- Service-to-service calls
- Dependency injection patterns
- Method invocations
- Flow types (Sync/Async/Reactive)

### 11. **Observability** 📊
- Logging configuration (SLF4J, Log4j)
- Correlation ID tracking
- Metrics collection (Micrometer, Prometheus)
- Health check endpoints

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download the analyzer
cd repo-flow-analyzer

# No external dependencies! Uses only Python standard library
# Python 3.10+ required
```

### Basic Usage

```bash
# Analyze a Spring Boot repository
python main.py --repo /path/to/spring-boot-project

# Analyze with custom output directory
python main.py --repo /path/to/repo --out my-analysis-results

# Enable verbose logging
python main.py --repo /path/to/repo --verbose

# Skip markdown generation
python main.py --repo /path/to/repo --no-md
```

### Example

```bash
python main.py --repo C:\Users\john\projects\my-spring-boot-app --out analysis
```

---

## 📊 Output Files

The analyzer generates **12 output files** in the specified output directory:

### CSV Reports (11 files)

| File | Contents | Use Case |
|------|----------|----------|
| `01_services.csv` | All detected services | Service inventory |
| `02_api_endpoints.csv` | REST endpoints | API documentation |
| `03_kafka_flows.csv` | Event subscriptions/publications | Event-driven architecture |
| `04_database_connections.csv` | DB access patterns | Data layer assessment |
| `05_configurations.csv` | Properties and settings | Configuration audit |
| `06_error_handlers.csv` | Exception handlers | Error handling review |
| `07_resilience_patterns.csv` | Retry/circuit breaker/timeout | Resilience assessment |
| `08_security_config.csv` | Auth and permissions | Security audit |
| `09_data_models.csv` | DTOs, Entities, Models | Data contract review |
| `10_service_dependencies.csv` | Service call graph | Dependency analysis |
| `11_observability.csv` | Logging, metrics, health | Observability review |

### Markdown Report

| File | Contents |
|------|----------|
| `README.md` | Executive summary with statistics and highlights |

---

## 🏗️ Architecture

The codebase is organized into **6 modular components**:

```
repo-flow-analyzer/
├── patterns.py          # Regex patterns registry (170 lines)
├── models.py            # Dataclasses for type safety (300+ lines)
├── extractors.py        # Individual analysis extractors (580 lines)
├── analyzer.py          # Orchestration engine (150 lines)
├── exporters.py         # CSV/Markdown export (350 lines)
└── main.py              # CLI entry point (140 lines)
```

### Design Principles

✅ **Modular**: Each extractor is independent and reusable  
✅ **Type-Safe**: Uses Python dataclasses for all models  
✅ **Zero Dependencies**: Only uses Python standard library  
✅ **Extensible**: Easy to add new extractors  
✅ **Well-Documented**: Comprehensive docstrings  
✅ **Production-Ready**: Error handling and logging throughout  

---

## 🔍 Analysis Deep-Dive

### What Gets Detected?

#### Services
```java
@RestController           // ✅ Detected as REST Controller
public class UserApi { }

@Service                  // ✅ Detected as Service
public class UserService { }

@Component                // ✅ Detected as Component
public class UserComponent { }
```

#### REST Endpoints
```java
@GetMapping("/users/{id}")           // ✅ Path extracted
public User getUser(
    @PathVariable Long id,            // ✅ Path var detected
    @RequestParam String filter,      // ✅ Query param detected
    @RequestBody UserRequest req      // ✅ Request body type
) { }
```

#### Kafka Flows
```java
@WalmartKafkaListener(topics = "user-events")    // ✅ Topic extracted
public void consume(UserEvent event) { }

kafkaTemplate.send("order-topic", payload);      // ✅ Producer detected
```

#### Databases
```java
JdbcTemplate.query("SELECT * FROM users");       // ✅ JDBC detected

@Entity
class User { }                                     // ✅ JPA entity detected

RestHighLevelClient                               // ✅ Elasticsearch detected

QueryBuilder.selectFrom("users")                  // ✅ Cassandra detected
```

#### Resilience
```java
@Retryable                                        // ✅ Retry pattern
@CircuitBreaker                                   // ✅ Circuit breaker
@Timeout                                          // ✅ Timeout config
@Fallback                                         // ✅ Fallback method
```

#### Security
```java
@Secured("ROLE_ADMIN")                           // ✅ Role-based security
@PreAuthorize("hasRole('ADMIN')")                // ✅ Permission check
JwtTokenProvider                                   // ✅ JWT detection
OAuth2RestTemplate                                // ✅ OAuth2 detection
```

---

## 💡 Use Cases

### 1. **Architecture Review** 🏛️
```bash
# Get complete architecture overview
python main.py --repo /path/to/repo --out architecture-review
# Review: 10_service_dependencies.csv for service call graph
```

### 2. **Security Audit** 🔒
```bash
# Identify all authentication mechanisms
python main.py --repo /path/to/repo --out security-audit
# Review: 08_security_config.csv for auth patterns
```

### 3. **Database Assessment** 🗄️
```bash
# Understand data layer
python main.py --repo /path/to/repo --out db-assessment
# Review: 04_database_connections.csv for DB patterns
```

### 4. **API Documentation** 📚
```bash
# Generate API catalog
python main.py --repo /path/to/repo --out api-docs
# Review: 02_api_endpoints.csv for endpoint catalog
```

### 5. **Resilience Assessment** 🛡️
```bash
# Find resilience gaps
python main.py --repo /path/to/repo --out resilience-check
# Review: 07_resilience_patterns.csv to find missing patterns
```

### 6. **Observability Audit** 📊
```bash
# Check logging and metrics
python main.py --repo /path/to/repo --out observability-audit
# Review: 11_observability.csv to identify blind spots
```

---

## 🎨 Example Output

### Console Output
```
============================================================
✅ ANALYSIS COMPLETE!
============================================================

Results saved to: C:\project\repo-analysis-output

📊 Summary Statistics:
  Total Services: 12
  Total Endpoints: 45
  Total Kafka Flows: 8
  Total Databases: 3
  Total Configurations: 24
  Total Error Handlers: 5
  Total Resilience Patterns: 6
  Total Data Models: 18
  Total Dependencies: 22

📁 Output Files:
  01_services.csv - All detected services
  02_api_endpoints.csv - REST API endpoints
  03_kafka_flows.csv - Kafka topics and flows
  ...
  README.md - Summary report

============================================================
```

### CSV Sample Output

**02_api_endpoints.csv**
```
Method,Path,Request Body,Response Type,Produces,Auth Required,Auth Type,File
GET,/api/users/,None,User,application/json,No,None,UserController.java
POST,/api/users/,UserCreateRequest,User,application/json,Yes,JWT,UserController.java
```

---

## 🔧 Advanced Usage

### Programmatic Usage

```python
from pathlib import Path
from analyzer import RepoAnalyzer

# Create analyzer
repo_path = Path("/path/to/repo")
analyzer = RepoAnalyzer(repo_path)

# Run analysis
result = analyzer.analyze()

# Access results programmatically
for service in result.services:
    print(f"Service: {service.service_name}")
    for endpoint in service.endpoints:
        print(f"  - {endpoint.method} {endpoint.path}")

# Get summary
summary = analyzer.get_analysis_summary()
print(summary)
```

### Adding Custom Extractors

```python
from extractors import BaseExtractor
from models import CustomModel

class CustomExtractor(BaseExtractor):
    def extract(self, content: str, file_path: str) -> list:
        # Your extraction logic
        return []
```

---

## 📋 Requirements

- **Python 3.10+**
- No external dependencies (uses only Python standard library)
- Works on Windows, macOS, Linux

---

## 🤝 Contributing

Feel free to extend the analyzer by:

1. Adding new patterns to `patterns.py`
2. Creating new models in `models.py`
3. Implementing new extractors in `extractors.py`
4. Adding export formats in `exporters.py`

---

## 📝 License

Created with ❤️ for Spring Boot developers

---

## 🐕 Made with Code Puppy

**Ramy the Code Puppy** - Your loyal AI code assistant for analyzing, understanding, and improving Spring Boot architectures!

Questions? Need help? Run with `--verbose` to see detailed analysis logs.
