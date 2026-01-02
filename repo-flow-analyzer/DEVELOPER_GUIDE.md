# Developer Guide - Repository Analyzer

## Overview

This guide explains how to use, extend, and maintain the Enterprise Spring Boot Repository Analyzer.

---

## Project Structure

### File Organization

```
repo-flow-analyzer/
├── patterns.py       (170 lines) - Regex patterns for all detections
├── models.py         (300 lines) - Type-safe dataclasses
├── extractors.py     (580 lines) - Individual feature extractors
├── analyzer.py       (150 lines) - Orchestration engine
├── exporters.py      (350 lines) - CSV/Markdown output
├── main.py           (140 lines) - CLI interface
├── requirements.txt  - Dependencies (zero external deps)
├── README.md         - User documentation
└── DEVELOPER_GUIDE.md - This file
```

### Design Patterns Used

1. **Factory Pattern** - `get_patterns()` in `patterns.py`
2. **Extractor Pattern** - `BaseExtractor` with specialized extractors
3. **Builder Pattern** - `AnalysisResult` accumulates findings
4. **Strategy Pattern** - Different exporters (CSV, Markdown)

---

## Understanding Each Module

### 1. patterns.py

**Responsibility**: Central registry of all regex patterns

**Key Classes**:
- `PatternRegistry` - Dataclass holding all compiled patterns
- `DB_TYPE_INDICATORS` - Dictionary mapping database types to keywords

**Adding New Patterns**:

```python
class PatternRegistry:
    # Add new pattern as class variable
    MY_NEW_PATTERN: Pattern = re.compile(r"@MyAnnotation")
```

**Pattern Categories**:
- Spring Core (@RestController, @Service, etc.)
- REST Mappings (@GetMapping, @RequestMapping, etc.)
- Kafka (@KafkaListener, KafkaTemplate)
- Databases (JDBC, JPA, Elasticsearch, Cassandra)
- Configuration (@Value, @ConfigurationProperties)
- Error Handling (@ExceptionHandler)
- Resilience (Retry, CircuitBreaker, Timeout)
- Security (@Secured, @PreAuthorize, JWT)
- Async/Reactive (Mono, Flux, CompletableFuture)
- Caching (@Cacheable, Redis)
- Observability (Logging, Metrics, Health)

---

### 2. models.py

**Responsibility**: Type-safe data models using dataclasses

**Key Classes**:

```python
# Enums
AccessType          # READ, WRITE, READ_WRITE
FlowType            # SYNC, ASYNC, REACTIVE
ResilienceType      # RETRY, CIRCUIT_BREAKER, TIMEOUT, FALLBACK, RATE_LIMIT
AuthType            # OAUTH2, JWT, BASIC, API_KEY, SPRING_SECURITY, NONE

# Main Models
Service                    # Spring service info
RestEndpoint              # API endpoint
KafkaFlow                 # Event flow
DatabaseConnection        # DB access
Configuration             # Property config
ErrorHandler              # Exception handling
ResiliencePattern         # Fault tolerance
SecurityConfig            # Authentication
DataModel                 # DTO/Entity
ObservabilityConfig       # Logging/Metrics
ServiceDependency         # Service calls

# Top-level result
AnalysisResult            # Container for all findings
```

**Adding New Model**:

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class MyNewModel:
    file_path: str
    my_field: str
    optional_field: Optional[str] = None
    list_field: List[str] = field(default_factory=list)
```

---

### 3. extractors.py

**Responsibility**: Extract specific information from Java source code

**Key Classes**:

```python
BaseExtractor              # Common utilities
├── RestEndpointExtractor
├── ServiceDependencyExtractor
├── KafkaExtractor
├── DatabaseExtractor
├── ConfigurationExtractor
├── ErrorHandlerExtractor
├── ResilienceExtractor
├── SecurityExtractor
├── DataModelExtractor
└── ObservabilityExtractor
```

**Creating New Extractor**:

```python
class MyNewExtractor(BaseExtractor):
    """Extracts my specific feature."""
    
    def extract(self, content: str, file_path: str) -> List[MyModel]:
        """Extract all instances of my feature."""
        results = []
        
        # Use self.patterns to find matches
        for match in self.patterns.MY_PATTERN.finditer(content):
            # Process match
            model = MyModel(
                file_path=str(file_path),
                # ... populate fields
            )
            results.append(model)
        
        return results
