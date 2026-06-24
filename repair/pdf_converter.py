from pathlib import Path
import subprocess


class PDFConverter:

    LIBREOFFICE_PATH = (
        r"C:\Program Files\LibreOffice\program\soffice.exe"
    )

    @classmethod
    def convert(
        cls,
        docx_path: str
    ):

        docx_path = Path(
            docx_path
        ).resolve()

        output_dir = (
            docx_path.parent
        )

        subprocess.run(
            [
                cls.LIBREOFFICE_PATH,
                "--headless",
                "--convert-to",
                "pdf",
                str(docx_path),
                "--outdir",
                str(output_dir)
            ],
            check=True
        )

        return str(
            docx_path.with_suffix(
                ".pdf"
            )
        )