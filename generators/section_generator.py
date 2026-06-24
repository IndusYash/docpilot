from llm import LLMRouter

from llm.json_extractor import (
    JSONExtractor
)

from prompts.section_prompt import (
    SECTION_SYSTEM_PROMPT
)

from schemas.document import (
    DocumentSection
)


class SectionGenerator:

    def __init__(self):

        self.router = LLMRouter()

    def generate(
        self,
        section_plan
    ):

        prompt = f"""
Generate this section.

Heading:
{section_plan.heading}

Target Words:
{section_plan.target_words}

Subsections:

{section_plan.model_dump_json(
    indent=2
)}
"""

        response = (
            self.router.generate(
                prompt=prompt,
                system_prompt=SECTION_SYSTEM_PROMPT
            )
        )
        print(
            "\n===== SECTION RESPONSE =====\n"
        )

        print(
            response
        )

        response = (
            JSONExtractor.extract(
                response
            )
        )

        return (
            DocumentSection.model_validate_json(
                response
            )
        )