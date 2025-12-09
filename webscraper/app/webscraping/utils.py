import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

MONTHS_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
}

def parse_pt_date(date_str: str) -> datetime:
    """
    Converte datas variadas (ex: '29 de agosto de 2024' ou '10/02/2024') 
    para objeto datetime. Retorna None se falhar.
    """
    if not date_str:
        return None
    
    date_str = date_str.strip().lower()

    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        pass

    try:
        parts = date_str.split(' de ')
        if len(parts) == 3:
            day = int(parts[0])
            month = MONTHS_PT.get(parts[1])
            year = int(parts[2])
            if month:
                return datetime(year, month, day)
    except Exception:
        pass

    logger.warning(f"Não foi possível converter a data: '{date_str}'")
    return None

def clean_text(text: str) -> str:
    """Remove excesso de espaços e quebras de linha."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()