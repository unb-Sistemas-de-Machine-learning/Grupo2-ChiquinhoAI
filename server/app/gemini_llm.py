import google.generativeai as genai
import logging
from app.interfaces.language_model import LanguageModel

logger = logging.getLogger(__name__)


class GeminiLLM(LanguageModel):
    def __init__(self, api_key: str, model_name: str = "gemini-flash-latest"):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Serviço LLM inicializado com o modelo: {model_name}")
        except Exception as e:
            logger.error(f"Falha ao inicializar o modelo Gemini: {e}")
            raise

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Erro ao chamar a API Gemini: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."
