import json
from webscraping import deg_scraper, saa_scraper
import requests
import os
import logging
from logging_config import setup_logging
from urllib.parse import urlparse

setup_logging()
logger = logging.getLogger(__name__)

OUTPUT_FILE = "unb_data.json"
PDF_DIR = "pdfs"

def download_pdfs(all_data):
    """
    Percorre a lista de dados, baixa os PDFs encontrados e adiciona 
    o caminho local ao item de dados.
    """
    logger.info("--- Iniciando download de PDFs ---")
    os.makedirs(PDF_DIR, exist_ok=True)
    
    for item in all_data:
        local_paths = []
        if not item.get("pdf_urls"):
            continue
            
        for pdf_url in item["pdf_urls"]:
            try:
                filename = os.path.basename(urlparse(pdf_url).path)
                local_path = os.path.join(PDF_DIR, filename)
                
                if not os.path.exists(local_path):
                    logger.info(f"Baixando: {pdf_url}")
                    resp = requests.get(pdf_url, timeout=20)
                    resp.raise_for_status()
                    with open(local_path, "wb") as f:
                        f.write(resp.content)
                else:
                    logger.info(f"Arquivo já existe (pulando): {local_path}")
                
                local_paths.append(local_path)
            except Exception as e:
                logger.warning(f"Falha ao baixar o PDF {pdf_url}: {e}")
        
        item["pdf_local_paths"] = local_paths
        
    logger.info("Download de PDFs finalizado.")

def main():
    saa_data = saa_scraper.scrape_all()
    deg_data = deg_scraper.scrape_all(query="monitoria", pages_limit=1)
    combined_data = saa_data + deg_data
    
    download_pdfs(combined_data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Processo concluído! {len(combined_data)} documentos salvos em '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    main()