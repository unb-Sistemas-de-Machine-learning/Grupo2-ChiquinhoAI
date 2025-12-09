import json
import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List

from app.webscraping.models import Document
from app.webscraping.utils import parse_pt_date, clean_text

logger = logging.getLogger(__name__)

BASE_URL = "https://sei.unb.br/sei/publicacoes/"
URL_ENDPOINT = urljoin(BASE_URL, "controlador_publicacoes.php")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

def fetch_document_text(doc_url: str) -> str:
    """Baixa o HTML do documento do SEI e extrai o texto central."""
    try:
        resp = requests.get(doc_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        doc_soup = BeautifulSoup(resp.content, "html.parser", from_encoding="iso-8859-1")

        # Lógica original restaurada para garantir robustez
        start_tag = doc_soup.find('p', class_='Texto_Centralizado_Maiusculas_Negrito') 
        if not start_tag:
            start_tag = doc_soup.find('table')
        
        end_tag = doc_soup.find('div', attrs={'unselectable': 'on'})

        if not start_tag:
            return ""
        
        # Fallback se não achar o fim
        if not end_tag:
            return start_tag.get_text(strip=True, separator=' ')

        content = []
        curr = start_tag
        while curr and curr != end_tag:
            if curr.name in ['p', 'table', 'div', 'span']:
                # separator=' ' é importante para não grudar palavras em tabelas
                text = curr.get_text(separator=" ", strip=True)
                if text: content.append(text)
            curr = curr.find_next_sibling()
            
        return "\n\n".join(content)
    except Exception as e:
        logger.error(f"Erro ao ler doc SEI {doc_url}: {e}")
        return ""

# Restaurado o padrão "FCTE ou FGA"
def scrape(series_ids=[("239", "Resolução"), ("844", "Edital")], search_term="FCTE ou FGA") -> List[Document]:
    logger.info(f"Iniciando scraping SEI: termo '{search_term}'")
    documents = []

    for series_id, doc_type in series_ids:
        # Configuração do Payload do SEI
        params = {
            "acao": "publicacao_pesquisar",
            "acao_origem": "publicacao_pesquisar",
            "id_orgao_publicacao": "0",
            "id_serie": series_id,
            "rdo_data_publicacao": "I",
        }
        
        # Restaurado hdnInfraNroItens para 20
        payload = {
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

        # Loop de Paginação
        while True:
            try:
                resp = requests.post(URL_ENDPOINT, params=params, data=payload, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(resp.text, "html.parser")
            except Exception as e:
                logger.error(f"Erro na requisição da lista: {e}")
                break

            rows = soup.find_all("tr", id=lambda x: x and x.startswith("trPublicacaoA"))
            if not rows: 
                logger.info(f"Sem mais resultados para série {series_id}.")
                break

            for row in rows:
                try:
                    cols = row.find_all("td")
                    link_tag = cols[1].find("a")
                    if not link_tag: continue

                    doc_url = urljoin(BASE_URL, link_tag["href"])
                    doc_title = cols[2].get_text(strip=True)
                    date_str = cols[4].get_text(strip=True) # DD/MM/YYYY
                    dept = cols[5].get_text(strip=True)

                    full_text = fetch_document_text(doc_url)
                    
                    logger.info(f"Processando documento: '{doc_title[:50]}...'")
                    doc = Document(
                        title=doc_title,
                        url=doc_url,
                        source="sei.unb.br",
                        content_text=clean_text(full_text),
                        publication_date=parse_pt_date(date_str),
                        metadata={
                            "type": doc_type,
                            "department": dept,
                        }
                    )
                    documents.append(doc)
                    time.sleep(0.5) # Politeness
                except Exception as e:
                    logger.warning(f"Erro ao processar linha: {e}")

            # Lógica de Próxima Página
            link_proxima = soup.find("a", string="Próxima")
            if not link_proxima:
                break
            
            # Atualiza o offset para a próxima página
            current_offset = int(payload["hdnInicio"])
            payload["hdnInicio"] = str(current_offset + int(payload["hdnInfraNroItens"]))
            time.sleep(1)

    logger.info(f"SEI finalizado. {len(documents)} documentos extraídos.")
    return documents

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    docs = scrape()
    with open("sei_output.json", "w", encoding="utf-8") as f:
        f.write(json.dumps([d.model_dump(mode='json') for d in docs], ensure_ascii=False, indent=2))