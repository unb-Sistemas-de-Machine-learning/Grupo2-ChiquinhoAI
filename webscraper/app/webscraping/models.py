from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

class Attachment(BaseModel):
    """Representa um arquivo anexo (PDF, DOC) encontrado na página pai."""
    url: str
    filename: Optional[str] = None
    media_type: str = "application/pdf"

class Document(BaseModel):
    """
    Modelo único de documento para o RAG.
    Representa a 'Página Pai' (HTML).
    """
    id: str = Field(default="", description="Hash MD5 da URL para garantir unicidade")
    title: str
    url: str
    source: str = Field(..., description="Fonte do dado: saa.unb.br, deg.unb.br, sei.unb.br")
    content_text: str = Field(..., description="Conteúdo textual extraído da página HTML")
    publication_date: Optional[datetime] = None
    
    attachments: List[Attachment] = Field(default_factory=list)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='before')
    @classmethod
    def generate_id_from_url(cls, data: Any) -> Any:
        """
        Gera hash MD5 da URL se o ID não for passado ou for vazio.
        Executa ANTES da validação dos campos individuais.
        """
        if isinstance(data, dict):
            # Verifica se 'id' está vazio ou ausente, e se temos 'url' para gerar
            if not data.get('id') and data.get('url'):
                data['id'] = hashlib.md5(str(data['url']).encode('utf-8')).hexdigest()
        return data