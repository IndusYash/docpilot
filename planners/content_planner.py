from llm import LLMRouter

from llm.json_extractor import (
    JSONExtractor
)

from schemas.content_plan import (
    ContentPlan
)

from prompts.content_plan_prompt import (
    CONTENT_PLAN_SYSTEM_PROMPT
)


class ContentPlanner:

    def __init__(self):

        self.router = LLMRouter()

    def generate(
        self,
        outline,
        pages: int
    ) -> ContentPlan:

        total_words = (
            pages * 410
        )

        prompt = f"""
Create a content plan.

Target Words:
{total_words}

Outline:

{outline.model_dump_json(
    indent=2
)}
"""

        response = (
            self.router.generate(
                prompt=prompt,
                system_prompt=CONTENT_PLAN_SYSTEM_PROMPT
            )
        )

        response = (
            JSONExtractor.extract(
                response
            )
        )

        return (
            ContentPlan.model_validate_json(
                response
            )
        )