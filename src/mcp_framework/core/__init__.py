"""
MCP Framework Core Module

Provides base server classes and common patterns extracted from existing MCP servers.
Supports both FastMCP and traditional SDK approaches with unified interface.
"""

import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass

# Import MCP SDK components
try:
    from mcp.server.fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

try:
    from mcp.server import Server
    from mcp.server.stdio import StdioServerTransport
    from mcp.types import (
        CallToolRequestSchema,
        ListToolsRequestSchema,
        Tool,
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

from ..auth import BaseAuth, create_auth_provider
from ..config import ConfigLoader, ServerConfig
from ..errors import ErrorHandler, MCPError, ValidationError


@dataclass
class ToolDefinition:
    """Tool definition with metadata"""
    name: str
    function: Callable
    description: str
    parameters: Dict[str, Any]
    async_tool: bool = False


class BaseMCPServer(ABC):
    """
    Base MCP server class providing common functionality
    
    Abstract base for both FastMCP and SDK implementations.
    Provides unified interface regardless of underlying implementation.
    """
    
    def __init__(self, 
                 name: str,
                 config: Optional[Union[Dict, ConfigLoader]] = None,
                 auth: Optional[BaseAuth] = None,
                 error_handler: Optional[ErrorHandler] = None):
        """
        Initialize base MCP server
        
        Args:
            name: Server name
            config: Configuration dict or ConfigLoader instance
            auth: Authentication provider
            error_handler: Error handler instance
        """
        self.name = name
        self.config = self._setup_config(config)
        self.auth = auth
        self.error_handler = error_handler or ErrorHandler()
        self.tools: Dict[str, ToolDefinition] = {}
        self.resources: Dict[str, Callable] = {}
        self._server = None
    
    def _setup_config(self, config: Optional[Union[Dict, ConfigLoader]]) -> ConfigLoader:
        """Setup configuration from various sources"""
        if isinstance(config, ConfigLoader):
            return config
        elif isinstance(config, dict):
            loader = ConfigLoader()
            for key, value in config.items():
                loader.set(key, value)
            return loader
        else:
            # Create default config
            loader = ConfigLoader()
            loader.load_env()  # Try to load .env file
            return loader
    
    @abstractmethod
    def _create_server(self) -> Any:
        """Create the underlying MCP server instance"""
        pass
    
    @abstractmethod
    def run(self):
        """Run the MCP server"""
        pass
    
    def tool(self, name: Optional[str] = None, description: Optional[str] = None):
        """
        Decorator to register tools
        
        Unified interface for both FastMCP and SDK patterns.
        """
        def decorator(func: Callable):
            tool_name = name or func.__name__
            tool_description = description or func.__doc__ or f"Tool: {tool_name}"
            
            # Extract parameter schema from function signature
            sig = inspect.signature(func)
            parameters = self._extract_parameters(sig)
            
            # Check if function is async
            is_async = asyncio.iscoroutinefunction(func)
            
            tool_def = ToolDefinition(
                name=tool_name,
                function=func,
                description=tool_description,
                parameters=parameters,
                async_tool=is_async
            )
            
            self.tools[tool_name] = tool_def
            return func
        
        return decorator
    
    def resource(self, uri_pattern: str):
        """
        Decorator to register resources
        
        Args:
            uri_pattern: Resource URI pattern (e.g., "job://{job_id}")
        """
        def decorator(func: Callable):
            self.resources[uri_pattern] = func
            return func
        
        return decorator
    
    def _extract_parameters(self, signature: inspect.Signature) -> Dict[str, Any]:
        """Extract parameter schema from function signature"""
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in signature.parameters.items():
            # Skip 'self' parameter
            if param_name == 'self':
                continue
            
            param_schema = {"type": "string"}  # Default type
            
            # Extract type from annotation
            if param.annotation != inspect.Parameter.empty:
                param_schema = self._type_to_schema(param.annotation)
            
            # Extract description from docstring if available
            # (This is a simplified approach - could be enhanced with proper docstring parsing)
            
            parameters["properties"][param_name] = param_schema
            
            # Mark as required if no default value
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
        
        return parameters
    
    def _type_to_schema(self, annotation: type) -> Dict[str, Any]:
        """Convert Python type annotation to JSON schema"""
        type_mapping = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            list: {"type": "array"},
            dict: {"type": "object"}
        }
        
        # Handle Optional types
        if hasattr(annotation, '__origin__'):
            if annotation.__origin__ is Union:
                # Handle Optional[T] which is Union[T, None]
                non_none_types = [arg for arg in annotation.__args__ if arg is not type(None)]
                if len(non_none_types) == 1:
                    return self._type_to_schema(non_none_types[0])
        
        return type_mapping.get(annotation, {"type": "string"})
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with error handling
        
        Common execution pattern extracted from all servers.
        """
        if tool_name not in self.tools:
            raise ValidationError(f"Tool '{tool_name}' not found")
        
        tool_def = self.tools[tool_name]
        
        try:
            # Validate arguments against tool schema
            self._validate_arguments(tool_def, arguments)
            
            # Execute tool function
            if tool_def.async_tool:
                result = await tool_def.function(**arguments)
            else:
                result = tool_def.function(**arguments)
            
            # Ensure result is JSON serializable
            if not isinstance(result, (dict, list, str, int, float, bool, type(None))):
                result = {"result": str(result)}
            
            return result
            
        except Exception as e:
            # Convert to MCP error and re-raise
            if isinstance(e, MCPError):
                raise
            else:
                raise MCPError(f"Tool execution failed: {str(e)}", original_error=e)
    
    def _validate_arguments(self, tool_def: ToolDefinition, arguments: Dict[str, Any]):
        """Validate tool arguments against schema"""
        required_params = tool_def.parameters.get("required", [])
        properties = tool_def.parameters.get("properties", {})
        
        # Check required parameters
        for required_param in required_params:
            if required_param not in arguments:
                raise ValidationError(
                    f"Missing required parameter: {required_param}",
                    parameter=required_param
                )
        
        # Basic type validation (could be enhanced with jsonschema)
        for param_name, param_value in arguments.items():
            if param_name in properties:
                expected_type = properties[param_name].get("type")
                if not self._validate_type(param_value, expected_type):
                    raise ValidationError(
                        f"Invalid type for parameter {param_name}",
                        parameter=param_name,
                        expected_type=expected_type
                    )
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Basic type validation"""
        type_validators = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int),
            "number": lambda v: isinstance(v, (int, float)),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, list),
            "object": lambda v: isinstance(v, dict)
        }
        
        validator = type_validators.get(expected_type)
        return validator(value) if validator else True


