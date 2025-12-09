import google.generativeai as genai
import logging
from app.services.llm.base import LLM

logger = logging.getLogger(__name__)


class GeminiLLM(LLM):
    def __init__(self, api_key: str, model_name: str = "gemini-flash-latest"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Serviço LLM inicializado com o modelo: {model_name}")

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Erro ao chamar a API Gemini: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."
