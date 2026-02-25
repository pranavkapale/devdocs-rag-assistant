import os
from pathlib import Path
from typing import Iterable, List
from .config import settings
from .models import IndexedChunk, ChunkMetadata

def iter_text_files(docs_dir: Path) -> Iterable[Path]:
    for root, _, files in os.walk(docs_dir):
        for name in files:
            path = Path(root) / name
            if path.suffix.lower() in {".txt", ".md"}:
                yield path

def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def simple_pdf_to_text(path: Path) -> str:
    # Optional: you can plug in PyPDF2 or pdfplumber here
    try:
        import PyPDF2
    except ImportError:
        return ""
    text_parts = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)

def iter_all_docs(docs_dir: Path) -> Iterable[tuple[str, str]]:
    for path in iter_text_files(docs_dir):
        yield str(path), load_text(path)
    # basic PDF support
    for root, _, files in os.walk(docs_dir):
        for name in files:
            path = Path(root) / name
            if path.suffix.lower() == ".pdf":
                yield str(path), simple_pdf_to_text(path)

def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    cleaned = " ".join(text.split())
    chunks: List[str] = []
    start = 0
    n = len(cleaned)
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(cleaned[start:end])
        if end == n:
            break
        start = end - overlap
    return chunks

def build_chunks() -> List[IndexedChunk]:
    chunks: List[IndexedChunk] = []
    for doc_idx, (source, text) in enumerate(iter_all_docs(settings.docs_dir)):
        if not text.strip():
            continue
        raw_chunks = chunk_text(
            text,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        for chunk_id, chunk in enumerate(raw_chunks):
            meta = ChunkMetadata(
                doc_id=f"doc-{doc_idx}",
                source=source,
                page=None,
                chunk_id=chunk_id,
            )
            chunks.append(IndexedChunk(text=chunk, metadata=meta))
    return chunks
