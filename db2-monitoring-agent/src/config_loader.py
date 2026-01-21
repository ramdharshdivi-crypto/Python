"""Configuration loader for monitoring agent."""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Load and validate configuration from YAML file."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize config loader.
        
        Args:
            config_path: Path to config file. Defaults to config.yaml in current dir.
        """
        if config_path is None:
            config_path = "config.yaml"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.example.yaml to config.yaml and update settings."
            )
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self._validate()
        return self.config
    
    def _validate(self) -> None:
        """Validate required configuration fields.
        
        Raises:
            ValueError: If required fields are missing
        """
        # Validate DB2 config
        if 'db2' in self.config:
            db2_config = self.config['db2']
            
            # Check if using JDBC URL or traditional connection
            has_jdbc_url = 'jdbc_url' in db2_config
            has_traditional = all(k in db2_config for k in ['host', 'port', 'database'])
            
            # Must have either JDBC URL or traditional parameters
            if not has_jdbc_url and not has_traditional:
                raise ValueError(
                    "DB2 config must have either:\n"
                    "  1. 'jdbc_url' (e.g., jdbc:db2://hostname:port/database), OR\n"
                    "  2. 'host', 'port', and 'database' fields\n"
                    "See config.example.yaml for examples."
                )
            
            # Validate JDBC URL format if provided
            if has_jdbc_url:
                jdbc_url = db2_config['jdbc_url']
                if not jdbc_url.startswith('jdbc:db2://'):
                    raise ValueError(
                        f"Invalid JDBC URL format: {jdbc_url}\n"
                        f"JDBC URL must start with 'jdbc:db2://'\n"
                        f"Example: jdbc:db2://hostname:port/database"
                    )
                
                # Check that URL has required parts
                if '/' not in jdbc_url.replace('jdbc:db2://', ''):
                    raise ValueError(
                        f"Invalid JDBC URL format: {jdbc_url}\n"
                        f"JDBC URL must include database name\n"
                        f"Example: jdbc:db2://hostname:port/database"
                    )
            
            # Validate username and password (required for both methods)
            if 'username' not in db2_config:
                raise ValueError("Missing required DB2 field: username")
            if 'password' not in db2_config:
                raise ValueError("Missing required DB2 field: password")
        
        # Validate Kubernetes config
        if 'kubernetes' in self.config:
            k8s_config = self.config['kubernetes']
            if 'namespace' not in k8s_config:
                raise ValueError("Missing required Kubernetes field: namespace")
            
            # Must have either pod_name or label_selector
            if 'pod_name' not in k8s_config and 'label_selector' not in k8s_config:
                raise ValueError(
                    "Kubernetes config must have either 'pod_name' or 'label_selector'"
                )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Dot-notation key (e.g., 'db2.host')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to load configuration.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    loader = ConfigLoader(config_path)
    return loader.load()
