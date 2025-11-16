from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

# Lazy-load the model to avoid heavy import at module import time
_model = None

def _get_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name)
    return _model

def embed_texts(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
    """Return a list of embeddings (lists of floats) for the given texts."""
    model = _get_model(model_name)
    vectors = model.encode(texts, show_progress_bar=False)
    # Ensure plain python lists (JSON serializable if needed)
    return [np.array(vec).tolist() for vec in vectors]

def embed_text(text: str, model_name: str = "all-MiniLM-L6-v2") -> List[float]:
    return embed_texts([text], model_name=model_name)[0]
