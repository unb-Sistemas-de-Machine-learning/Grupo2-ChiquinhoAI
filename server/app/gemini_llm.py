import google.generativeai as genai
import logging
from app.interfaces.language_model import LanguageModel

logger = logging.getLogger(__name__)


class GeminiLLM(LanguageModel):
    def __init__(self, api_key: str, model_name: str = "gemini-flash-latest"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Serviço LLM inicializado com o modelo: {model_name}")

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Erro ao chamar a API Gemini: {e}", exc_info=True)
            return f"Erro ao processar: {str(e)[:200]}"
