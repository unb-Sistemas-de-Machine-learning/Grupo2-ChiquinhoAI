import os
import json
import logging
from typing import List

from qdrant_client import QdrantClient

from app.config import get_settings
from app.embeddings import embed_texts

logger = logging.getLogger(__name__)

COLLECTION_NAME = "documents"


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
    """Converte a lista de documentos em payloads para subir no Qdrant.

    Cada documento deverá ter ao menos: title, url, content_text, publication_date, source
    """
    records = []
    for i, d in enumerate(docs):
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
        records.append({"id": i + 1, "text": text, "payload": payload})
    return records


def ingest(docs: List[dict], batch_size: int = 64, model_name: str = "all-MiniLM-L6-v2", recreate: bool = False):
    """
    Ingere documentos no Qdrant.
    
    Args:
        docs: Lista de documentos a ingerir
        batch_size: Tamanho do batch para upsert
        model_name: Nome do modelo de embeddings
        recreate: Se True, recria a coleção (apaga tudo). Se False, apenas adiciona novos pontos.
    """
    settings = get_settings()
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    client = QdrantClient(url=settings.qdrant_url, api_key=qdrant_api_key)

    records = build_records_from_docs(docs)
    if not records:
        logger.warning("Nenhum documento para ingerir.")
        return

    # Generate embeddings in batches
    texts = [r["text"] for r in records]
    logger.info(f"Gerando embeddings para {len(texts)} documentos (modelo={model_name})...")
    vectors = embed_texts(texts, model_name=model_name)

    # Verifica se a coleção existe
    vector_size = len(vectors[0])
    try:
        from qdrant_client.models import Distance, VectorParams
        
        collections = client.get_collections().collections
        collection_exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if recreate or not collection_exists:
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logger.info(f"Coleção '{COLLECTION_NAME}' {'recriada' if recreate else 'criada'} com dimensão={vector_size}.")
            next_id = 1
        else:
            # Obter próximo ID disponível
            collection_info = client.get_collection(COLLECTION_NAME)
            next_id = collection_info.points_count + 1
            logger.info(f"Coleção '{COLLECTION_NAME}' já existe com {collection_info.points_count} pontos. Adicionando novos documentos a partir do ID {next_id}.")
    except Exception:
        logger.exception("Falha ao criar/recriar coleção no Qdrant. Verifique a versão do client/servidor.")
        return

    # Upsert em batches com IDs incrementais
    points = []
    for i, (rec, vec) in enumerate(zip(records, vectors)):
        points.append({"id": next_id + i, "vector": vec, "payload": rec["payload"]})
        if len(points) >= batch_size:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info(f"Upserted batch de {len(points)} pontos")
            points = []

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info(f"Upserted final batch de {len(points)} pontos")
    
    logger.info(f"✅ Total de {len(records)} documentos adicionados ao banco vetorial.")


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Busca arquivos JSON gerados pelos scrapers (padrão: webscraper/*.json)
    possible = [
        os.path.join(os.path.dirname(__file__), "..", "..", "webscraper", "deg.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "webscraper", "unb_data.json"),
    ]
    # Normaliza paths
    possible = [os.path.normpath(p) for p in possible]
    docs = _load_source_files(possible)

    if not docs:
        logger.info("Nenhum arquivo local encontrado. Tentando rodar scraper DEG diretamente...")
        try:
            # Import dynamic to avoid heavy deps if not needed
            from webscraper.webscraping.deg_scraper import scrape_all

            docs = scrape_all(query="monitoria", pages_limit=1)
        except Exception:
            logger.exception("Falha ao executar scraper DEG; certifique-se de ter o pacote webscraper disponível.")

    ingest(docs, recreate=True)  # Modo manual recria a coleção


if __name__ == "__main__":
    main()
