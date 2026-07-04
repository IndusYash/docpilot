import fitz


class OverflowWordCounter:

    @staticmethod
    def count(
        pdf_path,
        target_pages
    ):

        overflow = 0

        with fitz.open(
            pdf_path
        ) as pdf:
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