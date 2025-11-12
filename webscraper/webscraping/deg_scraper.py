import requests
import time
import json
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote, urljoin

logger = logging.getLogger(__name__)

BASE_URL = "https://deg.unb.br/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}

def get_post_content(url):
    """Extrai conteúdo do post e PDFs embutidos."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Erro ao acessar post {url}: {e}")
        return {"text": None, "pdfs": []}
        
    soup = BeautifulSoup(resp.text, "html.parser")

    article_container = soup.select_one("article")
    text = ""
    if article_container:
        for tag in article_container.find_all(["script", "style", "aside", "footer", "nav"]):
            tag.decompose()
        text = article_container.get_text(separator="\n", strip=True)

    pdf_urls_set = set()

    for iframe in soup.select("iframe.embedpress-embed-document-pdf"):
        src = iframe.get("src")
        if src:
            parsed = urlparse(src)
            file_param = parse_qs(parsed.query).get("file")
            if file_param:
                pdf_url = unquote(file_param[0])
                pdf_urls_set.add(pdf_url)

    if article_container:
        for a_tag in article_container.find_all("a", href=True):
            href = a_tag.get("href")
            # Verifica se o link termina com .pdf (case-insensitive)
            if href and href.lower().endswith(".pdf"):
                # Constrói a URL absoluta para o caso de links relativos
                full_pdf_url = urljoin(BASE_URL, href)
                pdf_urls_set.add(full_pdf_url)

    return {"text": text, "pdfs": list(pdf_urls_set)}

def scrape_all(query="monitoria", pages_limit=1):
    """Percorre as páginas de busca do DEG e retorna os dados na estrutura padrão."""
    logger.info(f"Iniciando scraping do DEG com a busca '{query}'...")
    all_data = []
    
    for p in range(1, pages_limit + 1):
        logger.info(f"--- Processando página {p} de resultados do DEG ---")
        search_url = f"{BASE_URL}page/{p}/?s={query}"
        
        try:
            resp = requests.get(search_url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                logger.warning(f"Página {p} não encontrada ou sem resultados. Parando.")
                break
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar página de resultados {p}: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("article.elementor-post")
        
        if not articles:
            logger.info("Nenhum artigo encontrado nesta página. Parando.")
            break

        for art in articles:
            title_tag = art.select_one("h3.elementor-post__title a")
            date_tag = art.select_one("span.elementor-post-date")
            excerpt_tag = art.select_one("div.elementor-post__excerpt")

            if not title_tag or not title_tag.has_attr('href'):
                continue
            
            post_url = title_tag["href"]
            post_title = title_tag.get_text(strip=True)
            
            logger.info(f"Processando: '{post_title}")
            
            content = get_post_content(post_url)

            standardized_item = {
                "source": "deg.unb.br",
                "url": post_url,
                "title": post_title,
                "content_text": content["text"],
                "publication_date": date_tag.get_text(strip=True) if date_tag else None,
                "pdf_urls": content["pdfs"],
                "metadata": {
                    "excerpt": excerpt_tag.get_text(strip=True) if excerpt_tag else None
                }
            }
            all_data.append(standardized_item)
            time.sleep(1)

    logger.info("Scraping do DEG finalizado.")
    return all_data

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    dados = scrape_all(query="monitoria", pages_limit=1)
    with open("deg.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    logger.info("Feito! Conteúdo salvo em deg.json")
