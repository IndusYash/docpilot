import os

from datetime import datetime

from docx import (
    Document as WordDocument
)

from docx.shared import Inches

from builder.style_engine import (
    StyleEngine
)


class DocxBuilder:

    def build(
        self,
        document_data,
        output_path: str
    ):

        os.makedirs(
            os.path.dirname(
                output_path
            ),
            exist_ok=True
        )

        doc = WordDocument()

        # ======================
        # PAGE MARGINS
        # ======================

        page_section = (
            doc.sections[0]
        )

        page_section.top_margin = (
            Inches(1)
        )

        page_section.bottom_margin = (
            Inches(1)
        )

        page_section.left_margin = (
            Inches(1)
        )

        page_section.right_margin = (
            Inches(1)
        )

        # ======================
        # TITLE
        # ======================

        StyleEngine.apply_title(
            doc,
            document_data.title
        )

        # ======================
        # MAIN CONTENT
        # ======================

        for section in (
            document_data.sections
        ):

            print(
                f"\nWriting Section: "
                f"{section.heading}"
            )

            StyleEngine.apply_heading(
                doc,
                section.heading
            )

            StyleEngine.apply_body_text(
                doc,
                section.content
            )

            print(
                f"Subsections Found: "
                f"{len(section.sub_sections)}"
            )

            for subsection in (
                section.sub_sections
            ):

                print(
                    f"  -> {subsection.heading}"
                )

                StyleEngine.apply_subheading(
                    doc,
                    subsection.heading
                )

                StyleEngine.apply_body_text(
                    doc,
                    subsection.content
                )

        if not output_path:
            timestamp = (
                datetime.now()
                .strftime(
                    "%Y%m%d_%H%M%S"
                )
            )
            output_path = (
                f"output/generated_report_"
                f"{timestamp}.docx"
            )

        doc.save(
            output_path
        )

        return output_path