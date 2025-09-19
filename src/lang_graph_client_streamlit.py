import streamlit as st
import asyncio
import os
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, AIMessageChunk
from src.graph.state_graph import build_agent_graph, AgentState


PROJECT_ROOT1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DIR1 = os.path.join(PROJECT_ROOT1, "src/config")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "graph" not in st.session_state:
    st.session_state["graph"] = None


async def stream_graph_response(input: AgentState, graph: StateGraph, config: dict = {}):
    async for message_chunk, metadata in graph.astream(
        input=input, stream_mode="messages", config=config
    ):
        if isinstance(message_chunk, AIMessageChunk):
            if message_chunk.tool_call_chunks:
                tool_chunk = message_chunk.tool_call_chunks[0]
                yield f"<TOOL CALL {tool_chunk.get('name', '')}> {tool_chunk.get('args', '')}"
            else:
                yield message_chunk.content


async def init_graph():
    """Load MCP servers and build graph."""
    config_file = os.path.join(JSON_DIR1, "mcp_server.json")
    with open(config_file, "r") as f:
        mcp_config = json.load(f)

    client = MultiServerMCPClient(connections=mcp_config)
    tools = await client.get_tools()
    return build_agent_graph(tools=tools)


async def run_agent(user_input: str):
    """Send user input through the graph and stream assistant response."""
    if st.session_state["graph"] is None:
        st.session_state["graph"] = await init_graph()

    graph_config = {"configurable": {"thread_id": "1"}}
    responses = []
    async for response in stream_graph_response(
        AgentState(messages=[HumanMessage(content=user_input)]),
        st.session_state["graph"],
        graph_config,
    ):
        responses.append(response)
    return "".join(responses)


# --------- STREAMLIT UI ---------
st.title("MCP LangGraph Client")

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state["messages"].append(("user", user_input))
    assistant_reply = asyncio.run(run_agent(user_input))
    st.session_state["messages"].append(("assistant", assistant_reply))

# Display conversation
for role, text in st.session_state["messages"]:
    if role == "user":
        st.chat_message("user").write(text)
    else:
        st.chat_message("assistant").write(text)
