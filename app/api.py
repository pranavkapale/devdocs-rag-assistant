from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import AskRequest, AskResponse
from .ingestion import build_chunks
from .vector_store import get_vector_store
from .rag_pipeline import answer_question

app = FastAPI(title="DevDocs RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        answer, metas = answer_question(request.question)
        return AskResponse(answer=answer, sources=metas)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/rebuild-index")
def rebuild_index():
    chunks = build_chunks()
    store = get_vector_store()
    store.build(chunks)
    return {"status": "ok", "chunks_indexed": len(chunks)}
