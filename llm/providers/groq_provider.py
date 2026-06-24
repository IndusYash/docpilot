# Groq provider placeholder
from groq import Groq

from llm.config import GROQ_API_KEY
from llm.providers.base import BaseProvider


class GroqProvider(BaseProvider):

    def __init__(self):
        self.client = Groq(
            api_key=GROQ_API_KEY
        )

        self.model = "llama-3.3-70b-versatile"

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