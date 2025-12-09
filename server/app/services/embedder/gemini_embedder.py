import google.generativeai as genai
import logging
from app.services.embedder.base import Embedder

logger = logging.getLogger(__name__)

class GeminiEmbedder(Embedder):
    def __init__(self, api_key: str, model_name: str = "models/text-embedding-004"):
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        try:
            result = genai.embed_content(
                model=self.model_name,
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
