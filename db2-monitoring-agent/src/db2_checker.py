"""DB2 database health checker."""

import time
from typing import Dict, Any, Optional
from datetime import datetime

# Try to import DB2 drivers - support multiple options
DB2_DRIVER = None
DB2_DRIVER_TYPE = None

try:
    import ibm_db
    DB2_DRIVER = ibm_db
    DB2_DRIVER_TYPE = 'ibm_db'
except ImportError:
    try:
        import pyodbc
        DB2_DRIVER = pyodbc
        DB2_DRIVER_TYPE = 'pyodbc'
    except ImportError:
        pass  # No driver available


class DB2NotAvailableError(Exception):
    """Raised when no DB2 driver is available."""
    pass


class DB2HealthChecker:
    """Check DB2 database connectivity and execute queries."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize DB2 health checker.
        
        Args:
            config: DB2 configuration dictionary with host, port, database, etc.
            
        Raises:
            DB2NotAvailableError: If no DB2 driver is available
        """
        if DB2_DRIVER is None:
            raise DB2NotAvailableError(
                "No DB2 driver available. Please install one of:\n"
                "  1. ibm_db (requires IBM Data Server Driver)\n"
                "  2. pyodbc (with DB2 ODBC driver configured)\n"
                "\nSee README.md for installation instructions."
            )
        
        self.config = config
        self.connection = None
        self.driver_type = DB2_DRIVER_TYPE
        
    def _build_connection_string(self) -> str:
        """Build DB2 connection string based on driver type.
        
        Supports two connection methods:
        1. JDBC URL style: jdbc_url in config
        2. Traditional: host, port, database in config
        
        Returns:
            Connection string
        """
        username = self.config['username']
        password = self.config['password']
        
        # Check if JDBC URL is provided
        if 'jdbc_url' in self.config:
            jdbc_url = self.config['jdbc_url']
            
            # Parse JDBC URL to extract connection details
            # JDBC URL format: jdbc:db2://hostname:port/database
            if jdbc_url.startswith('jdbc:db2://'):
                # Extract parts from JDBC URL
                url_parts = jdbc_url.replace('jdbc:db2://', '').split('/')
                if len(url_parts) >= 2:
                    host_port = url_parts[0].split(':')
                    host = host_port[0]
                    port = host_port[1] if len(host_port) > 1 else '50000'
                    database = url_parts[1].split(';')[0].split('?')[0]  # Handle query params
                else:
                    raise ValueError(f"Invalid JDBC URL format: {jdbc_url}")
            else:
                raise ValueError(f"Invalid JDBC URL. Must start with 'jdbc:db2://'. Got: {jdbc_url}")
        else:
            # Traditional connection parameters
            host = self.config['host']
            port = self.config['port']
            database = self.config['database']
        
        # Build connection string based on driver type
        if self.driver_type == 'ibm_db':
            conn_str = (
                f"DATABASE={database};"
                f"HOSTNAME={host};"
                f"PORT={port};"
                f"PROTOCOL=TCPIP;"
                f"UID={username};"
                f"PWD={password};"
            )
        else:  # pyodbc
            # ODBC connection string for DB2
            conn_str = (
                f"DRIVER={{IBM DB2 ODBC DRIVER}};"
                f"DATABASE={database};"
                f"HOSTNAME={host};"
                f"PORT={port};"
                f"PROTOCOL=TCPIP;"
                f"UID={username};"
                f"PWD={password};"
            )
        
        return conn_str
    
    def connect(self) -> bool:
        """Establish connection to DB2 database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            conn_str = self._build_connection_string()
            
            if self.driver_type == 'ibm_db':
                self.connection = DB2_DRIVER.connect(conn_str, "", "")
            else:  # pyodbc
                self.connection = DB2_DRIVER.connect(conn_str)
            
            return True
        except Exception as e:
            print(f"DB2 connection failed: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Close DB2 connection."""
        if self.connection:
            try:
                if self.driver_type == 'ibm_db':
                    DB2_DRIVER.close(self.connection)
                else:  # pyodbc
                    self.connection.close()
            except Exception as e:
                print(f"Error closing connection: {str(e)}")
            finally:
                self.connection = None
    
    def execute_query(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Execute query and return result.
        
        Args:
            query: SQL query to execute. Uses config query if not provided.
            
        Returns:
            Dictionary with query result and metadata
        """
        if query is None:
            query = self.config.get('query', 'SELECT 1 FROM SYSIBM.SYSDUMMY1')
        
        result = {
            'success': False,
            'query': query,
            'result': None,
            'error': None,
            'execution_time_ms': 0
        }
        
        if not self.connection:
            result['error'] = "Not connected to database"
            return result
        
        try:
            start_time = time.time()
            
            if self.driver_type == 'ibm_db':
                stmt = DB2_DRIVER.exec_immediate(self.connection, query)
                
                # Fetch results
                rows = []
                row = DB2_DRIVER.fetch_assoc(stmt)
                while row:
                    rows.append(row)
                    row = DB2_DRIVER.fetch_assoc(stmt)
            else:  # pyodbc
                cursor = self.connection.cursor()
                cursor.execute(query)
                
                # Fetch results
                rows = []
                columns = [column[0] for column in cursor.description] if cursor.description else []
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    rows.append(row_dict)
                cursor.close()
            
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            
            result['success'] = True
            result['result'] = rows
            result['execution_time_ms'] = round(execution_time, 2)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def check_health(self) -> Dict[str, Any]:
        """Perform complete health check.
        
        Returns:
            Health check result dictionary
        """
        health_status = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'unknown',
            'connected': False,
            'query_executed': False,
            'response_time_ms': 0,
            'details': '',
            'error': None
        }
        
        # Try to connect
        if not self.connect():
            health_status['status'] = 'unhealthy'
            health_status['error'] = 'Failed to connect to DB2 database'
            
            # Build connection details for error message
            if 'jdbc_url' in self.config:
                conn_details = f"JDBC URL: {self.config['jdbc_url']}"
            else:
                conn_details = f"{self.config.get('host', 'unknown')}:{self.config.get('port', 'unknown')}"
            
            health_status['details'] = f"Could not connect to {conn_details}"
            return health_status
        
        health_status['connected'] = True
        
        # Execute query
        query_result = self.execute_query()
        
        if query_result['success']:
            health_status['status'] = 'healthy'
            health_status['query_executed'] = True
            health_status['response_time_ms'] = query_result['execution_time_ms']
            health_status['row_count'] = len(query_result['result'])
            health_status['query_results'] = query_result['result']  # Include actual query results
            health_status['query'] = query_result['query']  # Include the query that was executed
            health_status['details'] = f"Query executed successfully. Returned {len(query_result['result'])} row(s)."
        else:
            health_status['status'] = 'unhealthy'
            health_status['error'] = query_result['error']
            health_status['details'] = f"Query execution failed: {query_result['error']}"
        
        # Clean up
        self.disconnect()
        
        return health_status


def check_db2_health(config: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to check DB2 health.
    
    Args:
        config: DB2 configuration dictionary
        
    Returns:
        Health check result
    """
    try:
        checker = DB2HealthChecker(config)
        return checker.check_health()
    except DB2NotAvailableError as e:
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'error',
            'connected': False,
            'query_executed': False,
            'response_time_ms': 0,
            'details': 'DB2 driver not available',
            'error': str(e)
        }


def is_db2_available() -> bool:
    """Check if DB2 driver is available.
    
    Returns:
        True if a DB2 driver is available, False otherwise
    """
    return DB2_DRIVER is not None


def get_db2_driver_info() -> Dict[str, Any]:
    """Get information about available DB2 driver.
    
    Returns:
        Dictionary with driver information
    """
    return {
        'available': DB2_DRIVER is not None,
        'driver_type': DB2_DRIVER_TYPE,
        'driver_module': DB2_DRIVER.__name__ if DB2_DRIVER else None
    }
