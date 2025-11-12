import requests
import json
import logging
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

BASE_URL = "https://sei.unb.br/sei/publicacoes/"
URL_ENDPOINT = urljoin(BASE_URL, "controlador_publicacoes.php")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}

def fetch_page(params: Dict[str, Any], data: Dict[str, Any]) -> Optional[BeautifulSoup]:
    """Obtém o HTML da página de lista de publicações do SEI."""
    try:
        current_data = data.copy()
        logger.info(f"Buscando página com offset {current_data['hdnInicio']}...")
        
        resp = requests.post(
            URL_ENDPOINT,
            params=params,
            data=current_data,
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Erro ao acessar a página de lista: {e}")
        return None


def fetch_document_content(doc_url: str) -> str:
    """Obtém o conteúdo textual de um documento do SEI."""
    logger.info(f"Baixando conteúdo de: {doc_url}")
    try:
        resp = requests.get(doc_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        doc_soup = BeautifulSoup(resp.content, "html.parser", from_encoding="iso-8859-1")

        start_tag = doc_soup.find('p', class_='Texto_Centralizado_Maiusculas_Negrito')
        if not start_tag:
            start_tag = doc_soup.find('table')
            if not start_tag:
                logger.warning(f"Não foi possível identificar o início do texto ({doc_url})")
                return ""

        end_tag = doc_soup.find('div', attrs={'unselectable': 'on'})
        if not end_tag:
            logger.warning(f"Não foi possível identificar o fim do texto ({doc_url})")
            return start_tag.get_text(strip=True, separator=' ')

        content_parts = []
        current_tag = start_tag
        while current_tag and current_tag != end_tag:
            if current_tag.name in ['p', 'table', 'div']:
                text = current_tag.get_text(strip=True, separator=' ')
                if text:
                    content_parts.append(text)
            current_tag = current_tag.find_next_sibling()

        return "\n\n".join(content_parts) if content_parts else ""
    except requests.RequestException as e:
        logger.error(f"Erro ao baixar documento: {e}")
        return ""
    except Exception as e:
        logger.error(f"Erro ao processar documento: {e}")
        return ""


def parse_documents_page(soup: BeautifulSoup, doc_type: str) -> List[Dict[str, Any]]:
    """Extrai e processa todos os documentos de uma página."""
    documentos: List[Dict[str, Any]] = []
    tabela = soup.find("table", id="tblPublicacoes")

    if not tabela:
        logger.info("Nenhuma tabela de resultados encontrada.")
        return []

    linhas = tabela.find_all("tr", id=lambda x: x and x.startswith("trPublicacaoA"))
    if not linhas:
        logger.info("Nenhum documento encontrado nesta página.")
        return []

    for linha in linhas:
        try:
            cols = linha.find_all("td")
            link_tag = cols[1].find("a")
            if not link_tag:
                continue

            link_absoluto = urljoin(BASE_URL, link_tag["href"])
            numero_doc = link_tag.get_text(strip=True)
            descricao = cols[2].get_text(strip=True)
            data_publicacao = cols[4].get_text(strip=True)
            unidade = cols[5].get_text(strip=True)

            snippet = "N/A"
            linha_b = linha.find_next_sibling("tr", class_="pesquisaSnippet")
            if linha_b:
                snippet = linha_b.find("td").get_text(strip=True)
            
            time.sleep(0.5)
            conteudo_documento = fetch_document_content(link_absoluto)

            documentos.append({
                "source": "sei.unb.br",
                "url": link_absoluto,
                "title": descricao,
                "content_text": conteudo_documento,
                "publication_date": data_publicacao,
                "pdf_urls": [],
                "metadata": {
                    "excerpt": snippet,
                    "document_type": doc_type,
                    "document_number": numero_doc,
                    "department": unidade,
                }
            })
        except Exception as e:
            logger.warning(f"Erro ao processar linha da tabela: {e}")

    return documentos


def run_sei_scrape(series_id: str, doc_type: str, search_term: str) -> List[Dict[str, Any]]:
    """Executa scraping com paginação para uma série específica."""
    logger.info(f"Iniciando scraping de {doc_type} (Série {series_id})")
    logger.info(f"Termo de busca: {search_term}")

    params_search = {
        "acao": "publicacao_pesquisar",
        "acao_origem": "publicacao_pesquisar",
        "id_orgao_publicacao": "0",
        "id_serie": series_id,
        "rdo_data_publicacao": "I",
    }
    data_search_base = {
        "hdnInfraTipoPagina": "1",
        "sbmPesquisar": "Pesquisar",
        "selOrgao[]": "0",
        "txtInteiroTeor": search_term,
        "selSerie": series_id,
        "rdoDataPublicacao": "I",
        "hdnInfraNroItens": "20",
        "hdnInicio": "0",
        "txtResumo": "",
        "selUnidadeResponsavel": "",
        "txtNumero": "",
        "txtProtocoloPesquisa": "",
        "selVeiculoPublicacao": "",
        "txtDataDocumento": "",
        "txtDataInicio": "",
        "txtDataFim": "",
    }

    todos_os_documentos: List[Dict[str, Any]] = []
    pagina_atual = 0
    itens_por_pagina = int(data_search_base["hdnInfraNroItens"])

    while True:
        data_payload = data_search_base.copy()
        data_payload["hdnInicio"] = str(pagina_atual * itens_por_pagina)
        soup = fetch_page(params_search, data_payload)
        if not soup:
            break

        documentos_da_pagina = parse_documents_page(soup, doc_type)
        if not documentos_da_pagina:
            logger.info("Nenhum documento adicional encontrado.")
            break

        todos_os_documentos.extend(documentos_da_pagina)
        logger.info(f"Página {pagina_atual + 1} processada ({len(documentos_da_pagina)} documentos)")

        link_proxima = soup.find("a", string="Próxima")
        if not link_proxima:
            break

        pagina_atual += 1
        time.sleep(1)

    logger.info(f"Total de {len(todos_os_documentos)} documentos extraídos ({doc_type})")
    return todos_os_documentos


def scrape_all(search_term: str = "FCTE ou FGA") -> List[Dict[str, Any]]:
    """Executa scraping para as Séries configuradas (Editais e Resoluções)."""
    logger.info("Iniciando scraping do SEI...")
    SEARCHES_TO_RUN = [
        {"id": "239", "type": "Resolução"},
        {"id": "844", "type": "Edital"},
    ]

    all_scraped_data = []
    for search in SEARCHES_TO_RUN:
        results = run_sei_scrape(
            series_id=search["id"],
            doc_type=search["type"],
            search_term=search_term
        )
        all_scraped_data.extend(results)
        logger.info(f"Scraping de {search['type']} finalizado\n")

    logger.info("Scraping completo.")
    return all_scraped_data

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    dados = scrape_all()
    with open("sei.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    logger.info("Feito! Conteúdo salvo em sei.json")
