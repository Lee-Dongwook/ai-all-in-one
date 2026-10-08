"""Minimal, compilable LangGraph supervisor entry point.

Domain-specific routing and tools can be added as nodes without changing the
public graph factory used by ``langgraph.json``.
"""

from langgraph.graph import END, START, StateGraph

from .state import AgentState


def create_graph():
    """Return the MVP graph with a stable LangGraph-compatible contract."""
    graph = StateGraph(AgentState)
    graph.add_edge(START, END)
    return graph.compile()
