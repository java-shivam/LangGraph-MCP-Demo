from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from src.lang_graph_client import build_agent_graph, AgentState
from langchain_core.messages import HumanMessage, AIMessageChunk
import uuid


class LangGraphExecutor(AgentExecutor):
    """
    LangGraph executor for A2AClient.
    Sends natural language requests through the full state graph,
    including LLM nodes and MCP tools, and returns the final
    LLM-formatted response with tool results.
    """
    def __init__(self, tools):
        # Build the full state graph including LLM node
        self.graph = build_agent_graph(tools=tools)

    async def get_full_response(self, input_state: AgentState, config: dict = {}) -> str:
        """
        Run the full LangGraph state graph and return the final
        LLM-generated response with tool outputs included.
        """
        buffer = []

        async for message_chunk, metadata in self.graph.astream(
            input=input_state,
            stream_mode="messages",
            config=config
        ):
            if isinstance(message_chunk, AIMessageChunk):
                # Include tool return values if present
                if hasattr(message_chunk, "tool_return") and message_chunk.tool_return:
                    buffer.append(str(message_chunk.tool_return))

                # Include final LLM content
                if message_chunk.content and message_chunk.content.strip():
                    buffer.append(message_chunk.content.strip())

        # Join all chunks into a single human-readable string
        return " ".join(buffer).strip()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """
        Execute LangGraph agent for an incoming A2A message.
        Supports natural language prompts transformed into tool calls
        automatically by the LLM node in the state graph.
        """
        # Extract user message from A2A context
        user_message = (
            context.message.parts[0].root.text
            if context.message and context.message.parts
            else "Run my LangGraph agent, add two numbers 23 and 45!"
        )

        # Build LangGraph input state
        state = AgentState(messages=[HumanMessage(content=user_message)])
        thread_id = str(getattr(context, "context_id", None) or uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Run full graph: LLM -> MCP tools
            response_text = await self.get_full_response(state, config=config)

            # Send final LLM response to A2A client
            if response_text and not event_queue.is_closed():
                await event_queue.enqueue_event(new_agent_text_message(response_text))

        except Exception as e:
            print("Executor error:", e)
            if not event_queue.is_closed():
                await event_queue.enqueue_event(
                    new_agent_text_message(f"❌ Executor failed: {e}")
                )

        finally:
            # Graceful termination
            if not event_queue.is_closed():
                await event_queue.enqueue_event(
                    new_agent_text_message("✅ Done processing LangGraph request.")
                )
                await event_queue.close()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")



# from a2a.server.agent_execution import AgentExecutor
# from a2a.server.agent_execution.context import RequestContext
# from a2a.server.events.event_queue import EventQueue
# from a2a.utils import new_agent_text_message
# from src.lang_graph_client import build_agent_graph, AgentState
# from langchain_core.messages import HumanMessage, AIMessageChunk
# import uuid

# class LangGraphExecutor(AgentExecutor):
#     """
#     Wraps a LangGraph MCP agent as an A2A agent with synchronous full response.
#     """
#     def __init__(self, tools):
#         self.graph = build_agent_graph(tools=tools)

#     async def get_full_response(self, input: AgentState, config: dict = {}) -> str:
#         """
#         Collect the full response from LangGraph instead of streaming,
#         preserving spaces and newlines.
#         """
#         buffer = []

#         async for message_chunk, metadata in self.graph.astream(
#             input=input,
#             stream_mode="messages",
#             config=config
#         ):
#             if isinstance(message_chunk, AIMessageChunk):
#                 # Handle tool calls
#                 if message_chunk.tool_call_chunks:
#                     for tool_chunk in message_chunk.tool_call_chunks:
#                         tool_name = tool_chunk.get("name", "")
#                         args = tool_chunk.get("args", "")
#                         if tool_name:
#                             buffer.append(f"\n\n< TOOL CALL: {tool_name} >\n\n")
#                         if args:
#                             buffer.append(str(args))

#                 # Normal content
#                 elif message_chunk.content.strip():
#                     buffer.append(message_chunk.content.strip())

#         # Join all chunks with a space to prevent words from running together
#         return " ".join(buffer)

#     async def execute(self, context: RequestContext, event_queue: EventQueue):
#         # Extract user message
#         user_message = (
#             context.message.parts[0].root.text
#             if context.message and context.message.parts
#             else "Run my LangGraph agent, add two numbers 23 and 45!"
#         )

#         # Build LangGraph input state
#         state = AgentState(messages=[HumanMessage(content=user_message)])
#         thread_id = str(getattr(context, "context_id", None) or uuid.uuid4())
#         config = {"configurable": {"thread_id": thread_id}}

#         try:
#             # Get full response
#             response_text = await self.get_full_response(state, config=config)

#             # Send it to the event queue as a single message
#             if response_text.strip() and not event_queue.is_closed():
#                 await event_queue.enqueue_event(new_agent_text_message(response_text))

#         except Exception as e:
#             print("Executor error:", e)
#             if not event_queue.is_closed():
#                 await event_queue.enqueue_event(new_agent_text_message(f"❌ Executor failed: {e}"))

#         finally:
#             # Send a done message and close queue
#             if not event_queue.is_closed():
#                 await event_queue.enqueue_event(new_agent_text_message("✅ Done processing LangGraph request."))
#                 await event_queue.close()

#     async def cancel(self, context: RequestContext, event_queue: EventQueue):
#         raise Exception("Cancel not supported")





# from a2a.server.agent_execution import AgentExecutor
# from a2a.server.agent_execution.context import RequestContext
# from a2a.server.events.event_queue import EventQueue
# from a2a.utils import new_agent_text_message
# from src.lang_graph_client import build_agent_graph, AgentState
# from langchain_core.messages import HumanMessage, AIMessageChunk
# import uuid

# class LangGraphExecutor(AgentExecutor):
#     """
#     Wraps a LangGraph MCP agent as an A2A agent with synchronous full response.
#     """
#     def __init__(self, tools):
#         self.graph = build_agent_graph(tools=tools)

#     async def get_full_response(self, input: AgentState, config: dict = {}) -> str:
#         """
#         Collect the full response from LangGraph instead of streaming.
#         """
#         buffer = ""
#         async for message_chunk, metadata in self.graph.astream(
#             input=input,
#             stream_mode="messages",
#             config=config
#         ):
#             if isinstance(message_chunk, AIMessageChunk):
#                 # Handle tool calls
#                 if message_chunk.tool_call_chunks:
#                     for tool_chunk in message_chunk.tool_call_chunks:
#                         tool_name = tool_chunk.get("name", "")
#                         args = tool_chunk.get("args", "")
#                         if tool_name:
#                             buffer += f"\n\n< TOOL CALL: {tool_name} >\n\n"
#                         if args:
#                             buffer += str(args)

#                 # Normal content
#                 elif message_chunk.content.strip():
#                     buffer += message_chunk.content.strip()

#         return buffer

#     async def execute(self, context: RequestContext, event_queue: EventQueue):
#         # Extract user message
#         user_message = (
#             context.message.parts[0].root.text
#             if context.message and context.message.parts
#             else "Run my LangGraph agent, add two numbers 23 and 45!"
#         )

#         # Build LangGraph input state
#         state = AgentState(messages=[HumanMessage(content=user_message)])
#         thread_id = str(getattr(context, "context_id", None) or uuid.uuid4())
#         config = {"configurable": {"thread_id": thread_id}}

#         try:
#             # Get full response
#             response_text = await self.get_full_response(state, config=config)

#             # Send it to the event queue as a single message
#             if response_text.strip() and not event_queue.is_closed():
#                 await event_queue.enqueue_event(new_agent_text_message(response_text))

#         except Exception as e:
#             print("Executor error:", e)
#             if not event_queue.is_closed():
#                 await event_queue.enqueue_event(new_agent_text_message(f"❌ Executor failed: {e}"))

#         finally:
#             # Send a done message and close queue
#             if not event_queue.is_closed():
#                 await event_queue.enqueue_event(new_agent_text_message("✅ Done processing LangGraph request."))
#                 await event_queue.close()

#     async def cancel(self, context: RequestContext, event_queue: EventQueue):
#         raise Exception("Cancel not supported")
