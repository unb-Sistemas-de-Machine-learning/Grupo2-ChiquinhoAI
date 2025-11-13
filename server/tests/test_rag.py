from app.interfaces.language_model import LanguageModel
from app.interfaces.vector_store import VectorStore
from app.rag import RAGService


def test_generate_answer_calls_vector_store_search(
    rag_service: RAGService, mock_vector_store: VectorStore
):
    pergunta = "O que é FastAPI?"
    rag_service.generate_answer(pergunta)

    mock_vector_store.search.assert_called_once_with(pergunta)


def test_generate_answer_calls_llm_with_correct_prompt(
    rag_service: RAGService, mock_llm: LanguageModel
):
    pergunta = "Explique FastAPI"
    rag_service.generate_answer(pergunta)

    prompt_enviado = mock_llm.generate_response.call_args[0][0]

    assert "Explique FastAPI" in prompt_enviado
    assert "doc1" in prompt_enviado
    assert "doc2" in prompt_enviado
    assert "doc3" in prompt_enviado


def test_generate_answer_returns_llm_response(rag_service: RAGService):
    pergunta = "Qual é o objetivo do FastAPI?"
    resposta = rag_service.generate_answer(pergunta)

    assert resposta == "resposta gerada pelo LLM"
