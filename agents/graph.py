from langgraph.graph import (
    StateGraph,
    END
)

from agents.state import (
    AgentState
)

from agents.nodes.planner_node import (
    planner_node
)

from agents.nodes.execution_node import (
    execution_node
)

from agents.router import (
    router
)


builder = (
    StateGraph(
        AgentState
    )
)

builder.add_node(
    "planner",
    planner_node
)

builder.add_node(
    "executor",
    execution_node
)

builder.set_entry_point(
    "planner"
)

builder.add_conditional_edges(
    "planner",
    router,
    {
        "generate_document":
            "executor",

        "unknown":
            END
    }
)

builder.add_edge(
    "executor",
    END
)

graph = (
    builder.compile()
)