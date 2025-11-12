import os
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import get_rag_service
from app.rag import RAGService

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


if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 5555))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
