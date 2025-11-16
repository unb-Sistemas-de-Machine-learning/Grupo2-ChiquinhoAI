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
MAX_CHARS = 3500

llm = get_llm()


def split_text(text: str, max_chars: int = MAX_CHARS) -> List[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
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

    logger.info(f"Total após chunking: {len(records)} pedaços indexáveis.")

    vectors = []
    final_records = []

    for rec in records:
        try:
            vec = llm.embed_text(rec["text"])
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
        next_id = 1
    else:
        info = client.get_collection(COLLECTION_NAME)
        next_id = info.points_count + 1

    points = []
    for i, (rec, vec) in enumerate(zip(final_records, vectors)):
        point = {
            "id": next_id + i,
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

    ingest(docs, recreate=True)


if __name__ == "__main__":
    main()