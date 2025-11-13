from functools import lru_cache
from fastapi import Depends
from app.config import get_settings
from app.gemini_llm import GeminiLLM
from app.qdrant import QdrantVectorStore
from app.rag import RAGService
from app.interfaces.language_model import LanguageModel
from app.interfaces.vector_store import VectorStore


@lru_cache
def get_llm() -> LanguageModel:
    settings = get_settings()
    return GeminiLLM(
        api_key=settings.google_api_key, model_name=settings.gemini_model_name
    )


@lru_cache
def get_vector_store() -> VectorStore:
    settings = get_settings()
    return QdrantVectorStore(url=settings.qdrant_url)


def get_rag_service(
    llm: LanguageModel = Depends(get_llm),
    vector_store: VectorStore = Depends(get_vector_store),
) -> RAGService:
    return RAGService(llm=llm, vector_store=vector_store)
