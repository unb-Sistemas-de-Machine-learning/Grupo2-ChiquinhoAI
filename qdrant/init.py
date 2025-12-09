from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(
    url="http://qdrant:6333",
)

collection_name = "ChiquinhoAI"

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=768,
            distance=models.Distance.COSINE
        )
    )
    print(f"Collection '{collection_name}' criada.")
else:
    print(f"Collection '{collection_name}' já existe. Nada a fazer.")
