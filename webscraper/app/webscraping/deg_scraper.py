import requests
import time
import json
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote, urljoin
from typing import List

from app.webscraping.models import Document, Attachment
from app.webscraping.utils import parse_pt_date, clean_text

logger = logging.getLogger(__name__)

BASE_URL = "https://deg.unb.br/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

def get_post_details(url: str) -> dict:
    """Extrai texto e identifica anexos (iFrames e Links)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Erro no post {url}: {e}")
        return {"text": "", "attachments": []}
        
    soup = BeautifulSoup(resp.text, "html.parser")
    article = soup.select_one("article")
    
    text = ""
    attachments = []
    seen_urls = set()

    if article:
        # Limpeza
        for tag in article.find_all(["script", "style", "aside", "nav"]):
            tag.decompose()
        text = clean_text(article.get_text(separator=" ", strip=True))

        # 1. PDFs em iFrames (Comum no Elementor do DEG)
        for iframe in soup.select("iframe.embedpress-embed-document-pdf"):
            src = iframe.get("src")
            if src:
                # O src geralmente é um visualizador, o arquivo real está no query param 'file'
                parsed = urlparse(src)
                file_param = parse_qs(parsed.query).get("file")
                if file_param:
                    pdf_url = unquote(file_param[0])
                    if pdf_url not in seen_urls:
                        attachments.append(Attachment(url=pdf_url, filename="Documento Embutido"))
                        seen_urls.add(pdf_url)

        # 2. PDFs em Links Diretos
        for a in article.find_all("a", href=True):
            href = a.get("href")
            if href.lower().endswith(".pdf"):
                full_url = urljoin(BASE_URL, href)
                if full_url not in seen_urls:
                    attachments.append(Attachment(
                        url=full_url, 
                        filename=a.get_text(strip=True) or "Anexo PDF"
                    ))
                    seen_urls.add(full_url)

    return {"text": text, "attachments": attachments}

def scrape(query="monitoria", pages_limit=1) -> List[Document]:
    logger.info(f"Iniciando scraping DEG: termo '{query}'")
    documents = []
    
    for p in range(1, pages_limit + 1):
        search_url = f"{BASE_URL}page/{p}/?s={query}"
        try:
            resp = requests.get(search_url, headers=HEADERS, timeout=10)
            if resp.status_code != 200: break
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception:
            break

        articles = soup.select("article.elementor-post")
        if not articles: break

        for art in articles:
            title_tag = art.select_one("h3.elementor-post__title a")
            date_tag = art.select_one("span.elementor-post-date")
            excerpt_tag = art.select_one("div.elementor-post__excerpt")

            if not title_tag: continue
            
            post_url = title_tag["href"]
            post_title = title_tag.get_text(strip=True)
            date_str = date_tag.get_text(strip=True) if date_tag else None
            
            logger.info(f"Processando: {post_title}")
            details = get_post_details(post_url)
            
            doc = Document(
                title=post_title,
                url=post_url,
                source="deg.unb.br",
                content_text=details["text"],
                publication_date=parse_pt_date(date_str),
                attachments=details["attachments"],
                metadata={
                    "excerpt": clean_text(excerpt_tag.get_text()) if excerpt_tag else "",
                    "search_term": query
                }
            )
            documents.append(doc)
            time.sleep(1)

    logger.info(f"DEG finalizado. {len(documents)} documentos extraídos.")
    return documents

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    docs = scrape()
    with open("deg_output.json", "w", encoding="utf-8") as f:
        f.write(json.dumps([d.model_dump(mode='json') for d in docs], ensure_ascii=False, indent=2))