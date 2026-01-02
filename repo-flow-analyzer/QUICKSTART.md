# 🚀 Quick Start Guide

## Installation

1. **Clone or download** the analyzer directory:
   ```bash
   # The directory is located at:
   # C:\Users\vn59ikg\Documents\repo-flow-analyzer
   ```

2. **Requirements**:
   - Python 3.10 or higher
   - No external dependencies needed! Uses only Python standard library

## Basic Usage

### Analyze Your First Repository

```bash
cd C:\Users\vn59ikg\Documents\repo-flow-analyzer

# Analyze a Spring Boot repository
python main.py --repo C:\path\to\your\spring-boot-project

# Results will be in: C:\path\to\your\spring-boot-project\repo-analysis-output
```

### Common Commands

```bash
# Analyze with custom output directory
python main.py --repo C:\path\to\repo --out my-analysis

# Enable verbose output (see detailed logs)
python main.py --repo C:\path\to\repo --verbose

# Skip Markdown generation (CSV only)
python main.py --repo C:\path\to\repo --no-md

# Get help
python main.py --help
```

## Understanding the Output

After analysis, you'll find these files in your output directory:

### CSV Files (11 reports)

1. **01_services.csv** - All Spring services, controllers, components
2. **02_api_endpoints.csv** - REST API endpoints with methods, paths, auth
3. **03_kafka_flows.csv** - Kafka topics, producers, consumers
4. **04_database_connections.csv** - Database connections, tables, access types
5. **05_configurations.csv** - Configuration properties (@Value, @ConfigurationProperties)
6. **06_error_handlers.csv** - Exception handlers and error handling
7. **07_resilience_patterns.csv** - Retry, circuit breaker, timeout, fallback
8. **08_security_config.csv** - Authentication, authorization, JWT, OAuth2
9. **09_data_models.csv** - DTOs, Entities, Request/Response models
10. **10_service_dependencies.csv** - Service-to-service dependencies
11. **11_observability.csv** - Logging, metrics, health checks

### Markdown Report

**README.md** - Executive summary with statistics and key findings

## Real Example

```bash
# Example: Analyze a real project
python main.py --repo C:\Users\john\projects\ecommerce-platform

# Output:
# ============================================================
# ✅ ANALYSIS COMPLETE!
# ============================================================
#
# Results saved to: C:\Users\john\projects\ecommerce-platform\repo-analysis-output
#
# 📊 Summary Statistics:
#   Total Services: 12
#   Total Endpoints: 45
#   Total Kafka Flows: 8
#   Total Databases: 3
#   Total Configurations: 24
#   Total Error Handlers: 5
#   Total Resilience Patterns: 6
#   Total Data Models: 18
#   Total Dependencies: 22
#
# 📁 Output Files:
#   01_services.csv
#   02_api_endpoints.csv
#   ...
#   README.md
```

## What Gets Detected?

### ✅ Services
```java
@RestController              // ✅ REST Controller
public class UserApi { }

@Service                     // ✅ Service
public class UserService { }
```

### ✅ REST Endpoints
```java
@GetMapping("/users/{id}")   // ✅ Path extracted
public User getUser(@PathVariable Long id) { }  // ✅ Path variables
```

### ✅ Kafka Flows
```java
@KafkaListener(topics = "user-events")  // ✅ Topic extracted
public void consume(UserEvent event) { }
```

### ✅ Databases
```java
JdbcTemplate.query(...)      // ✅ JDBC detected
@Entity class User { }       // ✅ JPA detected
RestHighLevelClient          // ✅ Elasticsearch detected
```

### ✅ Resilience
```java
@Retryable                   // ✅ Retry pattern
@CircuitBreaker              // ✅ Circuit breaker
```

### ✅ Security
```java
@Secured("ROLE_ADMIN")       // ✅ Role-based security
JwtTokenProvider             // ✅ JWT detected
```

## Opening CSV Files

### Windows
- **Excel**: Right-click → Open with → Excel
- **Notepad**: Right-click → Open with → Notepad
- **VSCode**: Drag and drop into editor

### Analysis Tips

1. **Open in Excel for better filtering and sorting**
   - Use filters to find services
   - Sort by access type or database type
   - Use pivot tables for summaries

2. **Use grep/find for text search**
   ```bash
   # Find all endpoints related to "user"
   grep -i "user" 02_api_endpoints.csv
   ```

3. **Copy data to other tools**
   - Import into database tools
   - Load into visualization platforms
   - Share with team via sheets

## Troubleshooting

### No Java files found
```bash
python main.py --repo C:\path\to\repo --verbose
```
Make sure the path contains a Spring Boot project with .java files.

### Python not found
```bash
# Make sure Python 3.10+ is in PATH
python --version

# If not working, use full path
C:\Python310\python.exe main.py --repo C:\path\to\repo
```

### Permission denied error
```bash
# Try running as Administrator
# Or use a different output directory with write permissions
python main.py --repo C:\path\to\repo --out C:\Users\YourUsername\Desktop\analysis
```

## Next Steps

1. **Read the Full Docs**: See `README.md` for comprehensive documentation
2. **Developer Guide**: See `DEVELOPER_GUIDE.md` to extend the analyzer
3. **Analyze Multiple Repos**: Run the analyzer on different projects
4. **Share Results**: Excel files are easy to share with your team
5. **Set Up CI/CD**: Integrate analyzer into your build pipeline

## Tips for Best Results

1. ✅ **Run on source directory** - Not on `/target` or `/build`
2. ✅ **Analyze full projects** - Not just individual files
3. ✅ **Use verbose mode** - To debug if results seem off
4. ✅ **Check README.md** - Generated report has good overview
5. ✅ **Look at dependencies** - 10_service_dependencies.csv shows architecture

## Getting Help

For more information:
- User Guide: `README.md`
- Developer Guide: `DEVELOPER_GUIDE.md`
- Code Documentation: Check docstrings in source files

---

**Happy analyzing! 🐶**
