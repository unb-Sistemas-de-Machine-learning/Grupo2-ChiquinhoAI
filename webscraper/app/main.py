import json
import os
import logging
import requests
import concurrent.futures
from typing import List

from app.logging_config import setup_logging
from app.webscraping import deg_scraper, saa_scraper, sei_scraper
from app.webscraping.models import Document

setup_logging()
logger = logging.getLogger(__name__)

# Configurações
DATA_DIR = "data"
INGEST_URL = os.getenv("INGEST_URL", "http://server:55555/ingest") 
BATCH_SIZE = 50

def save_source_data_to_disk(source_name: str, documents: List[Document]):
    """Salva os dados de uma fonte no disco (Backup/Persistência)."""
    if not documents:
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    filename = os.path.join(DATA_DIR, f"{source_name.lower()}_output.json")
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json.dumps(
                [d.model_dump(mode='json') for d in documents], 
                ensure_ascii=False, 
                indent=2
            ))
        logger.info(f"[DISK] Arquivo '{filename}' gravado com sucesso ({len(documents)} docs).")
    except Exception as e:
        logger.error(f"[DISK] Erro ao gravar arquivo de {source_name}: {e}")

def send_batch_to_api(batch: List[Document], source_name: str):
    """Envia um lote de documentos para a API de ingestão."""
    try:
        payload = [doc.model_dump(mode='json') for doc in batch]
        logger.info(f"[API] Enviando lote de {len(batch)} docs de {source_name} para {INGEST_URL}...")
        resp = requests.post(INGEST_URL, json=payload, timeout=120)
        
        if resp.status_code in [200, 201]:
            logger.info(f"[API] Lote enviado com sucesso!")
        else:
            logger.error(f"[API] Falha no envio: {resp.status_code} - {resp.text}")
            
    except requests.exceptions.ConnectionError:
        logger.error(f"[API] Não foi possível conectar a {INGEST_URL}. A API está online?")
    except Exception as e:
        logger.error(f"[API] Erro genérico ao enviar lote: {e}")

def process_ingestion(source_name: str, documents: List[Document]):
    """Orquestra o salvamento local e o envio para a API."""
    if not documents:
        logger.warning(f"Fonte {source_name} não retornou documentos.")
        return

    save_source_data_to_disk(source_name, documents)

    total = len(documents)
    logger.info(f"Iniciando envio de {total} documentos de {source_name} para a API...")
    
    for i in range(0, total, BATCH_SIZE):
        batch = documents[i : i + BATCH_SIZE]
        send_batch_to_api(batch, source_name)

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3, thread_name_prefix="Scraper") as executor:
        logger.info(">>> Iniciando Coleta de Dados Paralela <<<")
        
        # Submete as tarefas
        # Certifique-se que suas funções scrape_* retornam List[Document]
        future_saa = executor.submit(saa_scraper.scrape)
        future_deg = executor.submit(deg_scraper.scrape, query="monitoria")
        future_sei = executor.submit(sei_scraper.scrape)

        future_map = {
            future_saa: "SAA",
            future_deg: "DEG",
            future_sei: "SEI",
        }

        for future in concurrent.futures.as_completed(future_map):
            source_name = future_map[future]
            try:
                data = future.result()
                logger.info(f"Módulo {source_name} finalizado. Iniciando processamento")
                
                process_ingestion(source_name, data)
                
            except Exception:
                logger.critical(f"FALHA CRÍTICA NO MÓDULO {source_name}", exc_info=True)

    logger.info(">>> Processo de scraping finalizado. <<<")

if __name__ == "__main__":
    main()