"""
This file implements the MCP Client for our Langgraph Agent.

MCP Clients are responsible for connecting and communicating with MCP servers. 
This client is analagous to Cursor or Claude Desktop and you would configure them in the 
same way by specifying the MCP server configuration in my_mcp/mcp_config.json.
"""

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, AIMessageChunk
from typing import AsyncGenerator
from src.graph.state_graph import build_agent_graph, AgentState
import asyncio
import os
import json


PROJECT_ROOT1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("PROJECT_ROOT1 file PATH=",PROJECT_ROOT1)
JSON_DIR1 = os.path.join(PROJECT_ROOT1, "src/config")
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
print("JSON_DIR1 file PATH=",JSON_DIR1)

# Config
# LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")   # "ollama" or "groq"
# OLLAMA_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.1")
# GROQ_MODEL   = os.getenv("GROQ_LLM_MODEL", "llama-3.1-8b-instant")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# def get_llm():
#     """Factory to create an LLM client based on provider selection."""
#     if LLM_PROVIDER.lower() == "groq":
#         if not GROQ_API_KEY:
#             raise ValueError("Missing GROQ_API_KEY in environment!")
#         return ChatGroq(model=GROQ_MODEL, temperature=0)
#     else:
#         return ChatOllama(model=OLLAMA_MODEL)

async def stream_graph_response_new(input: AgentState, graph: StateGraph, config: dict = {}):
    buffer = ""
    async for message_chunk, metadata in graph.astream(input=input, stream_mode="messages", config=config):
        if isinstance(message_chunk, AIMessageChunk):
            if message_chunk.tool_call_chunks:
                for tool_chunk in message_chunk.tool_call_chunks:
                    tool_name = tool_chunk.get("name", "")
                    args = tool_chunk.get("args", "")
                    if tool_name:
                        buffer += f"\n\n<TOOL CALL: {tool_name}>\n\n"
                    if args:
                        buffer += str(args)
            elif message_chunk.content.strip():
                buffer += message_chunk.content.strip()
        
        # Yield in batches
        if len(buffer) > 50:  # or another threshold
            yield buffer
            buffer = ""

    if buffer:
        yield buffer 

async def stream_graph_response(
        input: AgentState, graph: StateGraph, config: dict = {}
        ) -> AsyncGenerator[str, None]:
    """
    Stream the response from the graph while parsing out tool calls.

    Args:
        input: The input for the graph.
        graph: The graph to run.
        config: The config to pass to the graph. Required for memory.

    Yields:
        A processed string from the graph's chunked response.
    """
    async for message_chunk, metadata in graph.astream(
        input=input,
        stream_mode="messages",
        config=config
        ):
        if isinstance(message_chunk, AIMessageChunk):
            if message_chunk.response_metadata:
                finish_reason = message_chunk.response_metadata.get("finish_reason", "")
                if finish_reason == "tool_calls":
                    yield "\n\n"

            if message_chunk.tool_call_chunks:
                tool_chunk = message_chunk.tool_call_chunks[0]

                tool_name = tool_chunk.get("name", "")
                args = tool_chunk.get("args", "")
                
                if tool_name:
                    tool_call_str = f"\n\n< TOOL CALL: {tool_name} >\n\n"
                if args:
                    tool_call_str = args

                yield tool_call_str
            else:
                yield message_chunk.content
            continue


async def main():
    """
    Initialize the MCP client and run the agent conversation loop.

    The MultiServerMCPClient allows connection to multiple MCP servers using a single client and config.
    """
    # Load the JSON config
    JSON_DIR = "src/config/"
    config_file = os.path.join(PROJECT_ROOT1, JSON_DIR, "mcp_server.json")
    #config_file = JSON_DIR+'/mcp_server.json'

    with open(config_file, "r") as f:
        mcp_config = json.load(f)
    
    client = MultiServerMCPClient(connections=mcp_config)
    tools = await client.get_tools()
    
    # async with MultiServerMCPClient(
    #     connections=mcp_config
    # ) as client:
        # the get_tools() method returns a list of tools from all the connected servers
    #tools = client.get_tools()
    graph = build_agent_graph(tools=tools)

    # pass a config with a thread_id to use memory
    graph_config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    while True:
        user_input = input("\n\nUSER: ")
        if user_input in ["quit", "exit"]:
            break

        print("\n ----  USER  ---- \n\n", user_input)
        print("\n ----  ASSISTANT  ---- \n\n")

        async for response in stream_graph_response(
            input = AgentState(messages=[HumanMessage(content=user_input)]),
            graph = graph,
            config = graph_config
            ):
            print(response, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
# Streamlit page configuration
