# 📊 Usage Examples - Enterprise Spring Boot Repository Analyzer

## Real-World Scenarios

This document provides practical examples of how to use the analyzer for common tasks.

---

## Example 1: Analyze a Spring Boot Microservice

### Scenario
You have a Spring Boot microservice and want to understand its architecture.

### Command
```bash
cd C:\Users\vn59ikg\Documents\repo-flow-analyzer
python main.py --repo C:\Projects\user-service
```

### What You'll Get
- **01_services.csv** - List all services/controllers in the microservice
- **02_api_endpoints.csv** - All REST endpoints with methods and paths
- **03_kafka_flows.csv** - Event subscriptions (if any)
- **04_database_connections.csv** - Database tables accessed
- **08_security_config.csv** - Authentication setup
- **README.md** - Quick overview

### Next Steps
1. Open `02_api_endpoints.csv` in Excel
2. Filter by path or method
3. Share with your team
4. Document API contracts

---

## Example 2: Security Audit

### Scenario
Your security team needs to understand authentication mechanisms used in your codebase.

### Command
```bash
python main.py --repo C:\Projects\banking-app --out security-audit --verbose
```

### What You'll Get
- **08_security_config.csv** - All auth configurations
  - Authentication types (JWT, OAuth2, Spring Security)
  - Secured endpoints
  - Roles and permissions
  - CORS settings

### Analysis
```
Open security_config.csv and check:
- Are all endpoints authenticated? (Auth Required column)
- What authentication methods are used?
- Are there any endpoints with "None" auth?
- What roles/permissions are enforced?
```

### Example Output
```csv
Authentication Type,Secured Endpoints,Roles,Permissions,CORS Enabled,File
JWT,/api/users/*;/api/orders/*,ROLE_ADMIN;ROLE_USER,WRITE:USER,Yes,UserController.java
OAuth2,/api/oauth/*,ROLE_OAUTH_CLIENT,READ:PROFILE,No,OAuthController.java
```

---

## Example 3: Database Assessment

### Scenario
You're optimizing database queries and need to understand table relationships.

### Command
```bash
python main.py --repo C:\Projects\ecommerce --out db-assessment
```

### What You'll Get
- **04_database_connections.csv** with:
  - Database types (PostgreSQL, MySQL, MongoDB)
  - Tables accessed by each service
  - Access patterns (Read vs Read/Write)
  - Connection pooling status

### Analysis
```
1. Sort by Database Type
2. Check for tables accessed by multiple services
3. Identify Read-only vs Read/Write services
4. Plan for data consistency
```

### Example Output
```csv
Database Type,Access Type,Tables/Indices,Connection Pooling,File
PostgreSQL,Read/Write,users;orders;products,Yes,UserService.java
MySQL,Read,inventory;stock,Yes,InventoryService.java
Elasticsearch,Read/Write,user-index;product-index,No,SearchService.java
```

---

## Example 4: API Documentation Generation

### Scenario
You need to generate API documentation for your REST endpoints.

### Command
```bash
python main.py --repo C:\Projects\mobile-api --out api-docs
```

### What You'll Get
- **02_api_endpoints.csv** with all endpoint details:
  - HTTP Method (GET, POST, PUT, DELETE)
  - Path and path variables
  - Request/Response types
  - Authentication required
  - Response status codes

### How to Use
```
1. Open 02_api_endpoints.csv in Excel
2. Use filters to group by method or path
3. Export to create API documentation
4. Import into API tools (Postman, Swagger)
```

### Example Output
```csv
Method,Path,Request Body,Response Type,Auth Required,Auth Type,Response Status,File
GET,/api/users/,None,User,No,None,200,UserController.java
GET,/api/users/{id},None,User,No,None,200;404,UserController.java
POST,/api/users/,UserCreateRequest,User,Yes,JWT,201;400,UserController.java
PUT,/api/users/{id},UserUpdateRequest,User,Yes,JWT,200;400;404,UserController.java
DELETE,/api/users/{id},None,None,Yes,JWT,204;404,UserController.java
```

