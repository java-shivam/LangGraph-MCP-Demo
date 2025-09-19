"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""


import os
from typing import Any
import httpx

# Create an MCP server
#mcp = FastMCP("Demo")

from mcp.server.fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP(
    name="Shivam_MCP_Server",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8005,  # only used for SSE transport (set this to any port)
)


# Add an addition tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers and return the result."""
    return a * b

# @mcp.tool()
# def add_final_numbers(a: int, b: int) -> dict:
# @mcp.tool()
# def add_final_numbers(a: int, b: int) -> str:
#     """Add two final numbers and return the result."""
#     return f"The sum is {a + b}"

@mcp.tool()
def add(a: int, b: int) -> str:
    """Add two numbers and return as string."""
    return f"The sum of {a} and {b} is {a + b}"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

    #if __name__ == "__main__":
    # Allow configuration via environment variables to avoid port conflicts
    # MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
    # MCP_PORT = int(os.getenv("MCP_PORT", "8002"))
    # MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")
    # mcp.run(transport=MCP_TRANSPORT, host=MCP_HOST, port=MCP_PORT)

# Run the server
if __name__ == "__main__":

    # transport = "streamable-http"
    # if transport == "streamable-http":
    #     print("Running server with streamable-http transport")
    #     mcp.run(transport="streamable-http")

    transport ="stdio"
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")

    # transport = "sse"
    # if transport == "sse":
    #     print("Running server with SSE transport")
    #     mcp.run(transport="sse")
    else:
        raise ValueError(f"Unknown transport: {transport}")
