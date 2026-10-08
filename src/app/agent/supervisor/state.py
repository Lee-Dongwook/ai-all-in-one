from typing import Annotated, Any

from langgraph.graph import MessagesState
from langgraph.graph.ui import AnyUIMessage, ui_message_reducer
from langgraph.managed import RemainingSteps
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from typing_extensions import NotRequired

from ...core import logger

class BaseCondition(BaseModel):
    pass

class KeyExists(BaseCondition):
    key: str

class And(BaseCondition):
    conditions: list["Condition"]

Condition = KeyExists | And
And.model_rebuild()

def response_reducer(existing: dict[str, Any], new: dict[str, Any]| None) -> dict[str, Any]:
    if not existing:
        return new or {}
    
    if new is None:
        return {}
    
    result = existing.copy()
    for key, value in new.items():
        if not value: 
            continue
        
        if isinstance(value, dict):
            value = [value]
        
        if key in result:
            existing_value = result[key]
            if not isinstance(existing_value, list):
                existing_value = [existing_value]
                result[key] = existing_value
            
            if existing_value and (existing_value[-1] == value[0] or existing_value[-1] == value[-1]):
                continue

            result[key] = existing_value + value
        else:
            result[key] = value
    return result

def merge_unlocked_tools(left: list[str]| None, right: list[str] | None) -> list[str]:
    merged = list(left or [])
    merged += [name for name in (right or []) if name not in merged]
    return merged

class AgentState(MessagesState):
    user_uuid: str
    data_uuid: NotRequired[str | None]
    structured_response: Annotated[dict[str, Any], response_reducer]
    remaining_steps: RemainingSteps
    user_question: str
    language: str
    skill_ids: list[str] | None
    bound_deferred_tools: list[str] | None
    unlocked_tools: Annotated[list[str] | None, merge_unlocked_tools]
    ui: Annotated[list[AnyUIMessage], ui_message_reducer]
    values: dict[str, Any]
