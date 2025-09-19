Langgraph with MCP server
There are multiple MCP server ,we are going to connect with this LLM Agent

# The AI Launchpad

![SHIVAM MCP DEMO ](ai_launchpad/static/ai-launchpad-logo-wide.png)

This repo contains tutorials, code templates, and examples to help you build AI applications. Whether you're just learning or you have AI agents in production, I want to bring you as much value as possible. So please, open issues, leave me comments, and share your feedback.

> Note: I'm rapidly iterating on this repo so things will be broken and incomplete at times.

The AI Launchpad is a community for AI builders, entrepreneurs, and business leaders who want to learn, build, and solve real problems with AI. Get help, resources, connect with other builders, and accelerate your AI journey. 🚀

Sign up for the [**AI Launchpad**](https://kenneth-liao.kit.com/join) waitlist and get access to the Discord server (live now!).

## About Me 👋🏼

Hi! I'm Kenny, a Data Analytics Manager, AI Architect, and founder of the AI Launchpad. I also have a [YouTube channel](https://www.youtube.com/@KennethLiao) where **I teach you how to build AI solutions that solve real problems**.

---

## Getting Started

1. **Install UV to Manage Python Projects**

    [UV](https://docs.astral.sh/uv/) is a python project manager that replaces pip, poetry, pyenv, and more. It's 10-100x faster than pip and I recommend using it for all of your python projects.

    For MacOS it's easiest to install with homebrew:

    ```bash
    brew install uv
    ```

    For MacOS and Linux you can also run the following curl command:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    For Windows using irm:

    ```bash
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    There are several other ways to install uv. For more information, see the uv [documentation](https://docs.astral.sh/uv/getting-started/installation/).

2. **Clone the Repository and Navigate to the Project Directory**

    ```bash
    git clone https://github.com/kenneth-liao/ai-launchpad.git
    cd ai-launchpad
    ```

3. **Create a Virtual Environment and Install Dependencies**

    ```bash
    uv sync
    ```

    By default, uv will create a virtual environment for you in the `.venv` directory in your project root.

    This also installs the ai_launchpad project in editable mode so any changes to the codebase will be immediately reflected.

    Read more about managing python projects with [uv](https://docs.astral.sh/uv/guides/projects/).

4. **Copy the .env.example file to .env and add your API keys**

    If on MacOS or Linux you can run the following command:

    ```bash
    cp .env.example .env
    ```

    **REQUIRED KEYS**

    We use OpenAI as the default LLM provider and Tavily for search.

    **[Agents module](ai_launchpad/agents_module/README.md):**

    - [GROQ_API_KEY](https://platform.openai.com/account/api-keys) (required)
    - [TAVILY_API_KEY](https://tavily.com/) (required)

    **[Langgraph module](ai_launchpad/langgraph_module/README.md):**

    - [GROQ_API_KEY](https://platform.openai.com/account/api-keys) (required)
    - [TAVILY_API_KEY](https://tavily.com/) (required)
    - [LANGSMITH_API_KEY](https://smith.langchain.com/) (optional)

    I highly recommend getting a free Langsmith API key for observability which is critical for debugging and optimizing AI applications built with Langgraph.

    The project also has the Anthropic (langchain_anthropic) and Ollama (langchain_ollama) langchain integrations installed so you can easily switch to Anthropic or Ollama models if you prefer.

5. **Run the Code!**

    **This project uses ipykernel for interactive development!**

    I like it because you can...
    - Highlight blocks of code in any python file and run it in an interactive python window.
    - It's easy to experiment with code and see how each component works.

    Many of the example python files are written not as complete scripts, but rather as interactive files that you can run line by line. If you do run these files as scripts, you will see all of the outputs at once which may not be useful.

    Filenames that start with a number are meant to be run in interactive mode. Highlight the lines of code you want to run and press `shift+enter` to run them.

## Current Projects

As I release new tutorials and code templates, I'll add them here so make sure to follow the repo for updates!

At some point I'll also be migrating past projects from my Youtube channel to this repo.

### [Langgraph Module](ai_launchpad/langgraph_module/README.md)

1. [Building Effective Agents (langgraph_module/effective_agents)](ai_launchpad/langgraph_module/effective_agents/README.md)
2. [Frontends for Langgraph Agents (langgraph_module/frontends)](ai_launchpad/langgraph_module/frontends/README.md)
3. [Langgraph Server (langgraph_module/langgraph_server)](ai_launchpad/langgraph_module/langgraph_server/README.md)

### [Agents Module](ai_launchpad/agents_module/README.md)

1. [Agent From Scratch (agents_module/agent_from_scratch)](ai_launchpad/agents_module/agent_from_scratch/README.md)
2. [Agent With MCP (agents_module/agent_with_mcp)](ai_launchpad/agents_module/agent_with_mcp/README.md)