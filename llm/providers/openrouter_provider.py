# OpenRouter provider placeholder
from openai import OpenAI

from llm.config import OPENROUTER_API_KEY
from llm.providers.base import BaseProvider


class OpenRouterProvider(BaseProvider):

    def __init__(
        self,
        model: str
    ):

        self.model = model

        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

    def generate(
        self,
        prompt: str,
        system_prompt: str
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content