```

**Best Practices**:
- Use `BaseExtractor` utilities like `extract_text_in_parentheses()`
- Handle regex match groups carefully
- Return empty list if nothing found
- Use file encoding with `errors="ignore"`

---

### 4. analyzer.py

**Responsibility**: Orchestrate all extractors and correlate results

**Key Method**: `analyze()`

```
1. Find all .java files
2. For each file:
   - Extract REST endpoints
   - Extract Kafka flows
   - Extract database connections
   - Extract configurations
   - ... (all extractors)
3. Resolve dependencies between services
4. Correlate services with endpoints
5. Return combined AnalysisResult
```

**Adding New Extraction**:

```python
# In __init__
self.my_extractor = MyNewExtractor()

# In _analyze_file()
my_results = self.my_extractor.extract(content, java_file)
self.result.my_results.extend(my_results)
```

---

### 5. exporters.py

**Responsibility**: Export analysis results to user-friendly formats

**Key Classes**:

```python
CsvExporter       # Exports to 11 CSV files
├── export_services()
├── export_endpoints()
├── export_kafka()
├── ... (9 total export methods)
└── _write_csv()  # Helper

MarkdownExporter  # Exports to README.md
└── export_summary()
```

**Adding New Export**:

```python
# In CsvExporter
def export_my_feature(self, result: AnalysisResult) -> None:
    """Export my feature to CSV."""
    rows = []
    for item in result.my_items:
        rows.append({
            "Column1": item.field1,
            "Column2": item.field2,
        })
    self._write_csv("my_feature.csv", rows)

# Call from export_all()
def export_all(self, result: AnalysisResult) -> None:
    # ... existing exports
    self.export_my_feature(result)
```

---

### 6. main.py

**Responsibility**: CLI interface and orchestration

**Flow**:

```
1. Parse command-line arguments
2. Validate repo path
3. Create RepoAnalyzer
4. Run analysis
5. Export to CSV
6. Export to Markdown
7. Print summary
```

---

## Common Tasks

### Add Detection for New Framework Feature

1. **Add Regex Pattern** (patterns.py)
   ```python
   MY_FEATURE: Pattern = re.compile(r"@MyAnnotation")
   ```

2. **Create Data Model** (models.py)
   ```python
   @dataclass
   class MyFeature:
       file_path: str
       details: str
   ```

3. **Create Extractor** (extractors.py)
   ```python
   class MyFeatureExtractor(BaseExtractor):
       def extract(self, content: str, file_path: str) -> List[MyFeature]:
           # Implementation
   ```

4. **Wire into Analyzer** (analyzer.py)
   ```python
   self.my_extractor = MyFeatureExtractor()
   # ... in _analyze_file()
   results = self.my_extractor.extract(content, java_file)
   self.result.my_features.extend(results)
   ```

5. **Add to AnalysisResult** (models.py)
   ```python
   @dataclass
   class AnalysisResult:
       my_features: List[MyFeature] = field(default_factory=list)
   ```

6. **Export Results** (exporters.py)
   ```python
   def export_my_features(self, result: AnalysisResult) -> None:
       # Implementation
   ```

### Fix a Pattern that Doesn't Match

1. **Test Pattern in Python**:
   ```python
   import re
   pattern = re.compile(r"your pattern")
   with open("file.java") as f:
       content = f.read()
   matches = pattern.findall(content)
   print(matches)
   ```

2. **Debug with Verbose Logging**:
   ```bash
   python main.py --repo /path --verbose
   ```

3. **Update Pattern** in `patterns.py`

### Add New Export Format

1. **Create Exporter Class**:
   ```python
   class MyFormatExporter:
       def export_all(self, result: AnalysisResult) -> None:
           # Implementation
   ```

2. **Wire into main.py**

---

## Testing

### Manual Testing

```bash
# Test on sample repo
python main.py --repo /path/to/sample-spring-boot --verbose

