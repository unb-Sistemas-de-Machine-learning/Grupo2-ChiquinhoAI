from app.interfaces.language_model import LanguageModel
from app.interfaces.vector_store import VectorStore


class RAGService:
    """Orquestra o fluxo RAG (busca vetorial + geração de resposta)."""

    def __init__(self, llm: LanguageModel, vector_store: VectorStore):
        self.llm = llm
        self.vector_store = vector_store

    def generate_answer(self, query: str) -> str:
        docs = self.vector_store.search(query)
        context = "\n\n".join(docs)

        prompt = f"""
        Você é um assistente que responde com base nestes documentos:
        {context}

        Pergunta:
        {query}

        Responda de forma clara e com base apenas nas informações acima.
        """

        return self.llm.generate_response(prompt)
