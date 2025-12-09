import pytest
from unittest.mock import MagicMock

from app.services.rag import RAGService
from app.services.vector_store.base import VectorStore
from app.services.llm.base import LLM


@pytest.fixture
def mock_vector_store() -> VectorStore:
    mock = MagicMock(spec=VectorStore)
    mock.search.return_value = ["doc1", "doc2", "doc3"]
    return mock


@pytest.fixture
def mock_llm() -> LLM:
    mock = MagicMock(spec=LLM)
    mock.generate_response.return_value = "resposta gerada pelo LLM"
    return mock


@pytest.fixture
def rag_service(mock_llm: LLM, mock_vector_store: VectorStore) -> RAGService:
    return RAGService(llm=mock_llm, vector_store=mock_vector_store)
