import pytest
from unittest.mock import MagicMock

from app.rag import RAGService
from app.interfaces.vector_store import VectorStore
from app.interfaces.language_model import LanguageModel


@pytest.fixture
def mock_vector_store() -> VectorStore:
    mock = MagicMock(spec=VectorStore)
    mock.search.return_value = ["doc1", "doc2", "doc3"]
    return mock


@pytest.fixture
def mock_llm() -> LanguageModel:
    mock = MagicMock(spec=LanguageModel)
    mock.generate_response.return_value = "resposta gerada pelo LLM"
    return mock


@pytest.fixture
def rag_service(mock_llm: LanguageModel, mock_vector_store: VectorStore) -> RAGService:
    return RAGService(llm=mock_llm, vector_store=mock_vector_store)
