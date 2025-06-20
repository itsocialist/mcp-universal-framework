"""
MCP Framework Error Handling Module

Provides standardized error handling patterns extracted from existing MCP servers.
Includes common error types, response formatting, and error recovery strategies.
"""

import traceback
from typing import Dict, Any, Optional, Type, Callable
from dataclasses import dataclass
from enum import Enum


class ErrorCode(Enum):
    """Standard error codes for MCP operations"""
    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    
    # Authentication errors
    AUTH_FAILED = "AUTH_FAILED"
    AUTH_MISSING = "AUTH_MISSING"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    
    # API errors
    API_ERROR = "API_ERROR"
    API_TIMEOUT = "API_TIMEOUT"
    API_RATE_LIMITED = "API_RATE_LIMITED"
    API_UNAVAILABLE = "API_UNAVAILABLE"
    
    # Tool errors
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    
    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ACCESS_DENIED = "RESOURCE_ACCESS_DENIED"
    
    # Configuration errors
    CONFIG_MISSING = "CONFIG_MISSING"
    CONFIG_INVALID = "CONFIG_INVALID"


@dataclass
class ErrorResponse:
    """Standardized error response format"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "error": {
                "code": self.code,
                "message": self.message
            }
        }
        
        if self.details:
            result["error"]["details"] = self.details
        
        if self.trace_id:
            result["error"]["trace_id"] = self.trace_id
            
        return result


class MCPError(Exception):
    """Base exception class for MCP framework errors"""
    
    def __init__(self, 
                 message: str, 
                 code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
                 details: Optional[Dict[str, Any]] = None,
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.original_error = original_error
    
    def to_response(self) -> ErrorResponse:
        """Convert to standardized error response"""
        return ErrorResponse(
            code=self.code.value,
            message=self.message,
            details=self.details
        )


class ValidationError(MCPError):
    """Parameter validation errors - pattern from all servers"""
    
    def __init__(self, message: str, parameter: str = None, expected_type: str = None):
        details = {}
        if parameter:
            details["parameter"] = parameter
        if expected_type:
            details["expected_type"] = expected_type
            
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_PARAMETER,
            details=details
        )


class AuthenticationError(MCPError):
    """Authentication related errors - pattern from API servers"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code=ErrorCode.AUTH_FAILED
        )


class APIError(MCPError):
    """External API errors - pattern from Scenario.com and Meshy AI"""
    
    def __init__(self, 
                 message: str,
                 status_code: Optional[int] = None,
                 response_body: Optional[str] = None,
                 endpoint: Optional[str] = None):
        details = {}
        if status_code:
            details["status_code"] = status_code
        if response_body:
            details["response_body"] = response_body
        if endpoint:
            details["endpoint"] = endpoint
            
        super().__init__(
            message=message,
            code=ErrorCode.API_ERROR,
            details=details
        )


