from agents.graph import (
    graph
)


result = (
    graph.invoke(
        {
            "user_request":
                "Create a report on AI"
        }
    )
)

print(
    result
)