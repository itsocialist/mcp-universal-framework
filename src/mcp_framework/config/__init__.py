"""
MCP Framework Configuration Module

Provides standardized configuration management patterns extracted from existing MCP servers.
Supports environment variables, .env files, and validation schemas.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class ServerConfig:
    """Base server configuration"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    log_level: str = "INFO"
    timeout: int = 30
    max_retries: int = 3
    
    # MCP specific
    capabilities: Dict[str, Any] = field(default_factory=dict)
    tools: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)


@dataclass  
class APIConfig:
    """API integration configuration"""
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    rate_limit: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Authentication
    auth_type: str = "none"
    auth_config: Dict[str, Any] = field(default_factory=dict)


class ConfigLoader:
    """
    Configuration loader with multiple source support
    
    Pattern extracted from all analyzed servers - supports:
    - Environment variables
    - .env files  
    - JSON/YAML config files
    - Runtime configuration
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration loader
        
        Args:
            config_dir: Directory to search for config files
        """
        self.config_dir = Path(config_dir) if config_dir else Path.cwd()
        self.config = {}
        self.env_loaded = False
    
    def load_env(self, env_file: str = ".env") -> "ConfigLoader":
        """
        Load environment variables from .env file
        
        Pattern from Scenario.com and Meshy AI servers.
        """
        env_path = self.config_dir / env_file
        if env_path.exists():
            load_dotenv(env_path)
            self.env_loaded = True
        return self
    
    def load_file(self, config_file: str) -> "ConfigLoader":
        """
        Load configuration from JSON or YAML file
        
        Args:
            config_file: Path to configuration file
        """
        config_path = self.config_dir / config_file
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            if config_file.endswith('.json'):
                file_config = json.load(f)
            elif config_file.endswith(('.yml', '.yaml')):
                file_config = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_file}")
        
        self.config.update(file_config)
        return self
    
    def set(self, key: str, value: Any) -> "ConfigLoader":
        """Set configuration value"""
        self.config[key] = value
        return self
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with environment variable fallback
        
        Checks in order: runtime config -> environment variables -> default
        """
        # Check runtime config first
        if key in self.config:
            return self.config[key]
        
        # Check environment variables
        env_value = os.getenv(key.upper())
        if env_value is not None:
            return self._parse_env_value(env_value)
        
        return default
    
    def get_required(self, key: str) -> Any:
        """Get required configuration value, raise error if missing"""
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required configuration key '{key}' not found")
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return all configuration as dictionary"""
        return self.config.copy()
    
    def validate_required(self, required_keys: List[str]) -> bool:
        """
        Validate that all required configuration keys are present
        
        Args:
            required_keys: List of required configuration keys
            
        Returns:
            bool: True if all required keys are present
            
        Raises:
            ValueError: If any required key is missing
        """
        missing_keys = []
        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        return True
    
    @staticmethod
    def _parse_env_value(value: str) -> Union[str, int, float, bool]:
        """Parse environment variable value to appropriate type"""
        # Boolean values
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        return value


class ConfigValidator:
    """
    Configuration validation utilities
    
    Provides validation patterns commonly needed in MCP servers.
    """
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    @staticmethod
    def validate_port(port: Union[str, int]) -> bool:
        """Validate port number"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod  
    def validate_log_level(level: str) -> bool:
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        return level.upper() in valid_levels


def create_server_config(name: str, **kwargs) -> ServerConfig:
    """
    Factory function to create server configuration
    
    Args:
        name: Server name
        **kwargs: Additional configuration options
    
    Returns:
        ServerConfig: Configured server instance
    """
    return ServerConfig(name=name, **kwargs)


def create_api_config(base_url: str, **kwargs) -> APIConfig:
    """
    Factory function to create API configuration
    
    Args:
        base_url: API base URL
        **kwargs: Additional configuration options
    
    Returns:
        APIConfig: Configured API instance
    """
    return APIConfig(base_url=base_url, **kwargs)


# Common configuration patterns from analyzed servers
class CommonConfigs:
    """Pre-configured setups for common MCP server patterns"""
    
    @staticmethod
    def ai_service_config(service_name: str, api_key_env: str, base_url: str) -> Dict[str, Any]:
        """Configuration for AI service integration (Scenario.com, Meshy AI pattern)"""
        return {
            "server": {
                "name": f"{service_name}-mcp-server",
                "version": "1.0.0",
                "log_level": "ERROR"  # Common pattern in AI servers
            },
            "api": {
                "base_url": base_url,
                "auth_type": "api_key",
                "auth_config": {
                    "env_var": api_key_env,
                    "header_name": "Authorization",
                    "header_format": "Bearer {}"
                },
                "timeout": 30,
                "max_retries": 3
            }
        }
    
    @staticmethod
    def tool_server_config(server_name: str) -> Dict[str, Any]:
        """Configuration for tool/command servers (Dev Tools pattern)"""
        return {
            "server": {
                "name": server_name,
                "version": "1.0.0",
                "capabilities": {"tools": {}}
            },
            "security": {
                "allowed_commands": [],  # Whitelist pattern
                "timeout": 30,
                "max_output_size": 1024 * 1024  # 1MB limit
            }
        }
    
    @staticmethod
    def build_server_config(project_name: str) -> Dict[str, Any]:
        """Configuration for build/CI servers (Rocky Linux AI pattern)"""
        return {
            "server": {
                "name": f"{project_name}-build-server",
                "version": "1.0.0"
            },
            "build": {
                "output_dir": "output",
                "temp_dir": "tmp", 
                "parallel_jobs": 4,
                "timeout": 3600  # 1 hour for builds
            },
            "artifacts": {
                "retention_days": 30,
                "compression": True
            }
        }
