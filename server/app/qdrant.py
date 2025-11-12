from typing import List, Optional
from qdrant_client import QdrantClient
from app.interfaces.vector_store import VectorStore


class QdrantVectorStore(VectorStore):
    def __init__(self, url: str, api_key: Optional[str] = None):
        self.url = url
        self.qdrant = QdrantClient(url=self.url, api_key=api_key)

    def search(self, query: str, top_k: int = 3) -> List[str]:
        # TODO: implementar busca no banco de dados vetorial.
        mock_document = (
            "FastAPI é um framework moderno de Python para criar APIs rápidas, "
            "tipadas e assíncronas. Ele é amplamente usado para desenvolvimento web "
            "e microserviços, e permite gerar documentação automática via OpenAPI."
        )
        return [mock_document for _ in range(top_k)]
