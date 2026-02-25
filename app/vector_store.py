import json
from pathlib import Path
from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from .config import settings
from .models import IndexedChunk, ChunkMetadata

class VectorStore:
    def __init__(self, index_path: Path, meta_path: Path, model_name: str):
        self.index_path = index_path
        self.meta_path = meta_path
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata: List[ChunkMetadata] = []

    def _ensure_index(self, dim: int):
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)

    def build(self, chunks: List[IndexedChunk]) -> None:
        texts = [c.text for c in chunks]
        metas = [c.metadata for c in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.asarray(embeddings, dtype="float32")
        dim = embeddings.shape[1]
        self._ensure_index(dim)
        self.index.add(embeddings)
        self.metadata = metas
        self._save()

    def _save(self) -> None:
        settings.index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump([m.dict() for m in self.metadata], f, ensure_ascii=False)

    def load(self) -> None:
        self.index = faiss.read_index(str(self.index_path))
        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta_dicts = json.load(f)
        self.metadata = [ChunkMetadata(**m) for m in meta_dicts]

    def is_built(self) -> bool:
        return self.index_path.exists() and self.meta_path.exists()

    def search(self, query: str, k: int) -> List[Tuple[ChunkMetadata, float]]:
        if self.index is None:
            self.load()
        q_emb = self.model.encode([query])
        q_emb = np.asarray(q_emb, dtype="float32")
        distances, indices = self.index.search(q_emb, k)
        hits: List[Tuple[ChunkMetadata, float]] = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            hits.append((self.metadata[idx], float(dist)))
        return hits

def get_vector_store() -> VectorStore:
    return VectorStore(
        index_path=settings.index_dir / "faiss.index",
        meta_path=settings.index_dir / "metadata.json",
        model_name=settings.embedding_model_name,
    )
