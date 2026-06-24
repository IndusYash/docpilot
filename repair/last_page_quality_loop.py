from repair import (
    PDFConverter,
    PDFPageCounter,
    OverflowWordCounter,
    TargetedCompressor,
    TargetedExpander
)


class LastPageQualityLoop:

    MIN_LAST_PAGE_WORDS = 260

    MAX_FIX_PASSES = 3

    def repair(
        self,
        document,
        target_pages,
        builder,
        output_path
    ):

        expander = (
            TargetedExpander()
        )

        compressor = (
            TargetedCompressor()
        )

        for i in range(
            self.MAX_FIX_PASSES
        ):

            output_file = (
                builder.build(
                    document,
                    output_path
                )
            )

            pdf_path = (
                PDFConverter.convert(
                    output_file
                )
            )

            actual_pages = (
                PDFPageCounter.count(
                    pdf_path
                )
            )

            if (
                actual_pages
                != target_pages
            ):
                return document

            last_page_words = (
                OverflowWordCounter.count(
                    pdf_path,
                    target_pages - 1
                )
            )

            print(
                f"\n===== LAST PAGE CHECK {i+1} ====="
            )

            print(
                f"Last Page Words: "
                f"{last_page_words}"
            )

            if (
                last_page_words
                >=
                self.MIN_LAST_PAGE_WORDS
            ):

                print(
                    "Last page healthy."
                )

                return document

            deficit = (
                self.MIN_LAST_PAGE_WORDS
                -
                last_page_words
            )

            print(
                f"Need +{deficit} words"
            )

            document = (
                expander.expand(
                    document,
                    deficit
                )
            )

            output_file = (
                builder.build(
                    document,
                    output_path
                )
            )

            pdf_path = (
                PDFConverter.convert(
                    output_file
                )
            )

            pages_after = (
                PDFPageCounter.count(
                    pdf_path
                )
            )

            if (
                pages_after
                >
                target_pages
            ):

                overflow_words = (
                    OverflowWordCounter.count(
                        pdf_path,
                        target_pages
                    )
                )

                document = (
                    compressor.compress(
                        document,
                        overflow_words + 15
                    )
                )

        return document