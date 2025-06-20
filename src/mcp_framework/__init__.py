"""
MCP Universal Framework

A comprehensive framework for accelerating Model Context Protocol (MCP) server development
by providing reusable components, templates, and best practices extracted from real-world implementations.

This framework extracts patterns from production MCP servers including:
- Social MCP Server (TypeScript service-oriented architecture)
- AI-CICD MCP Server (Natural language processing patterns)
"""

__version__ = "1.0.0"
- Rocky Linux AI Project (Build automation/CI-CD)

Key Features:
- Unified server interface for both FastMCP and traditional SDK
- Standardized authentication patterns
- Configuration management with multiple sources
- Comprehensive error handling
- Tool and resource registration patterns
- Natural language processing utilities
"""

__version__ = "1.0.0"
__author__ = "MCP Framework Team"

# Core exports
from .core import (
    BaseMCPServer,
    FastMCPWrapper,
    SDKWrapper,
    create_server,
    ToolDefinition
)

from .auth import (
    BaseAuth,
    APIKeyAuth,
    BasicAuth,
    TokenAuth,
    NoAuth,
    create_auth_provider
)

from .config import (
    ConfigLoader,
    ServerConfig,
    APIConfig,
    ConfigValidator,
    create_server_config,
    create_api_config,
    CommonConfigs
)

from .errors import (
    MCPError,
    ValidationError,
    AuthenticationError,
    APIError,
    TimeoutError,
    ToolError,
    ConfigurationError,
    ErrorHandler,
    ErrorResponse,
    ErrorCode,
    create_error_handler,
    CommonErrors
)

# Convenience aliases for common patterns
Server = create_server
Auth = create_auth_provider
Config = ConfigLoader
Errors = CommonErrors

__all__ = [
    # Core components
    "BaseMCPServer",
    "FastMCPWrapper", 
    "SDKWrapper",
    "create_server",
    "ToolDefinition",
    
    # Authentication
    "BaseAuth",
    "APIKeyAuth",
    "BasicAuth", 
    "TokenAuth",
    "NoAuth",
    "create_auth_provider",
    
    # Configuration
    "ConfigLoader",
    "ServerConfig",
    "APIConfig", 
    "ConfigValidator",
    "create_server_config",
    "create_api_config",
    "CommonConfigs",
    
    # Error handling
    "MCPError",
    "ValidationError",
    "AuthenticationError",
    "APIError",
    "TimeoutError",
    "ToolError",
    "ConfigurationError",
    "ErrorHandler",
    "ErrorResponse", 
    "ErrorCode",
    "create_error_handler",
    "CommonErrors",
    
    # Convenience aliases
    "Server",
    "Auth",
    "Config",
    "Errors"
]
