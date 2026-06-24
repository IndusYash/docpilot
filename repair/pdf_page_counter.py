import fitz


class PDFPageCounter:

    @staticmethod
    def count(
        pdf_path
    ):

        pdf = fitz.open(
            pdf_path
        )

        pages = (
            len(pdf)
        )

        print(
            f"\nPDF Page Count: {pages}"
        )

        return pages