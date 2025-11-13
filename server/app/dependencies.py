import os
from functools import lru_cache
from fastapi import Depends
from app.gemini_llm import GeminiLLM
from app.qdrant import QdrantVectorStore
from app.rag import RAGService


@lru_cache
def get_llm() -> GeminiLLM:
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set in environment")

    return GeminiLLM(api_key=api_key)


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore(url=os.getenv("QDRANT_URL", "http://localhost:6333"))


def get_rag_service(
    llm: GeminiLLM = Depends(get_llm),
    vector_store: QdrantVectorStore = Depends(get_vector_store),
) -> RAGService:
    return RAGService(llm=llm, vector_store=vector_store)
