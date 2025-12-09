import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from app.rag import RAGService
from app.dependencies import get_rag_service
from app.ingest import ingest


app = FastAPI(
    title="ChiquinhoAI API",
    version="1.0.0",
    description="""
**ChiquinhoAI** — API para ingestão e consulta semântica de documentos.

**Endpoints principais**:
- `/response`: Gera uma resposta contextualizada usando RAG (Retriever-Augmented Generation)
- `/ingest`: Insere novos documentos no vetor store (Qdrant)
""",

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
    title: str = Field(..., example="Monitoria")
    url: str = Field(..., example="https://deg.unb.br/monitoria/")
    publication_date: str = Field(..., example="29 de agosto de 2024")
    source: str = Field(..., example="deg.unb.br")
    content_text: str = Field(..., example="Texto completo do artigo...")
    metadata: Dict[str, Any] | None = Field(default=None, example={"excerpt": "Resumo do conteúdo"})


class ResponseOutput(BaseModel):
    resposta: str = Field(..., example="A monitoria é uma atividade acadêmica oferecida pela UnB...")


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
async def ingest_docs(docs: List[Document]):
    ingest([doc.dict() for doc in docs], recreate=True)
    return {"status": "ok", "count": len(docs)}


if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 5555))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
