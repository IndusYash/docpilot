import fitz


class PDFPageCounter:

    @staticmethod
    def count(
        pdf_path
    ):

        with fitz.open(
            pdf_path
        ) as pdf:
            pages = (
                len(pdf)
            )

        print(
            f"\nPDF Page Count: {pages}"
        )

        return pages