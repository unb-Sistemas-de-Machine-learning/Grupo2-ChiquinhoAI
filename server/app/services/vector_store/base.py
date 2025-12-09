from abc import ABC, abstractmethod
from typing import List


class VectorStore(ABC):
    """Classe abstrata para qualquer banco vetorial."""

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> List[str]:
        pass