---

## Example 5: Resilience Patterns Review

### Scenario
You want to ensure your services handle failures gracefully.

### Command
```bash
python main.py --repo C:\Projects\distributed-system --out resilience-check
```

### What You'll Get
- **07_resilience_patterns.csv** showing:
  - Services with retry logic
  - Circuit breaker implementations
  - Timeout configurations
  - Fallback mechanisms

### Analysis
```
1. Check which services have resilience patterns
2. Identify services WITHOUT resilience (risky!)
3. Review pattern configurations
4. Add missing patterns
```

### Example Output
```csv
Pattern Type,Target,Configuration,File
Retry,UserService,max_retries=3,UserService.java
Circuit Breaker,OrderService,failure_threshold=50%,OrderService.java
Timeout,PaymentService,timeout_ms=5000,PaymentService.java
Fallback,NotificationService,fallback_method=sendLocal,NotificationService.java
Rate Limit,ApiGateway,max_requests=1000/min,ApiGateway.java
```

---

## Example 6: Observability Audit

### Scenario
You need to understand logging and monitoring setup across services.

### Command
```bash
python main.py --repo C:\Projects\critical-service --out observability
```

### What You'll Get
- **11_observability.csv** with:
  - Logging configuration (SLF4J, Log4j)
  - Correlation ID tracking
  - Metrics collection
  - Health check endpoints

### Analysis
```
1. Identify services WITHOUT logging
2. Check for correlation ID usage
3. Verify metrics are being collected
4. Ensure health checks are implemented
```

### Example Output
```csv
Has Logging,Logger Type,Tracks Correlation ID,Has Metrics,Metrics Type,Has Health Check,File
Yes,SLF4J,Yes,Yes,Micrometer,Yes,UserService.java
Yes,SLF4J,Yes,Yes,Micrometer,Yes,OrderService.java
No,None,No,No,None,No,InventoryService.java
Yes,Log4j,No,No,None,No,PaymentService.java
```

---

## Example 7: Service Dependency Mapping

### Scenario
You need to understand which services call which other services.

### Command
```bash
python main.py --repo C:\Projects\platform --out dependency-map
```

### What You'll Get
- **10_service_dependencies.csv** showing:
  - Source service
  - Target service
  - Call type (Sync/Async)
  - Method being called

### Analysis
```
1. Create service call matrix
2. Identify circular dependencies
3. Plan for service scaling
4. Understand blast radius of changes
```

### Example Output
```csv
Source Service,Target Service,Flow Type,Dependency Type,Method Called,Target File
UserService,AuthService,Sync,Method Call,validateToken,AuthService.java
OrderService,UserService,Sync,@Autowired,getUser,UserService.java
NotificationService,OrderService,Async,Kafka,onOrderCreated,OrderService.java
InventoryService,OrderService,Sync,Method Call,updateInventory,OrderService.java
```

---

## Example 8: Configuration Audit

### Scenario
You want to find all configuration properties and ensure they're properly externalized.

### Command
```bash
python main.py --repo C:\Projects\app --out config-audit
```

### What You'll Get
- **05_configurations.csv** with:
  - All @Value properties
  - @ConfigurationProperties classes
  - Property keys and sources

### Analysis
```
1. Identify hardcoded values
2. Find missing defaults
3. Plan configuration strategy
4. Document required properties
```

### Example Output
```csv
Property Name,Property Key,Default Value,Required,Source,File
max_retries,app.max-retries,3,No,@Value,RetryService.java
db_host,spring.datasource.host,N/A,Yes,@ConfigurationProperties,AppConfig.java
api_timeout,api.timeout-ms,5000,No,@Value,ApiClient.java
kafka_brokers,kafka.bootstrap-servers,N/A,Yes,@ConfigurationProperties,KafkaConfig.java
```

---

## Example 9: Error Handling Review

### Scenario
You want to ensure proper error handling across your application.

### Command
```bash
python main.py --repo C:\Projects\service --out error-handling
```

### What You'll Get
- **06_error_handlers.csv** with:
  - Exception handlers
  - Global vs local handlers
  - Exception types handled
  - Return types

### Analysis
```
1. Identify unhandled exception types
2. Check for global error handler
3. Verify error responses are consistent
4. Add missing handlers
```

### Example Output
```csv
Handler Name,Exception Types,Return Type,Global Handler,File
ExceptionHandler,BusinessException;ValidationException,ErrorResponse,No,UserController.java
ExceptionHandler,ResourceNotFoundException,ErrorResponse,No,UserController.java
GlobalExceptionHandler,Exception;RuntimeException,ErrorResponse,Yes,GlobalErrorHandler.java
```

---

## Example 10: Kafka Event Architecture

### Scenario
You need to understand your event-driven architecture.

### Command
```bash
python main.py --repo C:\Projects\event-platform --out event-arch
```

### What You'll Get
- **03_kafka_flows.csv** with:
  - Topics
  - Producers and consumers
  - Serialization formats
  - Dead Letter Topics
  - Consumer groups

### Analysis
```
1. Map event producers and consumers
2. Identify topics without consumers
3. Check for DLT setup
4. Plan for scalability
```

### Example Output
```csv
Topic,Direction,Implementation,Serialization,Consumer Group,Has DLT,File
user-events,Consume,KafkaListener,JSON,user-group,No,UserEventListener.java
user-events,Produce,KafkaTemplate,JSON,N/A,No,UserService.java
order-events,Consume,WalmartKafkaListener,JSON,order-group,Yes,OrderEventListener.java
order-events,Produce,KafkaTemplate,JSON,N/A,Yes,OrderService.java
```

---

## Tips for Analysis

### Working with CSV Files

1. **Open in Excel**
   - Better filtering and sorting
   - Conditional formatting
   - Pivot tables

2. **Filter by Column**
   - Find specific services
   - Filter by auth type
   - Find services without logging

3. **Sort by Column**
   - Sort endpoints by method
   - Sort by database type
   - Sort by resilience pattern

4. **Create Pivot Tables**
   - Count services by type
   - Analyze endpoints by auth
   - Summary of databases

### Sharing Results

1. **Email**: Send CSV files to stakeholders
2. **Sheets**: Import into Google Sheets
3. **Docs**: Include README.md in documentation
4. **Confluence**: Share findings with team

### Regular Scans

1. **Weekly**: Track changes to services
2. **Before Release**: Verify security
3. **After Changes**: Validate architecture
4. **Quarterly**: Overall assessment

---

## Combining Multiple Analyses

### Comprehensive Audit

```bash
# Run complete analysis
python main.py --repo C:\Projects\product --out comprehensive --verbose

# Review all 11 CSV files
# Check README.md for overview
# Share findings with team
```

### Focused Analysis

```bash
# Security focus
python main.py --repo C:\Projects\product --out security
# Review: 08_security_config.csv

# Performance focus
python main.py --repo C:\Projects\product --out performance
# Review: 04_database_connections.csv + 11_observability.csv

# Architecture focus
python main.py --repo C:\Projects\product --out architecture
# Review: 10_service_dependencies.csv + 01_services.csv
```

---

## Troubleshooting Examples

### Problem: No endpoints found
```bash
# Check if it's a REST controller
python main.py --repo C:\path --verbose
# Look for: "REST_CONTROLLER not found" messages
```

### Problem: Few databases detected
```bash
# Check what patterns matched
python main.py --repo C:\path --verbose
# Look for: Database detection logs
```

### Problem: Missing services
```bash
# Ensure path is to src directory
python main.py --repo C:\path\src --out analysis
```

---

## Conclusion

The analyzer is flexible and can be used for various purposes:
- ✅ Architecture reviews
- ✅ Security audits
- ✅ Performance assessment
- ✅ Documentation generation
- ✅ Compliance checking
- ✅ Team onboarding

For more information, see [README.md](README.md) or [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).
