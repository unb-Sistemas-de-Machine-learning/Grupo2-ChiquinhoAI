from qdrant_client import QdrantClient

client = QdrantClient(url="http://qdrant:6333")

collection_name = "ChiquinhoAI"

client.recreate_collection(
    collection_name=collection_name,
    vectors_config={"size": 768, "distance": "Cosine"},
)

print(f"Collection '{collection_name}' up.")
