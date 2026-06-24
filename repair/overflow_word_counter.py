import fitz


class OverflowWordCounter:

    @staticmethod
    def count(
        pdf_path,
        target_pages
    ):

        pdf = fitz.open(
            pdf_path
        )

        overflow = 0

        for page_index in range(
            target_pages,
            len(pdf)
        ):

            page = pdf[
                page_index
            ]

            text = (
                page.get_text()
            )

            words = len(
                text.split()
            )

            print(
                f"Overflow Page "
                f"{page_index + 1}: "
                f"{words} words"
            )

            overflow += words

        return overflow