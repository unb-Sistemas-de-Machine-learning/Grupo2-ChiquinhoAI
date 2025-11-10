from qdrant_client import QdrantClient
import os

class Qdrant:
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant = QdrantClient(url=self.qdrant_url)

    def find_data(self, data):
        return f"Dado mockado: {data}"