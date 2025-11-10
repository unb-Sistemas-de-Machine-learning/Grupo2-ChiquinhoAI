from fastapi import FastAPI
from qdrant_client import QdrantClient
import os

app = FastAPI()

qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
qdrant = QdrantClient(url=qdrant_url)

@app.get("/")
def root():
    return {"msg": "Servidor Python conectado ao Qdrant!"}

@app.get("/collections")
def get_collections():
    collections = qdrant.get_collections()
    return collections.dict()
