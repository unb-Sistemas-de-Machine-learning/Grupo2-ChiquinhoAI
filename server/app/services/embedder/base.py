from abc import ABC, abstractmethod
from typing import List

class Embedder(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass
