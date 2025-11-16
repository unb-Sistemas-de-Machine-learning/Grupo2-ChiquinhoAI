import json
import os
from webscraping import deg_scraper
import logging
from logging_config import setup_logging
import subprocess

setup_logging()
logger = logging.getLogger(__name__)

OUTPUT_FILE = "unb_data.json"

def main():
    combined_data = []

    logger.info("Iniciando Coleta de Dados do DEG (máximo possível)")
    
    try:
        # Coletar máximo de páginas possível (50 páginas)
        data = deg_scraper.scrape_all(query="unb", pages_limit=50)
        logger.info(f"DEG finalizado com sucesso ({len(data)} docs)")
        combined_data.extend(data)
    except Exception:
        logger.critical("FALHA CRÍTICA NO MÓDULO DEG", exc_info=True)

    logger.info(f"Coleta de dados finalizada")
    logger.info(f"Total de {len(combined_data)} documentos coletados.")

    if not combined_data:
        logger.warning("Nenhum dado foi coletado. Encerrando o script.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Processo concluído! {len(combined_data)} documentos salvos em '{OUTPUT_FILE}'.")
    
    # Ingestão automática no Qdrant
    logger.info("Iniciando ingestão automática no banco vetorial Qdrant...")
    try:
        server_dir = os.path.join(os.path.dirname(__file__), '..', 'server')
        venv_python = os.path.join(server_dir, '.venv', 'Scripts', 'python.exe')
        
        result = subprocess.run(
            [venv_python, '-m', 'app.ingest'],
            cwd=server_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info("✅ Ingestão concluída com sucesso! Documentos disponíveis para busca.")
            if result.stdout:
                logger.info(result.stdout)
        else:
            logger.error(f"❌ Falha na ingestão automática: {result.stderr}")
    except Exception:
        logger.error("❌ Erro ao executar ingestão automática. Execute 'python server/app/ingest.py' manualmente.", exc_info=True)


if __name__ == "__main__":
    main()
