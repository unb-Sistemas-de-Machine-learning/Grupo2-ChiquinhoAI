import json
import requests
import logging
from logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

OUTPUT_FILE = "unb_data.json"
INGEST_URL = "http://server:55555/ingest"

BATCH_SIZE = 50


def send_batch(batch):
    try:
        resp = requests.post(INGEST_URL, json=batch, timeout=120)
        if resp.status_code != 200:
            logger.error(f"Falha no batch: {resp.text}")
        else:
            logger.info(f"Lote enviado com sucesso! ({len(batch)} docs)")
    except Exception as e:
        logger.exception("Erro ao enviar lote")


def main():
    combined_data = []

    logger.info("Iniciando coleta...")

    from webscraping import deg_scraper
    data = deg_scraper.scrape_all(query="unb", pages_limit=50)
    combined_data.extend(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Total: {len(combined_data)} documentos coletados.")

    logger.info("Iniciando envio em lotes...")

    for i in range(0, len(combined_data), BATCH_SIZE):
        batch = combined_data[i:i + BATCH_SIZE]
        logger.info(f"Enviando batch {i//BATCH_SIZE+1} contendo {len(batch)} docs...")
        send_batch(batch)

    logger.info("Ingestão completa!")


if __name__ == "__main__":
    main()