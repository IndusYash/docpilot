# Base provider placeholder
from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str
    ) -> str:
        pass