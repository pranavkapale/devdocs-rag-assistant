from typing import List
import os
import requests

from .config import settings
from .vector_store import get_vector_store
from .models import ChunkMetadata

def fetch_chunk_texts(meta_list: List[ChunkMetadata]) -> List[str]:
    texts = []
    for meta in meta_list:
        try:
            with open(meta.source, "r", encoding="utf-8", errors="ignore") as f:
                texts.append(f.read())
        except Exception:
            texts.append("")
    return texts

def assemble_context(meta_list: List[ChunkMetadata]) -> str:
    contexts = []
    for meta, full_text in zip(meta_list, fetch_chunk_texts(meta_list)):
        snippet = full_text[:1000]
        contexts.append(f"[Source: {meta.source}]\n{snippet}")
    merged = "\n\n".join(contexts)
    return merged[: settings.max_context_chars]

def build_prompt(question: str, context: str) -> str:
    return (
        "You are a helpful assistant for a software developer. "
        "Answer the question using only the information from the context. "
        "If the answer is not in the context, say you do not know.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )

def call_llm(prompt: str) -> str:
    url = f"{settings.llm_api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 512,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()

def answer_question(question: str) -> tuple[str, List[ChunkMetadata]]:
    store = get_vector_store()
    if not store.is_built():
        raise RuntimeError("Index does not exist, please build it first.")
    hits = store.search(question, settings.top_k)
    metas = [m for m, _ in hits]
    context = assemble_context(metas)
    prompt = build_prompt(question, context)
    answer = call_llm(prompt)
    return answer, metas
