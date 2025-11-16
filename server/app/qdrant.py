from typing import List, Optional
from qdrant_client import QdrantClient
from app.interfaces.vector_store import VectorStore
from app.embeddings import embed_text
from app.config import get_settings


COLLECTION_NAME = "documents"


class QdrantVectorStore(VectorStore):
    def __init__(self, url: str, api_key: Optional[str] = None):
        self.url = url
        self.qdrant = QdrantClient(url=self.url, api_key=api_key)

    def _extract_text_from_payload(self, payload: dict) -> str:
        # Prefer content_text, fall back to title or excerpt
        return payload.get("content_text") or payload.get("excerpt") or payload.get("title") or ""

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Perform a vector search in Qdrant and return a list of document texts.

        This method generates an embedding for the query (using the local
        sentence-transformers model) and queries the Qdrant collection.
        """
        settings = get_settings()
        qdrant_api_key = None
        # Generate embedding for the query
        query_vector = embed_text(query)

        try:
            hits = self.qdrant.search(collection_name=COLLECTION_NAME, query_vector=query_vector, limit=top_k)
        except Exception:
            # If search fails (collection missing, client API mismatch), return empty list
            return []

        results: List[str] = []
        for hit in hits:
            payload = getattr(hit, "payload", None) or hit.get("payload", {})
            text = self._extract_text_from_payload(payload)
            results.append(text)

        return results
