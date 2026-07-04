from schemas.document import (
    Document
)

from generators.section_generator import (
    SectionGenerator
)


class DocumentGenerator:

    def __init__(self):

        self.section_generator = (
            SectionGenerator()
        )

    def generate(
        self,
        outline,
        content_plan,
        quality_feedback: str = None
    ):

        sections = []

        total = len(
            content_plan.sections
        )

        for index, section_plan in enumerate(
            content_plan.sections,
            start=1
        ):

            print(
                f"\nGenerating Section "
                f"{index}/{total}"
            )

            generated_section = (
                self.section_generator.generate(
                    section_plan,
                    quality_feedback=quality_feedback
                )
            )

            print(
                "\n===== PARSED SECTION =====\n"
            )

            print(
                generated_section.model_dump_json(
                    indent=4
                )
            )

            print(
                "\nSubsections Parsed: "
                f"{len(generated_section.sub_sections)}"
            )

            sections.append(
                generated_section
            )

        document = Document(
            title=outline.title,
            sections=sections
        )

        print(
            "\n===== FINAL DOCUMENT OBJECT =====\n"
        )

        print(
            document.model_dump_json(
                indent=4
            )
        )

        return document