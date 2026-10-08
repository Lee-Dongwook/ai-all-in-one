from typing import Any

from langchain_core.messages import AnyMessage, HumanMessage

from ...core.logger import logger
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
    """Build the smallest valid state passed into the supervisor graph."""
    initial_state: AgentState = {
        "messages": messages,
        "user_uuid": user_uuid,
        "structured_response": {},
        "unlocked_tools": [],
        "values": dict(init_params or {}),
    }

    logger.info("Supervisor initial state prepared for user=%s", user_uuid)
    return initial_state
