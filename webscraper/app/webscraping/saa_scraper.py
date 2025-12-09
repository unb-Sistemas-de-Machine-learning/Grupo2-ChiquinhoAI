import requests
import time
import json
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List
from app.webscraping.models import Document, Attachment
from app.webscraping.utils import clean_text

logger = logging.getLogger(__name__)

BASE_URL = "https://saa.unb.br"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

def get_saa_page_details(url: str) -> dict:
    """Acessa a página e separa texto de anexos."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Erro ao acessar {url}: {e}")
        return {"text": "", "attachments": []}

    soup = BeautifulSoup(resp.text, "html.parser")
    article_body = soup.select_one('div[itemprop="articleBody"]') or soup.find("div", class_="mc-column")
    
    texto = ""
    attachments = []

    if article_body:
        # 1. Limpeza do DOM (remove scripts, menus laterais, etc)
        for tag in article_body.find_all(["script", "style", "aside", "footer"]):
            tag.decompose()
        
        # 2. Extração de Texto Limpo
        texto = clean_text(article_body.get_text(separator=" ", strip=True))
        
        # 3. Extração de Anexos (PDFs)
        for a in article_body.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf"):
                full_url = urljoin(BASE_URL, href)
                attachments.append(Attachment(
                    url=full_url,
                    filename=a.get_text(strip=True) or href.split('/')[-1]
                ))
                
    return {"text": texto, "attachments": attachments}

def process_link(link_info: dict) -> Document:
    """Converte um link bruto em um objeto Document completo."""
    url = link_info["url"]
    title = link_info["title"]
    category = link_info["category"]
    
    logger.info(f"Processando: '{title}'")
    details = get_saa_page_details(url)
    
    # O SAA raramente tem data explícita no HTML, deixamos None ou usamos data atual se crítico
    return Document(
        title=title,
        url=url,
        source="saa.unb.br",
        content_text=details["text"],
        publication_date=None, 
        attachments=details["attachments"],
        metadata={
            "category": category,
            "original_title": title
        }
    )

def scrape() -> List[Document]:
    logger.info("Iniciando scraping do SAA...")
    
    try:
        grad_url = urljoin(BASE_URL, "/graduacao")
        resp = requests.get(grad_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Falha fatal ao acessar SAA: {e}")
        return []

    processed_urls = set()
    documents = []

    # Estratégia: Coletar links das caixas azuis e menus
    targets = []
    
    # Caixas Azuis
    for caixa_div in soup.select("div.moduletable h3.caixa_azul + ul.caixa_azul"):
        cat_title = caixa_div.find_previous_sibling("h3").get_text(strip=True)
        for a in caixa_div.find_all("a", href=True):
            targets.append({"url": urljoin(BASE_URL, a["href"]), "title": a.get_text(strip=True), "category": cat_title})

    # Menu Dropdown
    menu_grad = soup.select_one('li.parent a[href="/graduacao"] + ul.dropdown-menu-principal')
    if menu_grad:
        for a in menu_grad.find_all("a", href=True):
            targets.append({"url": urljoin(BASE_URL, a["href"]), "title": a.get_text(strip=True), "category": "Menu Graduação"})

    for target in targets:
        if target["url"] not in processed_urls:
            processed_urls.add(target["url"])
            try:
                doc = process_link(target)
                if doc.content_text: # Só salva se tiver conteúdo
                    documents.append(doc)
            except Exception as e:
                logger.error(f"Erro ao processar {target['url']}: {e}")
            time.sleep(0.5) # Politeness

    logger.info(f"SAA finalizado. {len(documents)} documentos extraídos.")
    return documents

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    docs = scrape()
    with open("saa_output.json", "w", encoding="utf-8") as f:
        f.write(json.dumps([d.model_dump(mode='json') for d in docs], ensure_ascii=False, indent=2))