from pydantic import BaseModel
from typing import Annotated, List
from langgraph.graph import add_messages


class AgentState(BaseModel):
    messages: Annotated[List, add_messages]