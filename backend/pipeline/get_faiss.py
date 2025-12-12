# backend/pipeline/get_faiss.py
import json
import os
import faiss
import pickle
import numpy as np 
from sentence_transformers import SentenceTransformer

INDEX_FILE = "pipeline/cache/vector.index"
META_FILE = "pipeline/cache/metadata.pkl"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
ACTS_PATH = "pipeline/data/julius_chunksafter.jsonl"


def get_faiss():
    if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
        print("✅ Loading existing FAISS index and metadata...")
        index = faiss.read_index(INDEX_FILE)
        with open(META_FILE, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata

    print("🧩 FAISS index not found. Building from documents.")

    model = SentenceTransformer(MODEL_NAME)
    acts = get_acts()
    acts = list(map(stringify_metadata, acts))

    print(acts)
    
    embeddings = model.encode([act for act in acts], normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    id_to_meta = {i: acts[i] for i in range(len(acts))}

    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump(id_to_meta, f)

    print("💾 Index and metadata saved.")
    return index, id_to_meta


def get_acts():
    raw_lines = []
    with open(ACTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            raw_lines.append(json.loads(line))

    # # Group by act and scene
    # from collections import defaultdict
    # grouped = defaultdict(list)
    # for line in raw_lines:
    #     key = (line['act'], line['scene'])
    #     grouped[key].append(line)

    # # Build chunks in the "In Act X, Scene Y, Speaker says that ..." style
    acts = raw_lines
    # for (act, scene), dialogues in grouped.items():
    #     text_chunk = f"In Act {act}, Scene {scene}, "
    #     utterances = [f"{d['speaker']} says that {d['text']}" for d in dialogues]
    #     text_chunk += ", ".join(utterances)
    #     acts.append({"act": act, "scene": scene, "text": text_chunk})

    return acts


def stringify_metadata(meta: dict) -> str:
    """
    Convert metadata + text into a clean, deterministic string
    suitable for embedding.
    """

    # Extract text separately
    text = meta.get("text", "")

    # Keep only metadata fields except 'text'
    meta_no_text = {k: v for k, v in meta.items() if k != "text"}

    # Sort keys for deterministic ordering
    parts = []
    for key in sorted(meta_no_text.keys()):
        parts.append(f"{key}: {meta_no_text[key]}")

    # Join metadata fields
    meta_str = "; ".join(parts)

    # Final embedding string
    return text

