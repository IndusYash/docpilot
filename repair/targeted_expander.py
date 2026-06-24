from llm import (
    LLMRouter
)

from llm.json_extractor import (
    JSONExtractor
)

from schemas.document import (
    Document
)

from prompts.document_prompt import (
    DOCUMENT_SYSTEM_PROMPT
)


class TargetedExpander:

    def __init__(self):

        self.router = (
            LLMRouter()
        )

    def expand(
        self,
        document,
        words_to_add
    ):

        prompt = f"""
Expand this document.

ADD APPROXIMATELY
{words_to_add}
WORDS.

RULES:

1. Keep all headings.
2. Keep all subsections.
3. Do not create sections.
4. Do not remove content.
5. Add useful explanation.
6. Add examples.
7. Preserve structure.

Return valid JSON only.

Document:

{document.model_dump_json(indent=2)}
"""

        response = (
            self.router.generate(
                prompt=prompt,
                system_prompt=
                DOCUMENT_SYSTEM_PROMPT
            )
        )

        response = (
            JSONExtractor.extract(
                response
            )
        )

        return (
            Document.model_validate_json(
                response
            )
        )