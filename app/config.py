import os
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass
class Settings:
    docs_dir: Path = BASE_DIR / "data" / "docs"
    index_dir: Path = BASE_DIR / "data" / "index"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    # LLM: any OpenAI-compatible chat endpoint
    llm_api_base: str = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    top_k: int = 5
    chunk_size: int = 800
    chunk_overlap: int = 200
    max_context_chars: int = 6000

settings = Settings()
