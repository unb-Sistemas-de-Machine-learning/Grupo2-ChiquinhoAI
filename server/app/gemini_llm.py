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
            logger.error(f"Erro ao chamar a API Gemini: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."

    def embed_text(self, text: str) -> list[float]:
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text
            )

            emb = (
                result.get("embedding", {}).get("values")
                if isinstance(result.get("embedding"), dict)
                else result.get("embedding")
            )

            if not emb:
                raise ValueError("Embedding vazio ou inválido")

            logger.info(f"Embedding gerado (5 valores): {emb[:5]} ...")
            return emb

        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return []

