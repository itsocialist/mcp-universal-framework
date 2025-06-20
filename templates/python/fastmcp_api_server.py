# FastMCP API Integration Template
# Based on patterns from Scenario.com and Meshy AI servers

import os
import asyncio
from typing import Dict, Any, Optional
from mcp_framework import FastMCPWrapper, APIKeyAuth, ConfigLoader, CommonErrors

# Load configuration
config = ConfigLoader()
config.load_env()  # Load from .env file

# Setup authentication - pattern from AI service servers
auth = APIKeyAuth(
    env_var="{{SERVICE_NAME}}_API_KEY",
    header_name="Authorization", 
    header_format="Bearer {}"
)

# Create server with unified framework
server = FastMCPWrapper(
    name="{{service_name}}-mcp-server",
    config=config,
    auth=auth
)

# Configuration constants
BASE_URL = config.get("{{SERVICE_NAME}}_BASE_URL", "https://api.{{service_name}}.com/v1")
DEFAULT_MODEL = config.get("{{SERVICE_NAME}}_MODEL_ID", "default-model")

class {{ServiceName}}Client:
    """API client following common patterns from analyzed servers"""
    
    def __init__(self, auth: APIKeyAuth, base_url: str):
        self.auth = auth
        self.base_url = base_url
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        headers.update(self.auth.get_headers())
        return headers
    
    async def make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Make authenticated API request with error handling"""
        import httpx
        
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                raise CommonErrors.api_error(
                    f"API request failed: {e.response.status_code}",
                    status_code=e.response.status_code,
                    response_body=e.response.text,
                    endpoint=endpoint
                )
            except Exception as e:
                raise CommonErrors.api_error(f"Request failed: {str(e)}")

# Initialize API client
api_client = {{ServiceName}}Client(auth, BASE_URL)

@server.tool()
async def {{sample_tool}}(prompt: str, model_id: Optional[str] = None) -> Dict[str, Any]:
    """
    {{Tool description}}
    
    Args:
        prompt: Text prompt for processing
        model_id: Model ID to use (defaults to configured model)
    
    Returns:
        dict: API response with job/task information
    """
    # Use provided model_id or fall back to default
    model_id = model_id or DEFAULT_MODEL
    
    # Prepare request payload - pattern from AI servers
    payload = {
        "prompt": prompt,
        "model_id": model_id,
        # Add other common parameters based on service
    }
    
    # Make API request
    response = await api_client.make_request("/{{endpoint}}", "POST", payload)
    
    # Extract common response patterns
    job_id = response.get("job", {}).get("jobId") or response.get("id")
    
    return {
        "job_id": job_id,
        "status": response.get("status", "submitted"),
        "full_response": response
    }

@server.tool()
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get job status and results
    
    Common pattern from all AI service servers for tracking long-running tasks.
    
    Args:
        job_id: ID of the job to check
        
    Returns:
        dict: Job status and results
    """
    response = await api_client.make_request(f"/jobs/{job_id}")
    return response

@server.resource("job://{job_id}")
async def job_resource(job_id: str) -> Dict[str, Any]:
    """
    Resource endpoint for job information
    
    Pattern from Scenario.com server for exposing job data as resources.
    """
    return await get_job_status(job_id)

@server.resource("status://info")
def server_status() -> Dict[str, Any]:
    """Server status information"""
    return {
        "server": "{{service_name}}-mcp-server",
        "version": "1.0.0",
        "status": "running",
        "auth_configured": auth.validate(),
        "base_url": BASE_URL
    }

if __name__ == "__main__":
    # Run the server
    server.run()
