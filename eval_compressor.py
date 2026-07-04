import os
from dotenv import load_dotenv

# Load environment first
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY").strip() if os.getenv("OPENROUTER_API_KEY") else None
GROQ_API_KEY = os.getenv("GROQ_API_KEY").strip() if os.getenv("GROQ_API_KEY") else None

# Set OpenAI environment variables for Ragas before it imports
if GROQ_API_KEY:
    os.environ["OPENAI_API_KEY"] = GROQ_API_KEY
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
elif OPENROUTER_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
else:
    raise ValueError("No GROQ_API_KEY or OPENROUTER_API_KEY found in .env!")

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, AspectCritic
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from langchain_core.embeddings import Embeddings

from repair.targeted_compressor import TargetedCompressor
from schemas.document import Document, DocumentSection

# 1. Setup Mock Embeddings to bypass OpenAI default initialization
class MockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.0] * 1536 for _ in texts]
    def embed_query(self, text):
        return [0.0] * 1536

# 2. Setup the LLM Judge wrapper
def get_judge_llm():
    if GROQ_API_KEY:
        print("Using Groq (llama-3.3-70b-versatile) as the evaluation judge.")
        return ChatOpenAI(
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
    elif OPENROUTER_API_KEY:
        print("Using OpenRouter (llama-3.3-70b-instruct) as the evaluation judge.")
        return ChatOpenAI(
            model="meta-llama/llama-3.3-70b-instruct",
            temperature=0.3
        )
    else:
        raise ValueError("No GROQ_API_KEY or OPENROUTER_API_KEY found in .env!")

def main():
    chat_llm = get_judge_llm()
    ragas_judge = LangchainLLMWrapper(chat_llm)
    mock_embeddings = MockEmbeddings()

    # Define custom Aspect Critic for Coherence
    coherence_critic = AspectCritic(
        name="coherence",
        definition="Is the generated text logical, readable, coherent, and flow naturally?",
        strictness=3,
        llm=ragas_judge
    )
    
    # Configure faithfulness to use the custom LLM judge
    faithfulness.llm = ragas_judge

    # Define a sample text that needs compression
    original_content = (
        "Artificial Intelligence has rapidly evolved over the past decade. "
        "Deep learning frameworks have enabled computer vision models to surpass human-level accuracy. "
        "Natural language processing has also seen immense progress with the advent of Transformers, "
        "allowing machines to comprehend and generate human-like text at scale."
    )

    doc = Document(
        title="AI Evaluation Study",
        sections=[
            DocumentSection(
                heading="1. Executive Summary",
                content=original_content,
                sub_sections=[]
            )
        ]
    )

    # Let's compress the document by ~25 words
    print("Compressing test document...")
    compressor = TargetedCompressor()
    compressed_doc = compressor.compress(doc, words_to_remove=25)
    compressed_content = compressed_doc.sections[0].content
    print(f"\nOriginal text: {original_content}")
    print(f"Compressed text: {compressed_content}\n")

    # Build evaluation dataset
    data = {
        "question": ["Compress the document to remove 25 words while preserving factual truth."],
        "contexts": [[original_content]],
        "answer": [compressed_content]
    }
    dataset = Dataset.from_dict(data)

    # Run Ragas evaluation
    print("Running Ragas evaluation...")
    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, coherence_critic],
        llm=ragas_judge,
        embeddings=mock_embeddings
    )

    print("\n===== RAGAS EVALUATION RESULTS =====")
    print(f"Faithfulness Score: {result['faithfulness']}")
    print(f"Coherence Score:    {result['coherence']}")

if __name__ == "__main__":
    main()
