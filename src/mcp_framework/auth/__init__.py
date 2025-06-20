"""
MCP Framework Authentication Module

Provides standardized authentication patterns extracted from existing MCP servers.
Supports multiple authentication methods commonly used in API integrations.
"""

import os
import base64
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class AuthConfig:
    """Configuration for authentication providers"""
    auth_type: str
    credentials: Dict[str, Any]
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


class BaseAuth(ABC):
    """Base authentication provider interface"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
    
    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Generate authentication headers for requests"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate authentication configuration"""
        pass


class APIKeyAuth(BaseAuth):
    """
    API Key authentication
    
    Pattern extracted from Scenario.com and Meshy AI servers.
    Supports various header formats and key locations.
    """
    
    def __init__(self, 
                 api_key: str = None,
                 env_var: str = None,
                 header_name: str = "Authorization",
                 header_format: str = "Bearer {}"):
        """
        Initialize API key authentication
        
        Args:
            api_key: Direct API key (not recommended for production)
            env_var: Environment variable name containing the API key
            header_name: HTTP header name for the API key
            header_format: Format string for the header value
        """
        self.api_key = api_key or os.getenv(env_var)
        self.header_name = header_name
        self.header_format = header_format
        
        if not self.api_key:
            raise ValueError(f"API key not found. Check {env_var} environment variable.")
    
    def get_headers(self) -> Dict[str, str]:
        """Generate authentication headers"""
        return {
            self.header_name: self.header_format.format(self.api_key)
        }
    
    def validate(self) -> bool:
        """Validate API key is present"""
        return bool(self.api_key)


class BasicAuth(BaseAuth):
    """
    Basic HTTP authentication
    
    Pattern extracted from Scenario.com server for API key/secret pairs.
    """
    
    def __init__(self, 
                 username: str = None,
                 password: str = None,
                 username_env: str = None,
                 password_env: str = None):
        """
        Initialize basic authentication
        
        Args:
            username: Username for basic auth
            password: Password for basic auth  
            username_env: Environment variable for username
            password_env: Environment variable for password
        """
        self.username = username or os.getenv(username_env)
        self.password = password or os.getenv(password_env)
        
        if not (self.username and self.password):
            raise ValueError("Both username and password are required for basic auth")
    
    def get_headers(self) -> Dict[str, str]:
        """Generate basic authentication headers"""
        # Create authorization string and encode it
        auth_string = f"{self.username}:{self.password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        return {
            "Authorization": f"Basic {auth_b64}"
        }
    
    def validate(self) -> bool:
        """Validate credentials are present"""
        return bool(self.username and self.password)


class TokenAuth(BaseAuth):
    """
    Token-based authentication
    
    For services that use access tokens with refresh capabilities.
    """
    
    def __init__(self,
                 access_token: str = None,
                 refresh_token: str = None,
                 token_env: str = None,
                 refresh_env: str = None,
                 token_type: str = "Bearer"):
        """
        Initialize token authentication
        
        Args:
            access_token: Access token
            refresh_token: Refresh token (optional)
            token_env: Environment variable for access token
            refresh_env: Environment variable for refresh token
            token_type: Token type (Bearer, JWT, etc.)
        """
        self.access_token = access_token or os.getenv(token_env)
        self.refresh_token = refresh_token or os.getenv(refresh_env)
        self.token_type = token_type
        
        if not self.access_token:
            raise ValueError(f"Access token not found. Check {token_env} environment variable.")
    
    def get_headers(self) -> Dict[str, str]:
        """Generate token authentication headers"""
        return {
            "Authorization": f"{self.token_type} {self.access_token}"
        }
    
    def validate(self) -> bool:
        """Validate token is present"""
        return bool(self.access_token)
    
    def refresh(self) -> bool:
        """Refresh access token (to be implemented by specific services)"""
        # This is a placeholder - specific implementations should override
        return False


class NoAuth(BaseAuth):
    """
    No authentication required
    
    For public APIs or internal services that don't require authentication.
    """
    
    def __init__(self):
        pass
    
    def get_headers(self) -> Dict[str, str]:
        """Return empty headers"""
        return {}
    
    def validate(self) -> bool:
        """Always valid for no auth"""
        return True


def create_auth_provider(auth_type: str, **kwargs) -> BaseAuth:
    """
    Factory function to create authentication providers
    
    Args:
        auth_type: Type of authentication ('api_key', 'basic', 'token', 'none')
        **kwargs: Arguments specific to the auth type
    
    Returns:
        BaseAuth: Configured authentication provider
    """
    auth_providers = {
        'api_key': APIKeyAuth,
        'basic': BasicAuth,
        'token': TokenAuth,
        'none': NoAuth
    }
    
    if auth_type not in auth_providers:
        raise ValueError(f"Unknown auth type: {auth_type}. Available: {list(auth_providers.keys())}")
    
    return auth_providers[auth_type](**kwargs)
