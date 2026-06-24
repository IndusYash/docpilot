from llm import (
    LLMRouter
)

from llm.json_extractor import (
    JSONExtractor
)

from schemas.document import (
    Document
)


COMPRESS_SYSTEM_PROMPT = """
You are a document compression agent.

Your task is to reduce document length.

Rules:

- Preserve all section headings.
- Preserve all subsection headings.
- Preserve document structure.
- Preserve readability.
- Remove redundant content.
- Remove repetitive explanations.
- Remove filler text.
- Never delete sections.
- Never delete subsection headings.

Return ONLY valid JSON.
"""


class TargetedCompressor:

    def __init__(self):

        self.router = (
            LLMRouter()
        )

    def compress(
        self,
        document,
        words_to_remove
    ):

        prompt = f"""
Reduce this document by approximately
{words_to_remove}
words.

IMPORTANT:

- Keep all headings.
- Keep all subsection headings.
- Keep the same JSON structure.
- Remove only low-value content.
- Do not add content.

Document:

{document.model_dump_json(indent=2)}
"""

        response = (
            self.router.generate(
                prompt=prompt,
                system_prompt=
                    COMPRESS_SYSTEM_PROMPT
            )
        )

        print(
            "\n===== COMPRESS RESPONSE =====\n"
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
            Document.model_validate_json(
                response
            )
        )