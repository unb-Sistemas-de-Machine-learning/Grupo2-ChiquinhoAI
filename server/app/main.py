import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any

from app.services.rag import RAGService
from app.dependencies import get_embedder, get_rag_service
from app.ingest import ingest
from app.config import get_settings
from app.services.embedder.base import Embedder

settings = get_settings()

app = FastAPI(
    title="ChiquinhoAI API",
    version="1.0.0",
    description="""
**ChiquinhoAI** — API para ingestão e consulta semântica de documentos.

**Endpoints principais**:
- `/response`: Gera uma resposta contextualizada usando RAG (Retriever-Augmented Generation)
- `/ingest`: Insere novos documentos no vetor store (Qdrant)
""",
    debug=settings.debug
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Document(BaseModel):
    """Modelo de documento a ser inserido no Qdrant"""
    title: str
    url: str
    publication_date: str | None = None
    source: str
    content_text: str
    metadata: Dict[str, Any] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Monitoria",
                "url": "https://deg.unb.br/monitoria/",
                "publication_date": "29 de agosto de 2024",
                "source": "deg.unb.br",
                "content_text": "Texto completo do artigo...",
                "metadata": {"excerpt": "Resumo do conteúdo"}
            }
        }
    )


class ResponseOutput(BaseModel):
    resposta: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "resposta": "A monitoria é uma atividade acadêmica oferecida pela UnB..."
            }
        }
    )


@app.get(
    "/response",
    response_model=ResponseOutput,
    summary="Gerar resposta contextualizada",
    description="Recebe uma pergunta em linguagem natural e retorna uma resposta baseada nos documentos indexados.",
)
def get_response(pergunta: str, rag: RAGService = Depends(get_rag_service)):
    resposta = rag.generate_answer(pergunta)
    return {"resposta": resposta}


@app.post(
    "/ingest",
    summary="Inserir documentos no Qdrant",
    description="Realiza a ingestão de uma lista de documentos no vetor store (Qdrant), gerando embeddings e salvando os metadados.",
)
async def ingest_docs(
    docs: List[Document],
    embedder: Embedder = Depends(get_embedder)  # injeta o embedder
):
    ingest([doc.model_dump() for doc in docs], embedder=embedder, recreate=True)
    return {"status": "ok", "count": len(docs)}


if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 5555))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
