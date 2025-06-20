# Base template class for all MCP templates

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json

class BaseTemplate(ABC):
    """Base class for all MCP server templates"""
    
    def __init__(self, template_name: str, description: str):
        self.template_name = template_name
        self.description = description
    
    @abstractmethod
    def generate_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate all template files based on configuration"""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        required_fields = self.get_required_fields()
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        return errors
    
    def get_required_fields(self) -> List[str]:
        """Get list of required configuration fields"""
        return ['name', 'version']
    
    def get_optional_fields(self) -> List[str]:
        """Get list of optional configuration fields"""
        return ['description', 'author', 'license']
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            'name': 'my-mcp-server',
            'version': '1.0.0',
            'description': 'MCP Server generated from template',
            'author': 'MCP Developer',
            'license': 'MIT'
        }
