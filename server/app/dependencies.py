from functools import lru_cache
from fastapi import Depends
from app.config import get_settings
from app.services.llm.gemini_llm import GeminiLLM
from app.services.embedder.gemini_embedder import GeminiEmbedder
from app.services.vector_store.qdrant import QdrantVectorStore
from app.services.rag import RAGService
from app.services.llm.base import LLM
from app.services.vector_store.base import VectorStore
from app.services.embedder.base import Embedder


@lru_cache
def get_llm() -> LLM:
    settings = get_settings()
    return GeminiLLM(
        api_key=settings.google_api_key,
        model_name=settings.gemini_model_name
    )

@lru_cache
def get_embedder() -> Embedder:
    settings = get_settings()
    return GeminiEmbedder(
        api_key=settings.google_api_key,
        model_name="models/text-embedding-004"
    )

@lru_cache
def get_vector_store(
    embedder: Embedder = Depends(get_embedder),
) -> VectorStore:
    settings = get_settings()
    return QdrantVectorStore(
        url=settings.qdrant_url,
        api_key=settings.qdrant_key,
        embedder=embedder,
        collection_name="ChiquinhoAI"
    )

def get_rag_service(
    llm: LLM = Depends(get_llm),
    vector_store: VectorStore = Depends(get_vector_store),
) -> RAGService:
    return RAGService(llm=llm, vector_store=vector_store)