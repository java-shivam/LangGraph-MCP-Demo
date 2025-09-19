from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from src.a2a_lang_graph_executor import LangGraphExecutor
from src.lang_graph_client import MultiServerMCPClient 
from a2a.server.apps import A2AStarletteApplication
import uvicorn
import asyncio
import json

def main():
    # 1. Load MCP config
    JSON_DIR = "/Users/shivamverma/Documents/python/PycharmProjects/LangGraph-MCP-Demo/src/config/mcp_server.json"
    with open(JSON_DIR, "r") as f:
        mcp_config = json.load(f)
    
    # 2. Define the LangGraph skill
    langgraph_skill = AgentSkill(
        id="langgraph_agent",
        name="LangGraphAgent",
        description="Calls the LangGraph MCP agent",
        tags=["langgraph", "mcp", "ai"],
        examples=["Hello LangGraph", "Process my state graph"]
    )

    # 3. Define agent card
    agent_card = AgentCard(
        name="MultiAgent Server",
        description="Server exposing LangGraph agent",
        url="http://localhost:9999/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[langgraph_skill],
        version="1.0.0",
        capabilities=AgentCapabilities()
    )

    # 4. Get tools from MCP
    mcp_client = MultiServerMCPClient(connections=mcp_config)
    tools_list = asyncio.run(mcp_client.get_tools())

    # 5. Create executor instance
    langgraph_executor = LangGraphExecutor(tools_list)

    print("LangGraphExecutor type:", type(langgraph_executor))
    print("Has execute:", hasattr(langgraph_executor, "execute"))

    # 6. Register executor (single executor, not a dict)
    request_handler = DefaultRequestHandler(
        agent_executor=langgraph_executor,  # <-- direct instance
        task_store=InMemoryTaskStore()
    )

    # 7. Start server
    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=9999)


if __name__ == "__main__":
    main()
