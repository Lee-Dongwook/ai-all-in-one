from typing import TYPE_CHECKING

from langgraph.graph import END

END_TARGETS = {"end", "END", str(END)}

def is_mutually_exclusive(a: str, b: str, conditional_targets: dict[str, set[str]], dominators: dict[str, set[str]]) -> bool:
    for source, targets in conditional_targets.items():
        if source not in dominators.get(a, ()) or source not in dominators.get(b, ()):
            continue
        for t in targets:
            for tx in targets:
                if t != tx and t in dominators.get(a,()) and tx in dominators.get(b,()):
                    return True
    return False

def compute_dominators(workflow: "") -> dict[str, set[str]]:
    names = {node.name for node in workflow.nodes}
    predecessors: dict[str, set[str]] = {}
    for edge in workflow.edges:
        if edge.edge_type == "end" or edge.target in END_TARGETS:
            continue
        if edge.target not in names or edge.source not in names:
            continue
        predecessors.setdefault(edge.target, set()).add(edge.source)
    
    start = workflow.start_node
    dominators = {name: ({name} if name == start else set(names)) for name in names}
    changed = True

    while changed:
        changed = False
        for name in names:
            if name == start:
                continue
            preds = predecessors.get(name, set())
            updated = (set.intersection(*(dominators[p] for p in preds)) | {name}) if preds else {name}
            if updated != dominators[name]:
                dominators[name] = updated
                changed = True
    return dominators

def reachable_from_start(workflow: "") -> set[str]:
    adjacency: dict[str, set[str]] = {}

    for edge in workflow.edges:
        if edge.edge_type == "end" or edge.target in END_TARGETS:
            continue
        adjacency.setdefault(edge.source, set()).add(edge.target)
    
    seen: set[str] = set()
    stack = [workflow.start_node]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(adjacency.get(current, ()))
    return seen

def compute_producers(workflow: "") -> dict[str, list[str]]:
    producers: dict[str, list[str]] = {}

    for node in workflow.nodes:
        action = node.action
        output_key = getattr(action, "output_key", None)
        if output_key:
            producers.setdefault(output_key, []).append(node.name)
        
        for target in getattr(action, "output_mapping", None) or {}:
            producers.setdefault(target, []).append(node.name)
    
    return producers


def compute_reachability(workflow: "") -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {}

    for edge in workflow.edges:
        if edge.edge_type == "end" or edge.target in END_TARGETS:
            continue
        adjacency.setdefault(edge.source, set()).add(edge.target)
    
    reachable: dict[str, set[str]] = {}
    for start in {node.name for node in workflow.nodes}:
        seen: set[str] = set()
        stack = list(adjacency.get(start, ()))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(adjacency.get(current, ()))
        reachable[start] = seen
    return reachable