class FastMCPWrapper(BaseMCPServer):
    """
    FastMCP implementation wrapper
    
    Pattern extracted from Scenario.com and Meshy AI servers.
    """
    
    def __init__(self, *args, **kwargs):
        if not FASTMCP_AVAILABLE:
            raise ImportError("FastMCP not available. Install with: pip install mcp")
        
        super().__init__(*args, **kwargs)
    
    def _create_server(self):
        """Create FastMCP server instance"""
        log_level = self.config.get("log_level", "ERROR")
        return FastMCP(self.name, log_level=log_level)
    
    def run(self):
        """Run FastMCP server"""
        if self._server is None:
            self._server = self._create_server()
            self._register_tools()
            self._register_resources()
        
        # FastMCP handles the run loop automatically
        return self._server
    
    def _register_tools(self):
        """Register tools with FastMCP"""
        for tool_name, tool_def in self.tools.items():
            # FastMCP uses decorators, so we need to register the function
            self._server.tool()(tool_def.function)
    
    def _register_resources(self):
        """Register resources with FastMCP"""
        for uri_pattern, resource_func in self.resources.items():
            self._server.resource(uri_pattern)(resource_func)


class SDKWrapper(BaseMCPServer):
    """
    Traditional MCP SDK implementation wrapper
    
    Pattern extracted from Dev Tools server.
    """
    
    def __init__(self, *args, **kwargs):
        if not SDK_AVAILABLE:
            raise ImportError("MCP SDK not available. Install with: pip install mcp")
        
        super().__init__(*args, **kwargs)
    
    def _create_server(self):
        """Create traditional SDK server instance"""
        if not SDK_AVAILABLE:
            raise ImportError("MCP SDK not available")
            
        version = self.config.get("version", "1.0.0")
        capabilities = self.config.get("capabilities", {"tools": {}})
        
        return Server(
            name=self.name,
            version=version,
            capabilities=capabilities
        )
    
    def run(self):
        """Run SDK server with stdio transport"""
        if self._server is None:
            self._server = self._create_server()
            self._setup_handlers()
        
        async def run_server():
            transport = StdioServerTransport()
            await self._server.run(transport)
        
        asyncio.run(run_server())
    
    def _setup_handlers(self):
        """Setup SDK request handlers"""
        self._server.setRequestHandler(ListToolsRequestSchema, self._handle_list_tools)
        self._server.setRequestHandler(CallToolRequestSchema, self._handle_call_tool)
    
    async def _handle_list_tools(self, request) -> Dict[str, Any]:
        """Handle list tools request"""
        tools = []
        for tool_name, tool_def in self.tools.items():
            tool = Tool(
                name=tool_name,
                description=tool_def.description,
                inputSchema=tool_def.parameters
            )
            tools.append(tool)
        
        return {"tools": tools}
    
    async def _handle_call_tool(self, request) -> Dict[str, Any]:
        """Handle call tool request"""
        tool_name = request.params.name
        arguments = request.params.arguments or {}
        
        try:
            result = await self._execute_tool(tool_name, arguments)
            return {"content": [{"type": "text", "text": str(result)}]}
        except Exception as e:
            error_response = self.error_handler.handle_error(e)
            return {
                "isError": True,
                "content": [{"type": "text", "text": str(error_response.to_dict())}]
            }


def create_server(server_type: str = "auto", **kwargs) -> BaseMCPServer:
    """
    Factory function to create MCP server
    
    Args:
        server_type: Type of server ('fastmcp', 'sdk', 'auto')
        **kwargs: Arguments passed to server constructor
    
    Returns:
        BaseMCPServer: Configured server instance
    """
    if server_type == "auto":
        # Auto-detect best available implementation
        if FASTMCP_AVAILABLE:
            server_type = "fastmcp"
        elif SDK_AVAILABLE:
            server_type = "sdk"
        else:
            raise ImportError("Neither FastMCP nor MCP SDK available")
    
    if server_type == "fastmcp":
        return FastMCPWrapper(**kwargs)
    elif server_type == "sdk":
        return SDKWrapper(**kwargs)
    else:
        raise ValueError(f"Unknown server type: {server_type}")
