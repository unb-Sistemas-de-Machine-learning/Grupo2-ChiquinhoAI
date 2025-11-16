import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.rag import RAGService
from app.dependencies import get_rag_service
from app.ingest import ingest

app = FastAPI(title="ChiquinhoAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/response")
def get_response(pergunta: str, rag: RAGService = Depends(get_rag_service)):
    resposta = rag.generate_answer(pergunta)
    return {"resposta": resposta}


@app.post("/ingest")
async def ingest_docs(docs: list[dict]):
    ingest(docs, recreate=True)
    return {"status": "ok", "count": len(docs)}


if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 5555))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
