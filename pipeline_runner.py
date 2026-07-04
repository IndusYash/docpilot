import os
import re
import sys
import io
from datetime import datetime
from chat import ChatState
from generators.outline_generator import OutlineGenerator
from generators.document_generator import DocumentGenerator
from planners.content_planner import ContentPlanner
from builder import DocxBuilder
from repair import (
    PDFConverter,
    PDFPageCounter,
    OverflowWordCounter,
    TargetedCompressor,
    LastPageQualityLoop
)
from repair.quality_guardrail import QualityGuardrail

class WebLogger(io.StringIO):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def write(self, s):
        super().write(s)
        val = s.strip()
        if val:
            self.callback("log", {"message": val})

class PipelineRunner:
    def __init__(self, title, pages):
        self.state = ChatState()
        self.state.title = title
        self.state.pages = pages
        self.outline_generator = OutlineGenerator()
        self.current_outline = None
        self.output_file = None

    def generate_outline(self):
        self.current_outline = self.outline_generator.generate(self.state)
        return self._outline_to_dict(self.current_outline)

    def add_feedback(self, feedback):
        self.state.add_feedback(feedback)
        self.current_outline = self.outline_generator.generate(self.state)
        return self._outline_to_dict(self.current_outline)

    def _outline_to_dict(self, outline):
        return {
            "title": outline.title,
            "sections": [
                {
                    "heading": s.heading,
                    "subheadings": s.subheadings
                } for s in outline.sections
            ]
        }

    def generate_document(self, progress_callback):
        # Redirect stdout to capture all inner print statements in real-time
        old_stdout = sys.stdout
        sys.stdout = WebLogger(progress_callback)
        
        try:
            print("\nOutline Approved. Starting generation...")
            print("Generating Content Plan...")
            planner = ContentPlanner()
            content_plan = planner.generate(self.current_outline, self.state.pages)
            print("Content plan ready.")

            MAX_REPAIR_PASSES = 5
            MAX_QUALITY_RETRIES = 3
            guardrail = QualityGuardrail()
            quality_feedback = None
            document_accepted = False
            scores = None
            document = None

            for quality_attempt in range(MAX_QUALITY_RETRIES):
                if quality_attempt > 0:
                    print(f"\n[Quality Retry {quality_attempt + 1}/{MAX_QUALITY_RETRIES}] Regenerating with feedback...")

                document_generator = DocumentGenerator()
                document = document_generator.generate(
                    self.current_outline,
                    content_plan,
                    quality_feedback=quality_feedback
                )

                builder = DocxBuilder()
                safe_title = re.sub(r"[^a-zA-Z0-9]+", "_", self.state.title.strip())
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"output/{safe_title}_{timestamp}.docx"
                output_file = builder.build(document, output_path)
                self.output_file = output_file

                compressor = TargetedCompressor()
                for iteration in range(MAX_REPAIR_PASSES):
                    pdf_path = PDFConverter.convert(output_file)
                    actual_pages = PDFPageCounter.count(pdf_path)
                    overflow_words = OverflowWordCounter.count(pdf_path, self.state.pages)

                    print(f"\n===== REPAIR PASS {iteration + 1} =====")
                    print(f"PDF Pages: {actual_pages}")
                    print(f"Overflow Words: {overflow_words}")

                    if actual_pages <= self.state.pages:
                        print("Target page count achieved.")
                        break

                    print(f"Compressing by ~{overflow_words} words...")
                    document = compressor.compress(document, overflow_words)
                    output_file = builder.build(document, output_path)
                    self.output_file = output_file

                quality_loop = LastPageQualityLoop()
                document = quality_loop.repair(
                    document=document,
                    target_pages=self.state.pages,
                    builder=builder,
                    output_path=output_path
                )
                output_file = builder.build(document, output_path)
                self.output_file = output_file

                scores = guardrail.evaluate_generation(self.current_outline, document)
                print("\n===== QUALITY GUARDRAIL RESULTS =====")
                print(f"Faithfulness Score: {scores['faithfulness']:.2f}")
                print(f"Coherence Score:    {scores['coherence']}")

                if scores['faithfulness'] >= 0.85:
                    document_accepted = True
                    break

                quality_feedback = (
                    f"Previous attempt FAILED the quality check (Faithfulness: {scores['faithfulness']:.2f}/1.00). "
                    f"The content was too generic and not grounded in the exact outline topics. "
                    f"You MUST strictly write about the exact headings and subheadings provided. "
                    f"Do NOT use placeholder phrases. Instead, write specific, detailed content about each heading."
                )

                if quality_attempt < MAX_QUALITY_RETRIES - 1:
                    if os.path.exists(output_file):
                        try:
                            os.remove(output_file)
                        except Exception:
                            pass
                    pdf_file = output_file.replace(".docx", ".pdf")
                    if os.path.exists(pdf_file):
                        try:
                            os.remove(pdf_file)
                        except Exception:
                            pass

            preview_data = []
            if document:
                for s in document.sections:
                    preview_data.append({"heading": s.heading, "content": s.content, "type": "section"})
                    for sub in s.sub_sections:
                        preview_data.append({"heading": sub.heading, "content": sub.content, "type": "subsection"})

            return {
                "accepted": document_accepted,
                "scores": scores,
                "preview": preview_data,
                "filename": os.path.basename(self.output_file) if self.output_file else None
            }

        finally:
            sys.stdout = old_stdout
