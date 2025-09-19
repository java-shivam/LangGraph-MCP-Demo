from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, add_messages, START, END
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from typing import List, Annotated
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import BaseTool
import os
from src.model.agentstate import AgentState

from IPython.display import display, Image
from dotenv import load_dotenv
from langsmith import traceable
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_ollama import OllamaLLM
from mcp_use import MCPAgent, MCPClient
from langchain_ollama import ChatOllama
import os
from langchain_groq import ChatGroq


load_dotenv()
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")


PROJECT_ROOT1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("PROJECT_ROOT1 file PATH=",PROJECT_ROOT1)
JSON_DIR1 = os.path.join(PROJECT_ROOT1, "src/config")
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
print("JSON_DIR1 file PATH=",JSON_DIR1)
# Config
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# JSON_DIR = os.path.join(PROJECT_ROOT, "/config")
# LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")   # "ollama" or "groq"
# OLLAMA_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.1")
# GROQ_MODEL   = os.getenv("GROQ_LLM_MODEL", "llama-3.1-8b-instant")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# class AgentState(BaseModel):
#     messages: Annotated[List, add_messages]

# Config
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

# def save_graphviz(graph_obj, filename="diagram.png"):
#     dot = graphviz.Digraph(comment="LangGraph Diagram")
    
#     # Extract nodes and edges from Mermaid text
#     mermaid_text = graph_obj.draw_mermaid()
#     print("\n--- Mermaid source ---\n")
#     print(mermaid_text)

#     # Simple parser: look for lines with `-->`
#     for line in mermaid_text.splitlines():
#         if "-->" in line:
#             parts = line.strip().split("-->")
#             if len(parts) == 2:
#                 src = parts[0].strip()
#                 dst = parts[1].strip()
#                 dot.edge(src, dst)

#     dot.render(filename, format="png", cleanup=True)
#     print(f"✅ Saved graph image to {filename}.png")

def build_agent_graph(tools: List[BaseTool] = []):
    system_prompt = """
Your name is Scout and you are an expert data scientist. You help customers manage their data science projects by leveraging the tools available to you. Your goal is to collaborate with the customer in incrementally building their analysis or data modeling project. Version control is a critical aspect of this project, so you must use the git tools to manage the project's version history and maintain a clean, easy to understand commit history.

<filesystem>
You have access to a set of tools that allow you to interact with the user's local filesystem. 
You are only able to access files within the working directory `projects`. 
The absolute path to this directory is: {working_dir}
If you try to access a file outside of this directory, you will receive an error.
Always use absolute paths when specifying files.
</filesystem>

<version_control>
You have access to git and Github tools.
You should use git tools to manage the version history of the project and Github tools to manage the project's remote repository.
Keep a clean, logical commit history for the repo where each commit should represent a logical, atomic change.
</version_control>

<projects>
A project is a directory within the `projects` directory.
When using the create_new_project tool to create a new project, the following commands will be run for you:
    a. `mkdir <project_name>` - creates a new directory for the project
    b. `cd <project_name>` - changes to the new directory
    c. `uv init .` - initializes a new project
    d. `git init` - initializes a new git repository
    e. `mkdir data` - creates a data directory
Every project has the exact same structure.

<data>
When the user refers to data for a project, they are referring to the data within the `data` directory of the project.
All projects must use the `data` directory to store all data related to the project. 
The user can also load data into this directory.
You have a set of tools called dataflow that allow you to interact with the customer's data. 
The dataflow tools are used to load data into the session to query and work with it. 
You must always first load data into the session before you can do anything with it.
</data>

<code>
The main.py file is the entry point for the project and will contain all the code to load, transform, and model the data. 
You will primarily work on this file to complete the user's requests.
main.py should only be used to implement permanent changes to the data - to be commited to git. 
</code>

<tools>
{tools}
</tools>

Assist the customer in all aspects of their data science workflow.
"""

    llm = get_llm()#ChatGroq(model=GROQ_MODEL)
  
    if tools:
        llm = llm.bind_tools(tools)
        #inject tools into system prompt
        tools_json = [tool.model_dump_json(include=["name", "description"]) for tool in tools]
        system_prompt = system_prompt.format(
            tools="\n".join(tools_json), 
            working_dir=os.environ.get("MCP_FILESYSTEM_DIR")
            )

    def assistant(state: AgentState) -> AgentState:
        response = llm.invoke([SystemMessage(content=system_prompt)] + state.messages)
        state.messages.append(response)
        return state

    builder = StateGraph(AgentState)

    builder.add_node("LLMAgent", assistant)
    builder.add_node(ToolNode(tools))

    builder.add_edge(START, "LLMAgent")
    builder.add_conditional_edges(
        "LLMAgent",
        tools_condition,
    )
    builder.add_edge("tools", "LLMAgent")

    return builder.compile(checkpointer=MemorySaver())


# visualize graph
if __name__ == "__main__":
    graph_builder = build_agent_graph()
    print(graph_builder)
    graph_obj = graph_builder.get_graph()
    mermaid_text = graph_obj.draw_mermaid()
    print("\n--- Mermaid source ---\n")
    print(mermaid_text)

    # Always print Mermaid text
    # try:
    #     mermaid_text = graph_obj.draw_mermaid()
    #     print("\n--- Mermaid source ---\n")
    #     print(mermaid_text)
    # except Exception as e:
    #     print("⚠️ Could not generate Mermaid text:")

    # # Try rendering PNG
    # try:
    #     # ✅ First try local Pyppeteer method
    #     #png_bytes = graph_obj.draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)
    #     # Force Playwright method instead of Pyppeteer
    #     png_bytes = graph_obj.draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)
    #     print(png_bytes)
    # except Exception as e:
    #     print("❌ Could not render PNG from graph: USE LINK [https://www.mermaidchart.com/] to open ", e)





# visualize graph
# if __name__ == "__main__":
#     #display(Image(graph_builder.get_graph().draw_mermaid_png()))
#     graph_builder = build_agent_graph()
#     print(graph_builder)
#     graph_obj = graph_builder.get_graph()
#     try:
#         mermaid_text = graph_obj.draw_mermaid()
#         print("\n--- Mermaid source ---\n")
#         print(mermaid_text)
#     except Exception:
#         pass

#     try:
#         png_bytes = graph_obj.draw_mermaid_png()
#         out_path = os.path.join(os.getcwd(), "condition_langgraph_diagram.png")
#         with open(out_path, "wb") as f:
#             f.write(png_bytes)
#         print(f"Saved graph image to: {out_path}")
#         try:
#             import subprocess

#             if os.name == "posix":
#                 subprocess.run(["open", out_path])
#             else:
#                 subprocess.run([out_path], check=False)
#         except Exception:
#             pass
#     except Exception as e:
#         print("Could not render PNG from graph:", e)

#     try:
#         display(Image(graph_obj.draw_mermaid_png()))
#     except Exception:
#         pass