# backend/pipeline/get_embed_model.py
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_embed_model(model_name = DEFAULT_MODEL):
    model = SentenceTransformer(model_name)
    return model