from llm import LLMRouter
from llm.json_extractor import JSONExtractor

from prompts.outline_prompt import (
    OUTLINE_SYSTEM_PROMPT
)

from schemas.outline import (
    Outline
)

from chat.state import (
    ChatState
)


class OutlineGenerator:

    def __init__(self):

        self.router = LLMRouter()

    def _build_prompt(
        self,
        state: ChatState
    ):

        prompt = f"""
Create or improve a professional document outline.

Title:
{state.title}

Approximate Pages:
{state.pages}
"""

        if state.current_outline:

            prompt += f"""

Current Outline:

{state.current_outline.model_dump_json(
    indent=2
)}
"""

        if state.feedback_history:

            prompt += """

Feedback History:
"""

            for item in state.feedback_history:

                prompt += f"\n- {item}"

        return prompt

    def generate(
        self,
        state: ChatState
    ) -> Outline:

        prompt = self._build_prompt(
            state
        )

        response = self.router.generate(
            prompt=prompt,
            system_prompt=OUTLINE_SYSTEM_PROMPT
        )

        print(
            "\n===== OUTLINE RESPONSE =====\n"
        )

        print(response)

        response = (
            JSONExtractor.extract(
                response
            )
        )

        outline = (
            Outline.model_validate_json(
                response
            )
        )

        return outline