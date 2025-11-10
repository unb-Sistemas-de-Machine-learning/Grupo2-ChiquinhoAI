from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant import Qdrant
from llm import LLM
import uvicorn
import os

class ServerApp:
    def __init__(self, qdrant, llm):
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.__qdrant = qdrant
        self.__llm = llm
        self.routes()

    def routes(self):
        @self.app.get("/response")
        def get_resposta(pergunta: str):
            print(f"Pergunta recebida: {pergunta}")
            dados = self.__qdrant.find_data(pergunta)
            resposta = self.__llm.request(pergunta, dados)
            return {"resposta": resposta}

server = ServerApp(Qdrant(), LLM())
app = server.app

if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 55555))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)