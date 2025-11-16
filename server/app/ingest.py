import os
import json
import logging
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import get_settings
from app.gemini_llm import GeminiLLM
from app.dependencies import get_llm

logger = logging.getLogger(__name__)

COLLECTION_NAME = "ChiquinhoAI"

llm = get_llm()

def _load_source_files(source_paths: List[str]) -> List[dict]:
    items = []
    for path in source_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        items.extend(data)
            except Exception:
                logger.exception(f"Falha ao ler arquivo JSON: {path}")
        else:
            logger.warning(f"Arquivo não encontrado: {path}")
    return items

def build_records_from_docs(docs: List[dict]) -> List[dict]:
    records = []
    for d in docs:
        text = (
            (d.get("title") or "") + "\n\n" + (d.get("content_text") or "")
        ).strip()
        payload = {
            "title": d.get("title"),
            "url": d.get("url"),
            "publication_date": d.get("publication_date"),
            "source": d.get("source"),
            "excerpt": d.get("metadata", {}).get("excerpt"),
            "content_text": d.get("content_text"),
        }

        records.append({"text": text, "payload": payload})
    return records

def ingest(
    docs: List[dict],
    batch_size: int = 64,
    recreate: bool = False,
):
    settings = get_settings()
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    client = QdrantClient(url=settings.qdrant_url, api_key=qdrant_api_key)
    records = build_records_from_docs(docs)
    if not records:
        logger.warning("Nenhum documento para ingerir.")
        return

    logger.info(f"Gerando embeddings com Gemini para {len(records)} documentos...")
    vectors = []
    for rec in records:
        vec = llm.embed_text(rec["text"])
        if not vec:
            logger.error("Falha ao gerar embedding, pulando documento.")
            continue
        vectors.append(vec)
    if not vectors:
        logger.error("Nenhum embedding foi gerado. Abortando.")
        return

    vector_size = len(vectors[0])
    collections = client.get_collections().collections
    collection_exists = any(c.name == COLLECTION_NAME for c in collections)

    if recreate or not collection_exists:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        logger.info(f"Coleção '{COLLECTION_NAME}' criada/recriada com dimensão={vector_size}")
        next_id = 1
    else:
        info = client.get_collection(COLLECTION_NAME)
        next_id = info.points_count + 1
        logger.info(
            f"Coleção '{COLLECTION_NAME}' existente com {info.points_count} pontos. "
            f"Novos IDs iniciam em {next_id}."
        )

    points = []
    for i, (rec, vec) in enumerate(zip(records, vectors)):
        point = {
            "id": next_id + i,
            "vector": vec,
            "payload": rec["payload"]
        }
        points.append(point)
        if len(points) >= batch_size:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info(f"Batch upsert ({len(points)}) OK")
            points = []
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info(f"Batch final ({len(points)}) OK")
    logger.info(f"Total de {len(vectors)} documentos adicionados ao Qdrant.")


def main():
    logging.basicConfig(level=logging.INFO)
    base = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "webscraper"))
    possible_files = [
        os.path.join(base, "deg.json"),
        os.path.join(base, "unb_data.json"),
    ]
    docs = _load_source_files(possible_files)
    if not docs:
        logger.error("Nenhum documento encontrado. Abortando.")
        return
    ingest(docs, recreate=True)


if __name__ == "__main__":
    main()
