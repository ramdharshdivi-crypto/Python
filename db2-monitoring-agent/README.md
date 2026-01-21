# DB2 & Kubernetes Monitoring Agent 🐶

A monitoring agent that checks DB2 database connectivity and Kubernetes pod health status.

## Features

- 🗄️ **DB2 Health Check**: Connects to DB2 database and executes a query to verify functionality
- 🔗 **JDBC URL Support**: Use enterprise-standard JDBC URLs or traditional connection parameters
- ☸️ **Kubernetes Pod Monitor**: Checks if specified pods are running and healthy
- 📊 **Formatted Output**: Clear JSON/text output with status and details
- ⚙️ **Configurable**: Use YAML config file for all settings
- 🔄 **Backward Compatible**: Old configs still work!

## Prerequisites

- Python 3.8+
- Access to DB2 database
- Kubernetes cluster access (with valid kubeconfig)
- **DB2 Driver** - One of:
  - IBM DB2 client libraries (for `ibm_db`)
  - DB2 ODBC driver (for `pyodbc`)
  - See [INSTALL_DB2_DRIVERS.md](INSTALL_DB2_DRIVERS.md) for detailed installation instructions

> **Note**: The agent will gracefully skip DB2 checks if no driver is available, so you can still use Kubernetes monitoring independently.

## Installation

> **🏢 Walmart Employees**: See [WALMART_SETUP.md](WALMART_SETUP.md) for Walmart-specific installation using MyTech!

1. Create a virtual environment:
```bash
uv venv
```

2. Activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com
```

4. **Check DB2 driver availability**:
```bash
python main.py --check-drivers
```

If no DB2 driver is found, see [INSTALL_DB2_DRIVERS.md](INSTALL_DB2_DRIVERS.md) for installation instructions.

## Configuration

Copy `config.example.yaml` to `config.yaml` and update with your settings:

### Using JDBC URL (Recommended) ⭐

```yaml
db2:
  jdbc_url: "jdbc:db2://your-db2-host:50000/your-database"
  username: "your-username"
  password: "your-password"
  query: "SELECT 1 FROM SYSIBM.SYSDUMMY1"
```

### Using Traditional Parameters (Also Supported)

```yaml
db2:
  host: "your-db2-host"
  port: 50000
  database: "your-database"
  username: "your-username"
  password: "your-password"
  query: "SELECT 1 FROM SYSIBM.SYSDUMMY1"

kubernetes:
  namespace: "default"
  pod_name: "your-pod-name"
  # Optional: kubeconfig path (defaults to ~/.kube/config)
  kubeconfig_path: null

output:
  format: "json"  # json or text
  verbose: true
```

## Usage

### Basic Usage
```bash
python main.py
```

### With Custom Config
```bash
python main.py --config /path/to/config.yaml
```

### Check Only DB2
```bash
python main.py --check db2
```

### Check Only Kubernetes
```bash
python main.py --check k8s
```

## Output Example

```json
{
  "timestamp": "2026-01-05T16:05:00Z",
  "checks": {
    "db2": {
      "status": "healthy",
      "response_time_ms": 45,
      "query_result": "Success",
      "details": "Query executed successfully"
    },
    "kubernetes": {
      "status": "healthy",
      "pod_name": "my-app-pod-12345",
      "phase": "Running",
      "ready": true,
      "restart_count": 0
    }
  },
  "overall_status": "healthy"
}
```

## Project Structure

```
db2-monitoring-agent/
├── README.md
├── requirements.txt
├── config.example.yaml
├── main.py                    # Main orchestrator
├── src/
│   ├── __init__.py
│   ├── db2_checker.py        # DB2 connectivity checker
│   ├── k8s_checker.py        # Kubernetes pod checker
│   ├── config_loader.py      # Configuration management
│   └── output_formatter.py   # Output formatting utilities
└── tests/
    └── __init__.py
```

## Troubleshooting

### DB2 Driver Not Available

**Error**: `ImportError: DLL load failed while importing ibm_db`

**Solution**: See [INSTALL_DB2_DRIVERS.md](INSTALL_DB2_DRIVERS.md) for detailed installation instructions.

**Quick Fix**: Use pyodbc instead of ibm_db:
```bash
uv pip install pyodbc --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com
```

### DB2 Connection Issues
- Run `python main.py --check-drivers` to verify driver installation
- Ensure IBM DB2 client libraries are installed (see INSTALL_DB2_DRIVERS.md)
- Verify network connectivity to DB2 host
- Check credentials and database name

### Kubernetes Connection Issues
- Verify kubeconfig is properly set up
- Check RBAC permissions for pod listing
- Ensure namespace exists

## License

MIT License - Built with 🐶 Code Puppy
