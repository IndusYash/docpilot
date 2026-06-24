from schemas.outline import Outline


class ChatState:

    def __init__(self):

        self.title = ""

        self.pages = 0

        self.current_outline = None

        self.feedback_history = []

    def add_feedback(
        self,
        feedback: str
    ):

        self.feedback_history.append(
            feedback
        )