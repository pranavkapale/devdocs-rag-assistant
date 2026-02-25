from pydantic import BaseModel
from typing import List, Optional

class ChunkMetadata(BaseModel):
    doc_id: str
    source: str
    page: Optional[int] = None
    chunk_id: int

class IndexedChunk(BaseModel):
    text: str
    metadata: ChunkMetadata

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: List[ChunkMetadata]
