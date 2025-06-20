# Getting Started with MCP Universal Framework

This guide will help you quickly create MCP servers using the Universal Framework's reusable components and templates.

## Prerequisites

- Python 3.8+ or Node.js 18+
- Basic understanding of Model Context Protocol (MCP)
- API credentials for external services (if building API integration servers)

## Installation

```bash
# Install the framework
pip install mcp-universal-framework

# Or install from source  
git clone <repository-url>
cd mcp-universal-framework
pip install -e .
```

## Quick Start

### 1. Choose Your Server Type

The framework supports multiple server patterns based on analyzed real-world implementations:

- **API Integration Server**: For connecting to external APIs (Scenario.com, Meshy AI pattern)
- **Tool Server**: For system commands and file operations (Dev Tools pattern)  
- **Build Server**: For CI/CD and automation tasks (Rocky Linux AI pattern)

### 2. Generate from Template

```bash
# Generate a FastMCP API server
mcp_framework generate --template fastmcp-api --name my-service

# Generate a traditional SDK tool server
mcp_framework generate --template sdk-tools --name my-tools

# Generate a TypeScript server
mcp_framework generate --template typescript --name my-ts-server
```

### 3. Basic Server Example

```python
from mcp_framework import FastMCPWrapper, APIKeyAuth, ConfigLoader

# Load configuration
config = ConfigLoader().load_env()

# Setup authentication
auth = APIKeyAuth(env_var="MY_API_KEY")

# Create server
server = FastMCPWrapper(
    name="my-server",
    config=config,
    auth=auth
)

@server.tool()
async def my_tool(param: str) -> dict:
    """My custom tool"""
    return {"result": f"Processed: {param}"}

if __name__ == "__main__":
    server.run()
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# API credentials
MY_API_KEY=your_api_key_here
MY_API_SECRET=your_secret_here

# Server settings
LOG_LEVEL=ERROR
TIMEOUT=30
MAX_RETRIES=3
```

### Configuration Loading

```python
from mcp_framework import ConfigLoader

# Load from multiple sources
config = ConfigLoader()
config.load_env()                    # Load .env file
config.load_file("config.json")     # Load JSON config
config.set("custom_setting", "value")  # Runtime config

# Get values with fallbacks
api_key = config.get_required("MY_API_KEY")
timeout = config.get("TIMEOUT", 30)
```

## Authentication

### API Key Authentication

```python
from mcp_framework import APIKeyAuth

# From environment variable
auth = APIKeyAuth(env_var="MY_API_KEY")

# Custom header format
auth = APIKeyAuth(
    env_var="MY_API_KEY",
    header_name="X-API-Key",
    header_format="{}"  # No prefix
)
```

### Basic Authentication

```python
from mcp_framework import BasicAuth

auth = BasicAuth(
    username_env="API_USERNAME",
    password_env="API_PASSWORD"
)
```

### Custom Authentication

```python
from mcp_framework import BaseAuth

class CustomAuth(BaseAuth):
    def get_headers(self) -> dict:
        return {"Authorization": f"Custom {self.token}"}
    
    def validate(self) -> bool:
        return bool(self.token)
```

## Error Handling

### Built-in Error Types

```python
from mcp_framework import ValidationError, APIError, CommonErrors

# Validation errors
if not param:
    raise ValidationError("Parameter required", parameter="param")

# API errors  
if response.status_code != 200:
    raise APIError("API request failed", status_code=response.status_code)

# Common patterns
raise CommonErrors.missing_api_key("MyService")
raise CommonErrors.invalid_model_id(model_id)
```

### Custom Error Handler

```python
from mcp_framework import ErrorHandler, create_error_handler

# Create with custom settings
error_handler = create_error_handler(include_traceback=True)

# Register custom handler
def handle_my_error(error):
    return ErrorResponse(code="MY_ERROR", message=str(error))

error_handler.register_error_handler(MyCustomError, handle_my_error)
```

## Tool Registration

### Automatic Parameter Extraction

```python
@server.tool()
async def process_data(
    text: str,                    # Required string parameter
    count: int = 10,             # Optional integer with default
    options: dict = None         # Optional object parameter
) -> dict:
    """Process text data with options"""
    options = options or {}
    return {"processed": text, "count": count, "options": options}
```

### Manual Schema Definition

```python
@server.tool(
    name="custom_tool",
    description="Custom tool with manual schema"
)
async def custom_tool(params: dict) -> dict:
    # Manual parameter validation
    if "required_param" not in params:
        raise ValidationError("required_param missing")
    
    return {"result": "success"}
```

## Resource Endpoints

```python
@server.resource("job://{job_id}")
async def job_resource(job_id: str) -> dict:
    """Resource endpoint for job information"""
    return await get_job_status(job_id)

@server.resource("status://info")
def server_status() -> dict:
    """Server status information"""
    return {
        "server": "my-server",
        "status": "running",
        "version": "1.0.0"
    }
```

## API Integration Pattern

### HTTP Client Setup

```python
import httpx
from mcp_framework import APIKeyAuth

class MyAPIClient:
    def __init__(self, auth: APIKeyAuth, base_url: str):
        self.auth = auth
        self.base_url = base_url
    
    async def make_request(self, endpoint: str, method: str = "GET", data: dict = None):
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            **self.auth.get_headers()
        }
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            
            response.raise_for_status()
            return response.json()
```

### Tool Implementation

```python
@server.tool()
async def create_job(prompt: str, model_id: str = None) -> dict:
    """Create a new processing job"""
    payload = {
        "prompt": prompt,
        "model_id": model_id or "default-model"
    }
    
    response = await api_client.make_request("/jobs", "POST", payload)
    
    return {
        "job_id": response.get("id"),
        "status": response.get("status", "submitted"),
        "full_response": response
    }
```

## Claude Desktop Integration

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/my-server/src/server.py"],
      "env": {
        "MY_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Development Tips

### Debugging

```python
# Enable debug logging
config.set("log_level", "DEBUG")

# Include tracebacks in errors
error_handler = create_error_handler(include_traceback=True)
```

### Testing

```python
import pytest
from mcp_framework.testing import MockServer

@pytest.fixture
def server():
    return MockServer("test-server")

def test_my_tool(server):
    result = server.call_tool("my_tool", {"param": "test"})
    assert result["result"] == "Processed: test"
```

### Hot Reload

```bash
# Run with auto-reload (development only)
mcp_framework dev src/server.py --reload
```

## Next Steps

- Check out the [Architecture Guide](architecture.md) for deeper understanding
- See [Examples](../examples/) for complete implementations
- Read the [Migration Guide](migration-guide.md) to upgrade existing servers
- Browse the [API Reference](api-reference.md) for detailed documentation

## Common Patterns

### AI Service Integration
- Use FastMCP for simplicity
- Implement job tracking for long-running tasks
- Add resource endpoints for status checking
- Handle API errors gracefully

### System Tool Servers
- Use traditional SDK for more control
- Implement command whitelisting for security
- Add timeout handling
- Validate file paths and arguments

### Build/CI Servers
- Use async operations for long builds
- Implement progress tracking
- Add artifact management
- Include comprehensive logging

Ready to build your MCP server? Start with one of our templates and customize as needed!
