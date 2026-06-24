from typing import TypedDict


class AgentState(TypedDict):

    user_request: str

    action: str

    result: str