# Verify CSV files were created
ls repo-analysis-output/

# Check CSV content
cat repo-analysis-output/01_services.csv
```

### Pattern Testing

```python
# test_patterns.py
from patterns import get_patterns
import re

patterns = get_patterns()

# Test a specific pattern
test_code = """@RestController\npublic class UserApi { }"""

if patterns.REST_CONTROLLER.search(test_code):
    print("Pattern works!")
else:
    print("Pattern needs fixing")
```

---

## Performance Considerations

### File Reading
- Uses `errors="ignore"` to handle encoding issues
- Reads entire file into memory (acceptable for Java files)

### Regex Performance
- Patterns compiled once at startup
- Use `re.DOTALL` sparingly (affects backtracking)
- Use raw strings (r"...") for regex patterns

### Scalability
- Tested on repos with 1000+ Java files
- Linear time complexity O(n*m) where n=files, m=file size
- Memory usage: ~10MB per 1000 Java files

---

## Debugging Tips

### Enable Verbose Logging
```bash
python main.py --repo /path --verbose
```

### Check Pattern Matches
```python
from patterns import get_patterns
patterns = get_patterns()
with open("file.java") as f:
    content = f.read()
matches = patterns.REST_CONTROLLER.findall(content)
print(matches)
```

### Inspect Analysis Result
```python
from analyzer import RepoAnalyzer
from pathlib import Path

analyzer = RepoAnalyzer(Path("/repo"))
result = analyzer.analyze()
print(f"Services: {len(result.services)}")
print(f"Endpoints: {len(result.rest_endpoints)}")
```

---

## Best Practices

### Code Quality
- ✅ Use type hints everywhere
- ✅ Keep functions small and focused
- ✅ Use meaningful variable names
- ✅ Add docstrings to all functions
- ✅ Handle exceptions gracefully
- ✅ Log important steps

### File Size
- ✅ Keep each file under 600 lines
- ✅ Split large modules into submodules
- ✅ Use composition over inheritance

### Regex Patterns
- ✅ Use raw strings (r"...")
- ✅ Document complex patterns
- ✅ Test patterns independently
- ✅ Use `re.IGNORECASE` when needed
- ✅ Handle edge cases (escaped quotes, etc.)

### Testing New Features
- ✅ Test on real code samples
- ✅ Verify edge cases
- ✅ Check false positives/negatives
- ✅ Document limitations

---

## Known Limitations

1. **Runtime Resolution**: Some values are determined at runtime (e.g., Kafka topics from variables)
2. **Complex Expressions**: Doesn't parse complex method expressions
3. **Generated Code**: Doesn't analyze generated code in `/target` directory
4. **Multi-File Context**: Doesn't track information across files (by design for speed)
5. **Version Detection**: Doesn't detect framework versions

---

## Future Enhancements

- [ ] AST-based analysis using Python's `ast` module
- [ ] Service-to-service call graph visualization
- [ ] Circular dependency detection
- [ ] API versioning analysis
- [ ] Database schema relationship mapping
- [ ] Security vulnerability scanning
- [ ] Performance bottleneck detection
- [ ] Test coverage analysis
- [ ] Web UI for interactive exploration
- [ ] Integration with CI/CD pipelines

---

## Questions?

Refer to:
- **User Guide**: See `README.md`
- **API Details**: Check docstrings in source code
- **Examples**: Run `python main.py --repo /path --verbose`

**Happy analyzing! 🐶**
