class WordCounter:

    @staticmethod
    def count(
        text
    ):

        if not text:

            return 0

        return len(
            text.split()
        )

    @classmethod
    def count_document(
        cls,
        document
    ):

        total = 0

        for section in (
            document.sections
        ):

            total += cls.count(
                section.content
            )

            for subsection in (
                section.sub_sections
            ):

                total += cls.count(
                    subsection.content
                )

        return total