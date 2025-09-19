import asyncio
from dotenv import load_dotenv
load_dotenv()
from langchain_ollama import OllamaLLM
from mcp_use import MCPAgent, MCPClient
from langchain_ollama import ChatOllama
import os
from langchain_groq import ChatGroq

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.1")
#LLM_MODEL = os.getenv("LLM_MODEL")
load_dotenv()
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")


# Config
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DIR = os.path.join(PROJECT_ROOT, "/config")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")   # "ollama" or "groq"
OLLAMA_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.1")
GROQ_MODEL   = os.getenv("GROQ_LLM_MODEL", "llama-3.1-8b-instant")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def get_llm():
    """Factory to create an LLM client based on provider selection."""
    if LLM_PROVIDER.lower() == "groq":
        if not GROQ_API_KEY:
            raise ValueError("Missing GROQ_API_KEY in environment!")
        return ChatGroq(model=GROQ_MODEL, temperature=0)
    else:
        return ChatOllama(model=OLLAMA_MODEL)


async def run_memory_chat():
    """Run a chat using MCPAgent's built-in conversation memory."""
    # Load environment variables for API keys
    load_dotenv()
    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
    PROJECT_ROOT1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("PROJECT_ROOT1 file PATH=",PROJECT_ROOT1)
    JSON_DIR1 = os.path.join(PROJECT_ROOT1, "/config")
    print("JSON_DIR1 file PATH=",JSON_DIR1)

    # Config file path - change this to your config file

    config_file = PROJECT_ROOT1+JSON_DIR1+'/mcp_server.json'
    print("config file PATH=",config_file)
    print("Initializing chat...")

    # Create MCP client and agent with memory enabled
    client = MCPClient.from_config_file(config_file)
    llm =get_llm()
    #llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    #llm = ChatOllama(model=LLM_MODEL)
    # 🔑 Fetch MCP tools and bind them to the LLM
    #tools = await (client.list_tools())
    #llm_with_tools = llm.bind_tools(tools)

    # Create agent with memory_enabled=True
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True,# Enable built-in conversation memory
    )

    print("\n===== Interactive MCP Chat =====")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("==================================\n")

    try:
        # Main chat loop
        while True:
            # Get user input
            user_input = input("\nYou: ")

            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation...")
                break

            # Check for clear history command
            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue

            # Get response from agent
            print("\nAssistant: ", end="", flush=True)

            try:
                # Run the agent with the user input (memory handling is automatic)
                result = await agent.run(user_input)
                print(result)

            except Exception as e:
                print(f"\nError: {e}")

    finally:
        # Clean up
        if client and client.sessions:
            await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(run_memory_chat())