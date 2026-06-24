# Router placeholder for LLM providers
from llm.providers.groq_provider import GroqProvider
from llm.providers.openrouter_provider import OpenRouterProvider


class LLMRouter:

    def __init__(self):

        self.providers = [

            GroqProvider(),

            OpenRouterProvider(
                "qwen/qwen3-32b"
            ),

            OpenRouterProvider(
                "google/gemma-3-27b-it"
            ),

            OpenRouterProvider(
                "meta-llama/llama-3.3-70b-instruct"
            )
        ]

    def generate(
        self,
        prompt: str,
        system_prompt: str
    ):

        last_error = None

        for provider in self.providers:

            try:

                return provider.generate(
                    prompt,
                    system_prompt
                )

            except Exception as e:

                print(
                    f"Provider failed: {e}"
                )

                last_error = e

        raise last_error