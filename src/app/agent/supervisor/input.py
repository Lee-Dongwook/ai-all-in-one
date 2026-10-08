import json
from typing import Any

from fastapi import HTTPException, status
from langchain_core.messages import(
    AIMessage,
    AnyMessage,
    ChatMessage,
    HumanMessage,
    ToolMessage,
)
from pydantic import ValidationError

from ...core import logger
from .state import AgentState

def _prepare_initial_messages(
    message: str | list[Any]
) -> list[AnyMessage]:
    messages: list[AnyMessage] = [HumanMessage(content=message)]

    return messages

def setup_initial_state(
    messages: list[AnyMessage],
    user_uuid: str,
    init_params: dict[str, Any] | None = None
) -> AgentState:
    initial_state = AgentState(
        messages=messages,
        user_uuid=user_uuid,
        structured_response=None,
    )

    logger.info(f"init_params={init_params}")
    #TODO:
