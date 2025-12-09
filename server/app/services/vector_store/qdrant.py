from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from app.services.vector_store.base import VectorStore
from app.services.embedder.base import Embedder

class QdrantVectorStore(VectorStore):
    def __init__(
        self,
        url: str,
        embedder: Embedder,
        api_key: str | None = None,
        collection_name: str = "ChiquinhoAI",
        embedding_size: int = 768,
    ):
        self.collection_name = collection_name
        self.embedding_size = embedding_size
        self.embedder = embedder

        self.qdrant = QdrantClient(
            url=url,
            api_key=api_key or None,
            check_compatibility=False
        )

        if not self.qdrant.collection_exists(self.collection_name):
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_size,
                    distance=Distance.COSINE
                ),
            )

    def embed(self, text: str) -> List[float]:
        return self.embedder.embed_text(text)

    def add_document(self, doc_id: str, text: str):
        vector = self.embed(text)

        point = PointStruct(
            id=doc_id,
            vector=vector,
            payload={"text": text},
        )

        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def search(self, query: str, top_k: int = 4):
        vector = self.embed(query)

        result = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k
        )

        return [hit.payload.get("text", "") for hit in result.points]