class TimeoutError(MCPError):
    """Timeout errors - pattern from Dev Tools server"""
    
    def __init__(self, message: str = "Operation timed out", timeout_seconds: int = None):
        details = {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
            
        super().__init__(
            message=message,
            code=ErrorCode.TOOL_TIMEOUT,
            details=details
        )


class ToolError(MCPError):
    """Tool execution errors - pattern from Dev Tools server"""
    
    def __init__(self, 
                 message: str,
                 tool_name: str = None,
                 exit_code: Optional[int] = None,
                 stderr: Optional[str] = None):
        details = {}
        if tool_name:
            details["tool_name"] = tool_name
        if exit_code is not None:
            details["exit_code"] = exit_code
        if stderr:
            details["stderr"] = stderr
            
        super().__init__(
            message=message,
            code=ErrorCode.TOOL_EXECUTION_FAILED,
            details=details
        )


class ConfigurationError(MCPError):
    """Configuration errors - common pattern"""
    
    def __init__(self, message: str, config_key: str = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
            
        super().__init__(
            message=message,
            code=ErrorCode.CONFIG_INVALID,
            details=details
        )


class ErrorHandler:
    """
    Centralized error handling with customizable responses
    
    Pattern extracted from error handling in all analyzed servers.
    """
    
    def __init__(self, include_traceback: bool = False):
        """
        Initialize error handler
        
        Args:
            include_traceback: Include Python traceback in error responses
        """
        self.include_traceback = include_traceback
        self.error_mappings: Dict[Type[Exception], Callable] = {}
        self._setup_default_mappings()
    
    def _setup_default_mappings(self):
        """Setup default error type mappings"""
        self.error_mappings.update({
            ValidationError: self._handle_validation_error,
            AuthenticationError: self._handle_auth_error,
            APIError: self._handle_api_error,
            TimeoutError: self._handle_timeout_error,
            ToolError: self._handle_tool_error,
            ConfigurationError: self._handle_config_error,
            MCPError: self._handle_mcp_error,
            Exception: self._handle_generic_error
        })
    
    def handle_error(self, error: Exception) -> ErrorResponse:
        """
        Handle an error and return standardized response
        
        Args:
            error: Exception to handle
            
        Returns:
            ErrorResponse: Standardized error response
        """
        # Find the most specific handler
        for error_type, handler in self.error_mappings.items():
            if isinstance(error, error_type):
                return handler(error)
        
        # Fallback to generic handler
        return self._handle_generic_error(error)
    
    def register_error_handler(self, 
                              error_type: Type[Exception], 
                              handler: Callable[[Exception], ErrorResponse]):
        """Register custom error handler for specific error type"""
        self.error_mappings[error_type] = handler
    
    def _handle_validation_error(self, error: ValidationError) -> ErrorResponse:
        """Handle validation errors"""
        response = error.to_response()
        if self.include_traceback:
            response.details["traceback"] = traceback.format_exc()
        return response
    
    def _handle_auth_error(self, error: AuthenticationError) -> ErrorResponse:
        """Handle authentication errors"""
        response = error.to_response()
        # Don't include sensitive auth details in response
        return response
    
    def _handle_api_error(self, error: APIError) -> ErrorResponse:
        """Handle external API errors"""
        response = error.to_response()
        if self.include_traceback:
            response.details["traceback"] = traceback.format_exc()
        return response
    
    def _handle_timeout_error(self, error: TimeoutError) -> ErrorResponse:
        """Handle timeout errors"""
        return error.to_response()
    
    def _handle_tool_error(self, error: ToolError) -> ErrorResponse:
        """Handle tool execution errors"""
        response = error.to_response()
        if self.include_traceback:
            response.details["traceback"] = traceback.format_exc()
        return response
    
    def _handle_config_error(self, error: ConfigurationError) -> ErrorResponse:
        """Handle configuration errors"""
        return error.to_response()
    
    def _handle_mcp_error(self, error: MCPError) -> ErrorResponse:
        """Handle generic MCP errors"""
        response = error.to_response()
        if self.include_traceback:
            response.details["traceback"] = traceback.format_exc()
        return response
    
    def _handle_generic_error(self, error: Exception) -> ErrorResponse:
        """Handle unexpected generic errors"""
        details = {
            "error_type": type(error).__name__
        }
        
        if self.include_traceback:
            details["traceback"] = traceback.format_exc()
        
        return ErrorResponse(
            code=ErrorCode.UNKNOWN_ERROR.value,
            message=str(error),
            details=details
        )


def create_error_handler(include_traceback: bool = False) -> ErrorHandler:
    """
    Factory function to create error handler
    
    Args:
        include_traceback: Include Python traceback in responses
        
    Returns:
        ErrorHandler: Configured error handler
    """
    return ErrorHandler(include_traceback=include_traceback)


# Common error patterns from analyzed servers
class CommonErrors:
    """Pre-defined error scenarios from real MCP servers"""
    
    @staticmethod
    def missing_api_key(service_name: str) -> AuthenticationError:
        """Missing API key error - common in AI services"""
        return AuthenticationError(f"{service_name} API key not provided")
    
    @staticmethod
    def invalid_model_id(model_id: str) -> ValidationError:
        """Invalid model ID - common in AI services"""
        return ValidationError(
            f"Invalid model ID: {model_id}",
            parameter="model_id",
            expected_type="valid_model_identifier"
        )
    
    @staticmethod
    def command_not_allowed(command: str) -> ValidationError:
        """Command not in whitelist - Dev Tools pattern"""
        return ValidationError(
            f"Command not allowed: {command}",
            parameter="command"
        )
    
    @staticmethod
    def file_not_found(file_path: str) -> ValidationError:
        """File not found - common in file operations"""
        return ValidationError(
            f"File not found: {file_path}",
            parameter="file_path"
        )
    
    @staticmethod
    def build_failed(exit_code: int, stderr: str) -> ToolError:
        """Build failure - CI/CD pattern"""
        return ToolError(
            "Build process failed",
            tool_name="build",
            exit_code=exit_code,
            stderr=stderr
        )
