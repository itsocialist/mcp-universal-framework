"""
MCP Universal Framework

A comprehensive framework for accelerating Model Context Protocol (MCP) server development
by providing reusable components, templates, and best practices extracted from real-world implementations.

This framework extracts patterns from production MCP servers including:
- Social MCP Server (TypeScript service-oriented architecture)
- AI-CICD MCP Server (Natural language processing patterns)
"""

__version__ = "1.0.0"
__author__ = "MCP Framework Team"

# Core exports
from .core import (
    BaseMCPServer,
    FastMCPWrapper,
    SDKWrapper,
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
    ServerConfig
)

from .errors import (
    ErrorHandler,
    MCPError,
    ValidationError,
    AuthenticationError
)

from .service_oriented import (
    ServiceOrientedMCPServer,
    BaseService,
    PlatformService,
    ContentGeneratorService,
    AnalyticsService,
    SchedulerService
)

from .nlp_utils import (
    ContentRequestProcessor,
    RequirementsProcessor,
    IntentClassifier,
    standardize_response_format
)

from .templates.typescript_service import TypeScriptServiceTemplate
from .templates.base import BaseTemplate

__all__ = [
    # Version info
    "__version__",
    "__author__",
    
    # Core components
    "BaseMCPServer",
    "FastMCPWrapper", 
    "SDKWrapper",
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
    
    # Error handling
    "ErrorHandler",
    "MCPError",
    "ValidationError",
    "AuthenticationError",
    
    # Service-oriented architecture
    "ServiceOrientedMCPServer",
    "BaseService",
    "PlatformService",
    "ContentGeneratorService", 
    "AnalyticsService",
    "SchedulerService",
    
    # Natural language processing
    "ContentRequestProcessor",
    "RequirementsProcessor",
    "IntentClassifier",
    "standardize_response_format",
    
    # Templates
    "TypeScriptServiceTemplate",
    "BaseTemplate",
]
