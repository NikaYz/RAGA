# backend/ml_pipeline/download_model.py
"""
Downloads a sentence-transformers model (cached locally).
Used by CI to ensure the model is present before building embeddings.
"""
from sentence_transformers import SentenceTransformer
import argparse
import os

def main(model_name: str, cache_dir: str):
    os.makedirs(cache_dir, exist_ok=True)
    print(f"Downloading model {model_name} to {cache_dir} (if not cached)...")
    model = SentenceTransformer(model_name)
    # model is now cached by sentence-transformers / huggingface
    print("Model downloaded / cached.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--cache-dir", default="/root/.cache/huggingface")
    args = parser.parse_args()
    main(args.model_name, args.cache_dir)
