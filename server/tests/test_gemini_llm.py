from unittest.mock import patch
from app.services.llm.gemini_llm import GeminiLLM


def test_gemini_llm_generate_response_success():
    with patch("app.services.llm.gemini_llm.genai.GenerativeModel") as MockModel:
        mock_instance = MockModel.return_value
        mock_instance.generate_content.return_value.text = "resposta simulada"

        llm = GeminiLLM(api_key="fake_key")
        resposta = llm.generate_response("Pergunta de teste")

        assert resposta == "resposta simulada"
        mock_instance.generate_content.assert_called_once()


def test_gemini_llm_generate_response_error():
    with patch("app.services.llm.gemini_llm.genai.GenerativeModel") as MockModel:
        mock_instance = MockModel.return_value
        mock_instance.generate_content.side_effect = Exception("API falhou")

        llm = GeminiLLM(api_key="fake_key")
        resposta = llm.generate_response("Pergunta de teste")

        assert resposta == "Desculpe, ocorreu um erro ao processar sua solicitação."
