# import json
# from webscraping import deg_scraper, saa_scraper, sei_scraper
# import requests
# import os
# import logging
# from logging_config import setup_logging
# from urllib.parse import urlparse
# import concurrent.futures
#
# setup_logging()
# logger = logging.getLogger(__name__)
#
# OUTPUT_FILE = "unb_data.json"
# PDF_DIR = "pdfs"
#
# def download_pdfs(all_data: list[dict]):
#     """
#     Coleta todas as URLs de PDF únicas, tenta baixar cada uma UMA VEZ,
#     e depois mapeia os caminhos locais de volta para os itens.
#     """
#     logger.info("Iniciando download de PDFs")
#     os.makedirs(PDF_DIR, exist_ok=True)
#
#     all_unique_urls = set()
#     for item in all_data:
#         if item.get("pdf_urls"):
#             all_unique_urls.update(item["pdf_urls"])
#
#     if not all_unique_urls:
#         logger.info("Nenhum PDF para baixar.")
#         return
#
#     logger.info(f"Encontradas {len(all_unique_urls)} URLs de PDF únicas para processar.")
#
#     url_to_local_path_map = {}
#
#     for pdf_url in all_unique_urls:
#         try:
#             filename = os.path.basename(urlparse(pdf_url).path)
#             if not filename:
#                 logger.warning(f"URL não contém nome de arquivo (pulando): {pdf_url}")
#                 continue
#             local_path = os.path.join(PDF_DIR, filename)
#
#             if not os.path.exists(local_path):
#                 logger.info(f"Baixando: {pdf_url}")
#                 resp = requests.get(pdf_url, timeout=20)
#                 resp.raise_for_status()
#                 with open(local_path, "wb") as f:
#                     f.write(resp.content)
#             else:
#                 logger.info(f"Arquivo já existe (pulando download): {local_path}")
#
#             url_to_local_path_map[pdf_url] = local_path
#
#         except requests.exceptions.Timeout:
#             logger.warning(f"Timeout ao tentar baixar {pdf_url}.")
#         except requests.exceptions.RequestException as e:
#             logger.warning(f"Falha ao baixar o PDF {pdf_url}: {e}.")
#         except Exception as e:
#             logger.error(f"Erro inesperado ao processar {pdf_url}: {e}")
#
#     logger.info("Fase de download concluída.")
#
#     logger.info("Mapeando caminhos locais de volta para os dados...")
#     for item in all_data:
#         item["pdf_local_paths"] = [url_to_local_path_map[url]
#                                    for url in item.get("pdf_urls", [])
#                                    if url in url_to_local_path_map]
#
#     logger.info("Download de PDFs finalizado.")
#
#
# def main():
#     combined_data = []
#
#     with concurrent.futures.ThreadPoolExecutor(max_workers=3, thread_name_prefix="Scraper") as executor:
#
#         logger.info("Iniciando Coleta de Dados Paralela")
#
#         future_saa = executor.submit(saa_scraper.scrape_all)
#         future_deg = executor.submit(deg_scraper.scrape_all, query="monitoria", pages_limit=1)
#         future_sei = executor.submit(sei_scraper.scrape_all)
#
#         futures = {
#             future_saa: "SAA",
#             future_deg: "DEG",
#             future_sei: "SEI",
#         }
#
#         for future in concurrent.futures.as_completed(futures):
#             source_name = futures[future]
#             try:
#                 data = future.result()
#                 logger.info(f"Módulo {source_name} finalizado com sucesso ({len(data)} docs)")
#                 combined_data.extend(data)
#             except Exception:
#                 logger.critical(f"FALHA CRÍTICA NO MÓDULO {source_name}", exc_info=True)
#
#     logger.info(f"Coleta de dados finalizada")
#     logger.info(f"Total de {len(combined_data)} documentos coletados de todas as fontes.")
#
#     if not combined_data:
#         logger.warning("Nenhum dado foi coletado. Encerrando o script.")
#         return
#
#     download_pdfs(combined_data)
#
#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(combined_data, f, ensure_ascii=False, indent=2)
#
#     logger.info(f"Processo concluído! {len(combined_data)} documentos salvos em '{OUTPUT_FILE}'.")
#
#
# if __name__ == "__main__":
#     main()