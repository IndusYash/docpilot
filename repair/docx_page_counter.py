from utils.word_counter import (
    WordCounter
)


class DocxPageCounter:

    WORDS_PER_PAGE = 300

    TITLE_COST = 25

    HEADING_COST = 15

    SUBHEADING_COST = 10

    PARAGRAPH_COST = 5

    @classmethod
    def estimate_pages(
        cls,
        document
    ):

        words = 0

        headings = 0

        subheadings = 0

        paragraphs = 0

        for section in document.sections:

            headings += 1

            paragraphs += 1

            words += WordCounter.count(
                section.content
            )

            for subsection in (
                section.sub_sections
            ):

                subheadings += 1

                paragraphs += 1

                words += WordCounter.count(
                    subsection.content
                )

        effective_words = (
            words
            + cls.TITLE_COST
            + (
                headings
                * cls.HEADING_COST
            )
            + (
                subheadings
                * cls.SUBHEADING_COST
            )
            + (
                paragraphs
                * cls.PARAGRAPH_COST
            )
        )

        pages = (
            effective_words
            / cls.WORDS_PER_PAGE
        )

        return round(
            pages,
            2
        )