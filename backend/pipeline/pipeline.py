# backend/pipeline/pipeline.py
import json
import os
import numpy as np
import google.generativeai as genai
from pipeline.get_faiss import get_faiss
from pipeline.get_embed_model import get_embed_model

DEF_SYS_PRMPT = (
    "You are a literary analyst specialized in Shakespearean literature. "
    "Use the provided context to answer the user's question. "
    "If the context is insufficient, clearly say so instead of inventing details."
    "Ensure to figure out coreferences of entitties accurately"
    "You are a concise assistant. Avoid formatting."
)

class Pipeline:
    def __init__(self, system_prompt=DEF_SYS_PRMPT):
        self.index, self.id_to_meta = get_faiss()
        self.embed_model = get_embed_model()
        self.gen_model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
        self.system_prompt = system_prompt

        # genai.configure(api_key = 'AIzaSyAH5qJyAGL-34wmRqunhJqEdrlLsEhn-2k')
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set or loaded.")

        genai.configure(api_key=api_key)

    def __call__(self, query):
        meta_docs = self._retrieve(query)
        docs = [meta_doc for meta_doc in meta_docs]
        response = self._generate(query, docs)

        return response.text, meta_docs

    def _generate(self, query, docs):
        context = "\n".join(docs)
        full_prompt = f"""{self.system_prompt}

        Context:
        {context}

        Question:
        {query}
        """

        return self.gen_model.generate_content(full_prompt)

    def _retrieve(self, query: str):
        query_emb = self.embed_model.encode([query], normalize_embeddings=True)
        query_emb = np.array(query_emb, dtype=np.float32)

        distances, indices = self.index.search(query_emb, k=10)
        return [self.id_to_meta[idx] for idx in indices[0]]