import argparse
import uvicorn

from .ingestion import build_chunks
from .vector_store import get_vector_store
from .rag_pipeline import answer_question

def cmd_build_index():
    print("Building index...")
    chunks = build_chunks()
    store = get_vector_store()
    store.build(chunks)
    print(f"Indexed {len(chunks)} chunks.")

def cmd_ask(question: str):
    answer, metas = answer_question(question)
    print("\nAnswer:\n")
    print(answer)
    print("\nSources:")
    for m in metas:
        print(f"- {m.source} (chunk {m.chunk_id})")

def cmd_serve(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("app.api:app", host=host, port=port, reload=False)

def main():
    parser = argparse.ArgumentParser(description="DevDocs RAG Assistant")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("build-index")
    ask_p = sub.add_parser("ask")
    ask_p.add_argument("question", type=str)
    serve_p = sub.add_parser("serve")
    serve_p.add_argument("--host", type=str, default="0.0.0.0")
    serve_p.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()
    if args.command == "build-index":
        cmd_build_index()
    elif args.command == "ask":
        cmd_ask(args.question)
    elif args.command == "serve":
        cmd_serve(args.host, args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
