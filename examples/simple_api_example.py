# Simple API Integration Example
# Demonstrates how to quickly create an MCP server for any REST API

from mcp_framework import FastMCPWrapper, APIKeyAuth, ConfigLoader

# Configuration
config = ConfigLoader().load_env()
auth = APIKeyAuth(env_var="EXAMPLE_API_KEY")

# Create server
server = FastMCPWrapper(
    name="example-api-server",
    config=config,
    auth=auth
)

@server.tool()
async def search_data(query: str, limit: int = 10) -> dict:
    """Search for data using the Example API"""
    import httpx
    
    url = "https://api.example.com/search"
    headers = auth.get_headers()
    params = {"q": query, "limit": limit}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

@server.tool()
async def get_item(item_id: str) -> dict:
    """Get a specific item by ID"""
    import httpx
    
    url = f"https://api.example.com/items/{item_id}"
    headers = auth.get_headers()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    server.run()
