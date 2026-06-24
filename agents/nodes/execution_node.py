from agents.tools.generate_document_tool import (
    generate_document_tool
)


def execution_node(
    state
):

    action = (
        state[
            "action"
        ]
    )

    if (
        action
        ==
        "generate_document"
    ):

        return (
            generate_document_tool(
                state
            )
        )

    state[
        "result"
    ] = (
        "Unknown Action"
    )

    return state