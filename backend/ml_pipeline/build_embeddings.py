# backend/ml_pipeline
"""
Rebuild FAISS index and metadata.pkl from pipeline/data/*.jsonl
Saves to pipeline/cache/vector.index and pipeline/cache/metadata.pkl
Intended to be run in CI before deployment.
"""
import argparse
import json
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "julius_chunks.jsonl")
INDEX_FILE = os.path.join(ROOT, "cache", "vector.index")
META_FILE = os.path.join(ROOT, "cache", "metadata.pkl")

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_docs(path):
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
    return docs

def stringify_metadata(meta):
    # keep text as the searchable text
    return meta.get("text", "")

def build_index(model_name=DEFAULT_MODEL, k=10):
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    model = SentenceTransformer(model_name)
    acts = load_docs(DATA_PATH)
    docs = [stringify_metadata(a) for a in acts]
    print(f"Encoding {len(docs)} docs with model {model_name} ...")
    embeddings = model.encode(docs, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype=np.float32)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    id_to_meta = {i: acts[i] for i in range(len(acts))}
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump(id_to_meta, f)
    print("Saved index and metadata at:", INDEX_FILE, META_FILE)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()
    build_index(model_name=args.model)
