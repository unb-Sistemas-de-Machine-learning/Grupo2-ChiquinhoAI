import requests
import time
import json
import logging
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

BASE_URL = "https://saa.unb.br"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}

def get_saa_page_content(url):
    """Extrai texto principal e PDFs de uma página SAA."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Erro ao acessar {url}: {e}")
        return {"texto": None, "pdfs": []}

    soup = BeautifulSoup(resp.text, "html.parser")
    article_body = soup.select_one('div[itemprop="articleBody"]') or soup.find("div", class_="mc-column")
    
    texto = ""
    pdfs = []

    if article_body:
        for tag in article_body.find_all(["script", "style", "aside", "footer"]):
            tag.decompose()
        texto = article_body.get_text(separator="\n", strip=True)
        for a in article_body.find_all("a", href=True):
            link_url = urljoin(BASE_URL, a["href"])
            if link_url.lower().endswith(".pdf"):
                pdfs.append(link_url)
    return {"texto": texto, "pdfs": pdfs}

def process_link(link_info: Dict[str, str]) -> Dict[str, Any]:
    """
    Função auxiliar que processa um único link: faz o scraping,
    formata os dados e retorna um dicionário padronizado.
    """
    url = link_info["url"]
    title = link_info["title"]
    category = link_info["category"]
    
    logger.info(f"Processando: '{title}' (Categoria: {category})")
    content = get_saa_page_content(url)
    
    return {
        "source": "saa.unb.br",
        "url": url,
        "title": title,
        "content_text": content["texto"],
        "publication_date": None,
        "pdf_urls": content["pdfs"],
        "metadata": {
            "category": category
        }
    }

def scrape_all() -> List[Dict[str, Any]]:
    """
    Orquestra o scraping: descobre todos os links únicos e depois
    os processa para extrair o conteúdo.
    """
    logger.info("Iniciando scraping do SAA...")
    
    try:
        grad_url = urljoin(BASE_URL, "/graduacao")
        resp = requests.get(grad_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Não foi possível acessar a página principal de Graduação. Erro: {e}")
        return []

    links_to_process = []
    processed_urls = set()

    # Coleta das "Caixas Azuis"
    for caixa_div in soup.select("div.moduletable h3.caixa_azul + ul.caixa_azul"):
        category_title = caixa_div.find_previous_sibling("h3").get_text(strip=True)
        for a in caixa_div.find_all("a", href=True):
            link_url = urljoin(BASE_URL, a["href"])
            if link_url not in processed_urls:
                processed_urls.add(link_url)
                links_to_process.append({
                    "url": link_url,
                    "title": a.get_text(strip=True),
                    "category": category_title
                })

    # Coleta do Menu Principal de Graduação
    menu_graduacao_ul = soup.select_one('li.parent a[href="/graduacao"] + ul.dropdown-menu-principal')
    if menu_graduacao_ul:
        for a in menu_graduacao_ul.find_all("a", href=True):
            link_url = urljoin(BASE_URL, a["href"])
            if link_url not in processed_urls:
                processed_urls.add(link_url)
                links_to_process.append({
                    "url": link_url,
                    "title": a.get_text(strip=True),
                    "category": "GRADUAÇÃO"
                })

    logger.info(f"Foram encontrados {len(links_to_process)} links únicos para processar.")

    all_data = []
    for link_info in links_to_process:
        item_data = process_link(link_info)
        if item_data:
            all_data.append(item_data)
        time.sleep(1)

    logging.info("Scraping finalizado.")
    return all_data

if __name__ == "__main__":
    dados = scrape_all()
    with open("saa_content.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    logger.info("Feito! Conteúdo salvo em saa_content.json")
