from abc import ABC, abstractmethod


class LanguageModel(ABC):
    """Classe base abstrata para qualquer modelo de linguagem (LLM)."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass
