from agents.planner import (
    Planner
)


def planner_node(
    state
):

    state["action"] = (
        Planner.plan(
            state[
                "user_request"
            ]
        )
    )

    return state