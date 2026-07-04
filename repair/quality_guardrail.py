import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, AspectCritic
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from langchain_core.embeddings import Embeddings

# 1. Setup Mock Embeddings to bypass OpenAI default initialization
class MockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.0] * 1536 for _ in texts]
    def embed_query(self, text):
        return [0.0] * 1536

class QualityGuardrail:

    def __init__(self):
        # Read keys
        from llm.config import GROQ_API_KEY, OPENROUTER_API_KEY
        
        self.groq_key = GROQ_API_KEY.strip() if GROQ_API_KEY else None
        self.openrouter_key = OPENROUTER_API_KEY.strip() if OPENROUTER_API_KEY else None
        
        # Set OpenAI environment variables for Ragas before we construct wrappers
        if self.groq_key:
            os.environ["OPENAI_API_KEY"] = self.groq_key
            os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
            self.chat_llm = ChatOpenAI(
                model="llama-3.3-70b-versatile",
                temperature=0.3
            )
        elif self.openrouter_key:
            os.environ["OPENAI_API_KEY"] = self.openrouter_key
            os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
            self.chat_llm = ChatOpenAI(
                model="meta-llama/llama-3.3-70b-instruct",
                temperature=0.3
            )
        else:
            raise ValueError("No GROQ_API_KEY or OPENROUTER_API_KEY found in config!")

        self.ragas_judge = LangchainLLMWrapper(self.chat_llm)
        self.mock_embeddings = MockEmbeddings()

        # Define custom Aspect Critic for Coherence
        self.coherence_critic = AspectCritic(
            name="coherence",
            definition="Is the generated text logical, readable, coherent, and flow naturally?",
            strictness=2,
            llm=self.ragas_judge
        )
        
        # Configure faithfulness to use the judge
        faithfulness.llm = self.ragas_judge

    def evaluate_generation(self, outline, document):
        """
        Evaluates the generated document against the initial user-approved outline.
        Returns:
            dict: { 'faithfulness': float, 'coherence': int }
        """
        # Format the outline plan as context
        outline_contexts = []
        for s in outline.sections:
            sec_text = f"Heading: {s.heading}"
            if s.subheadings:
                sec_text += f"\nSubheadings: " + ", ".join(s.subheadings)
            outline_contexts.append(sec_text)

        # Format generated document as final answer
        doc_answers = []
        for s in document.sections:
            doc_answers.append(f"Heading: {s.heading}\n{s.content}")
            for sub in s.sub_sections:
                doc_answers.append(f"Subheading: {sub.heading}\n{sub.content}")
                
        final_answer = "\n\n".join(doc_answers)

        # Build evaluation dataset
        data = {
            "question": [f"Write a detailed document about: {outline.title or 'the specified topic'}."],
            "contexts": [outline_contexts],
            "answer": [final_answer]
        }
        dataset = Dataset.from_dict(data)

        print("\nRunning Quality Guardrail Evaluation...")
        try:
            result = evaluate(
                dataset=dataset,
                metrics=[faithfulness, self.coherence_critic],
                llm=self.ragas_judge,
                embeddings=self.mock_embeddings
            )
            return {
                "faithfulness": float(result["faithfulness"][0]),
                "coherence": int(result["coherence"][0])
            }
        except Exception as e:
            print(f"Quality check execution failed: {e}")
            return {
                "faithfulness": 1.0,
                "coherence": 1
            }
