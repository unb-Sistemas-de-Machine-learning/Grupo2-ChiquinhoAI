import os
import json
import logging
import uuid
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import get_settings
from app.services.embedder.base import Embedder
from app.dependencies import get_embedder

logger = logging.getLogger(__name__)

COLLECTION_NAME = "ChiquinhoAI"
MAX_CHARS = 3500


def split_text(text: str, max_chars: int = MAX_CHARS) -> List[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end

    return chunks


def build_records_from_docs(docs: List[dict]) -> List[dict]:
    records = []

    for d in docs:
        full_text = f"{d.get('title','')}\n\n{d.get('content_text','')}".strip()
        chunks = split_text(full_text, MAX_CHARS)

        for idx, chunk in enumerate(chunks):
            payload = {
                "title": d.get("title"),
                "url": d.get("url"),
                "publication_date": d.get("publication_date"),
                "source": d.get("source"),
                "excerpt": d.get("metadata", {}).get("excerpt"),
                "content_text": chunk,
                "chunk": idx,
                "total_chunks": len(chunks)
            }

            records.append({
                "text": chunk,
                "payload": payload
            })

    return records


def make_point_id(url: str, chunk_idx: int) -> str:
    """Gera um UUID5 determinístico baseado na URL e no número do chunk."""
    raw = f"{url}-{chunk_idx}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))


def ingest(
    docs: List[dict],
    embedder: Embedder,
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

    logger.info(f"Total após chunking: {len(records)} pedaços indexáveis.")

    vectors = []
    final_records = []

    for rec in records:
        try:
            vec = embedder.embed_text(rec["text"])
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            continue

        if not vec:
            logger.error("Falha ao gerar embedding, pulando chunk.")
            continue

        vectors.append(vec)
        final_records.append(rec)

    if not vectors:
        logger.error("Nenhum embedding foi gerado. Abortando ingest.")
        return

    vector_size = len(vectors[0])
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)

    if recreate or not exists:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        logger.info(f"Coleção criada com dimensão={vector_size}")

    points = []
    for rec, vec in zip(final_records, vectors):
        url = rec["payload"]["url"]
        chunk_idx = rec["payload"]["chunk"]

        point_id = make_point_id(url, chunk_idx)

        point = {
            "id": point_id,
            "vector": vec,
            "payload": rec["payload"]
        }

        points.append(point)

        if len(points) >= batch_size:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info(f"Upsert batch ({len(points)}) OK")
            points = []

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info(f"Upsert final ({len(points)}) OK")

    logger.info(f"INGEST FINALIZADO — {len(final_records)} chunks inseridos.")


def main():
    logging.basicConfig(level=logging.INFO)

    embedder = get_embedder()

    base = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "webscraper"))
    possible_files = [
        os.path.join(base, "deg.json"),
        os.path.join(base, "unb_data.json"),
    ]

    docs = []
    for p in possible_files:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                docs.extend(json.load(f))

    if not docs:
        logger.error("Nenhum documento encontrado.")
        return

    ingest(docs, embedder=embedder, recreate=True)


if __name__ == "__main__":
    main()
