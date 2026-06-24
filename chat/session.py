from chat.message import Message


class ChatSession:

    def __init__(self):

        self.messages = []

    def add_user(
        self,
        content: str
    ):

        self.messages.append(
            Message(
                role="user",
                content=content
            )
        )

    def add_assistant(
        self,
        content: str
    ):

        self.messages.append(
            Message(
                role="assistant",
                content=content
            )
        )

    def get_context(self):

        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in self.messages
        ]