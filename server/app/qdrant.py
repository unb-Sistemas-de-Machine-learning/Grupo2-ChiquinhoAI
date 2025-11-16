from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    VectorParams,
    Distance,
    PointStruct
)
from app.gemini_llm import GeminiLLM


class QdrantVectorStore:
    def __init__(
        self,
        url: str,
        api_key: str | None = None,
        llm: GeminiLLM = None,
        collection_name: str = "Chiquinho_ai"
    ):
        self.collection_name = collection_name

        if llm is None:
            raise ValueError("É necessário fornecer um GeminiLLM para gerar embeddings.")

        self.llm = llm
        self.embedding_size = 768

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
        return self.llm.embed_text(text)

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

        result = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=top_k
        )
        return [hit.payload["text"] for hit in result]
