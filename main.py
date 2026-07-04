from generators.outline_generator import (
    OutlineGenerator
)

from generators.document_generator import (
    DocumentGenerator
)

from planners.content_planner import (
    ContentPlanner
)

from builder import (
    DocxBuilder
)

from chat import (
    ChatState
)

from repair import (
    PDFConverter,
    PDFPageCounter,
    OverflowWordCounter,
    TargetedCompressor
)
from repair import (
    LastPageQualityLoop
)
import re
from datetime import datetime

MAX_REPAIR_PASSES = 5


def display_outline(
    outline
):

    print(
        "\nGenerated Outline:\n"
    )

    for idx, section in enumerate(
        outline.sections,
        start=1
    ):

        print(
            f"{idx}. {section.heading}"
        )

        for sub in section.subheadings:

            print(
                f"    - {sub}"
            )


def main():

    state = ChatState()

    outline_generator = (
        OutlineGenerator()
    )

    state.title = input(
        "Topic: "
    )

    state.pages = int(
        input(
            "Pages: "
        )
    )

    state.current_outline = (
        outline_generator.generate(
            state
        )
    )

    display_outline(
        state.current_outline
    )

    while True:

        print(
            "\nCommands:"
        )

        print(
            "approve"
        )

        print(
            "feedback <text>"
        )

        print(
            "show"
        )

        print(
            "history"
        )

        command = input(
            "\n> "
        ).strip()

        # ======================
        # APPROVE OUTLINE
        # ======================

        if command.lower() == "approve":

            print(
                "\nOutline Approved."
            )

            print(
                "\nGenerating document...\n"
            )

            # ======================
            # CONTENT PLAN
            # ======================

            planner = (
                ContentPlanner()
            )

            content_plan = (
                planner.generate(
                    state.current_outline,
                    state.pages
                )
            )

            print(
                "\n===== CONTENT PLAN =====\n"
            )

            print(
                content_plan.model_dump_json(
                    indent=4
                )
            )

            # ======================
            # QUALITY RETRY LOOP
            # ======================
            from repair.quality_guardrail import QualityGuardrail
            import os

            MAX_QUALITY_RETRIES = 3
            guardrail = QualityGuardrail()
            quality_feedback = None
            document_accepted = False

            for quality_attempt in range(MAX_QUALITY_RETRIES):

                if quality_attempt > 0:
                    print(
                        f"\n[Quality Retry {quality_attempt + 1}/{MAX_QUALITY_RETRIES}] "
                        f"Regenerating with quality feedback injected..."
                    )

                # --- DOCUMENT GENERATION ---
                document_generator = (
                    DocumentGenerator()
                )

                document = (
                    document_generator.generate(
                        state.current_outline,
                        content_plan,
                        quality_feedback=quality_feedback
                    )
                )

                print(
                    "\n===== GENERATED DOCUMENT =====\n"
                )

                print(
                    document.model_dump_json(
                        indent=4
                    )
                )

                # --- DOCX BUILD ---
                builder = (
                    DocxBuilder()
                )

                safe_title = re.sub(
                    r"[^a-zA-Z0-9]+",
                    "_",
                    state.title.strip()
                )

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                output_path = (
                    f"output/"
                    f"{safe_title}_"
                    f"{timestamp}.docx"
                )

                output_file = (
                    builder.build(
                        document,
                        output_path
                    )
                )

                compressor = (
                    TargetedCompressor()
                )

                for iteration in range(
                    MAX_REPAIR_PASSES
                ):

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

                    overflow_words = (
                        OverflowWordCounter.count(
                            pdf_path,
                            state.pages
                        )
                    )

                    print(
                        f"\n===== REPAIR PASS {iteration + 1} ====="
                    )

                    print(
                        f"PDF Pages: {actual_pages}"
                    )

                    print(
                        f"Overflow Words: {overflow_words}"
                    )

                    if (
                        actual_pages <= state.pages
                    ):

                        print(
                            "\nTarget reached."
                        )

                        break

                    words_to_remove = (
                        overflow_words
                    )

                    print(
                        f"\nCompressing by ~{words_to_remove} words"
                    )

                    document = (
                        compressor.compress(
                            document,
                            words_to_remove
                        )
                    )

                    output_file = (
                        builder.build(
                            document,
                            output_path
                        )
                    )

                quality_loop = (
                    LastPageQualityLoop()
                )

                document = (
                    quality_loop.repair(
                        document=document,
                        target_pages=state.pages,
                        builder=builder,
                        output_path=output_path
                    )
                )

                output_file = (
                    builder.build(
                        document,
                        output_path
                    )
                )

                # --- QUALITY GUARDRAIL CHECK ---
                scores = guardrail.evaluate_generation(
                    state.current_outline, document
                )

                print("\n===== QUALITY GUARDRAIL RESULTS =====")
                print(f"Faithfulness Score: {scores['faithfulness']:.2f} (Threshold: >= 0.85)")
                print(f"Coherence Score:    {scores['coherence']} (Pass: 1, Fail: 0)")

                if scores['faithfulness'] >= 0.85:
                    document_accepted = True
                    break

                # Build targeted feedback for the next retry
                quality_feedback = (
                    f"Previous attempt FAILED the quality check "
                    f"(Faithfulness: {scores['faithfulness']:.2f}/1.00). "
                    f"The content was too generic and not grounded in the exact outline topics. "
                    f"You MUST strictly write about the exact headings and subheadings provided. "
                    f"Do NOT use placeholder phrases like 'this section provides an overview' or "
                    f"'the topic holds significant relevance'. Instead, write specific, factual, "
                    f"detailed content directly about each heading's subject matter."
                )

                print(
                    f"\n[WARNING] Quality check failed "
                    f"(attempt {quality_attempt + 1}/{MAX_QUALITY_RETRIES}). "
                    f"Auto-retrying with feedback..."
                )

                # Clean up the failed file before retrying
                if os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                    except Exception:
                        pass

            # --- FINAL DECISION ---
            if not document_accepted:
                print(
                    f"\n[WARNING] Document failed quality checks after "
                    f"{MAX_QUALITY_RETRIES} attempts."
                )
                print(f"Final Faithfulness Score: {scores['faithfulness']:.2f}")
                choice = input(
                    "Do you want to accept or reject this document? [accept/reject]: "
                ).strip().lower()
                if choice == "reject":
                    print("\nDocument rejected. Cleaning up generated file...")
                    if os.path.exists(output_file):
                        try:
                            os.remove(output_file)
                        except Exception as e:
                            print(f"Failed to delete document: {e}")
                    break

            print(
                f"\nDocument saved to:\n"
                f"{output_file}"
            )

            break

        # ======================
        # SHOW CURRENT OUTLINE
        # ======================

        elif command.lower() == "show":

            display_outline(
                state.current_outline
            )

        # ======================
        # FEEDBACK HISTORY
        # ======================

        elif command.lower() == "history":

            print(
                "\nFeedback History:\n"
            )

            if not (
                state.feedback_history
            ):

                print(
                    "No feedback yet."
                )

            else:

                for item in (
                    state.feedback_history
                ):

                    print(
                        f"- {item}"
                    )

        # ======================
        # FEEDBACK LOOP
        # ======================

        elif command.startswith(
            "feedback "
        ):

            feedback = command[
                len(
                    "feedback "
                ):
            ].strip()

            state.add_feedback(
                feedback
            )

            state.current_outline = (
                outline_generator.generate(
                    state
                )
            )

            display_outline(
                state.current_outline
            )

        # ======================
        # INVALID COMMAND
        # ======================

        else:

            print(
                "\nUnknown command."
            )


if __name__ == "__main__":

    main()