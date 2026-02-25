# Personal DevDocs AI Assistant 📖 🤖

## 📌 Overview
**Personal DevDocs AI Assistant** is a local **Retrieval-Augmented Generation (RAG)** application designed for developers. It allows you to chat with your own documentation (Markdown, text, and PDFs) using local embeddings and any OpenAI-compatible LLM.

RAG enhances AI responses by grounding them in your specific data, providing more accurate, up-to-date, and domain-specific answers without the need for fine-tuning.

**Key Features:**
* **Local Document Ingestion:** Scans and processes `.md`, `.txt`, and `.pdf` files from your local folders.
* **Semantic Search:** Uses `sentence-transformers` and **FAISS** for high-performance vector retrieval.
* **Modular Pipeline:** Separate layers for ingestion, embedding, vector storage, and generation.
* **Dual Interface:** Chat with your docs via a **FastAPI** backend + simple Web UI or a handy **CLI**.
* **Flexible LLM Integration:** Works with any OpenAI-compatible API (e.g., GPT-4o, llama.cpp, Ollama).

---

## 🏗 Architecture
The system follows a classic RAG lifecycle:

1.  **Indexing Phase:**
    *   **Load:** Scans `data/docs` for supported file types.
    *   **Chunk:** Splits documents into overlapping segments for better context retention.
    *   **Embed:** Computes vector embeddings using `all-MiniLM-L6-v2`.
    *   **Store:** Persists vectors in a FAISS index with JSON metadata.

2.  **Retrieval + Generation Phase:**
    *   **Retrieve:** Finds top-k most relevant chunks for a user query.
    *   **Augment:** Assembles a prompt using retrieved chunks as context.
    *   **Generate:** Calls the LLM to produce a response grounded in the context.

### Project Structure
```text
devdocs-rag-assistant/
  ├─ app/
  │   ├─ config.py          # Centralized settings and paths
  │   ├─ ingestion.py       # Document loading and chunking logic
  │   ├─ vector_store.py    # FAISS and embedding management
  │   ├─ rag_pipeline.py    # Retrieval + LLM call orchestration
  │   ├─ api.py             # FastAPI HTTP endpoints
  │   └─ cli.py             # Command-line interface
  ├─ web/
  │   ├─ index.html         # Minimal chat UI
  │   └─ main.js            # Frontend logic
  ├─ data/
  │   ├─ docs/              # Drop your .md, .txt, .pdf files here
  │   └─ index/             # Generated FAISS index + metadata
  ├─ .env.example           # Environment variable template
  └─ requirements.txt       # Python dependencies
```

## 🛠 Tech Stack
| Layer         | Purpose                                  | Main Libs/Tools                           |
|---------------|------------------------------------------|-------------------------------------------|
| **Ingestion**     | Load / parse / chunk docs                | `PyPDF2`, `python-stdlib`                 |
| **Embeddings**    | Turn text chunks into vectors            | `sentence-transformers`                   |
| **Vector Store**  | Similarity search over doc embeddings    | **FAISS** (faiss-cpu)                     |
| **Orchestration** | Wire retriever + LLM + prompt template   | Custom Python logic                       |
| **Serving**       | Expose HTTP API + simple web interface   | **FastAPI**, **Uvicorn**, HTML/JS         |

---

## 🚀 How to Run

### Prerequisites
* Python 3.9+ installed.
* An OpenAI-compatible API key (or local LLM server running).

### 1. Setup Environment
```bash
# Clone the repository and navigate to it
# (Assuming current directory is devdocs-rag-assistant)

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your LLM_API_KEY and LLM_API_BASE
```

### 2. Build the Document Index
Place your documentation files in `data/docs/`, then run:
```bash
python -m app.cli build-index
```

### 3. Start the Assistant
You can interact with the system via CLI or Web UI.

**Run CLI Query:**
```bash
python -m app.cli ask "How do I configure settings?"
```

**Launch Web UI:**
```bash
# Start the FastAPI server
python -m app.cli serve --port 8000
# Open web/index.html in your browser
```

---

## 📊 Workflow & Usage

1.  **Configuration:** Update `app/config.py` to adjust chunk size, overlap, or top-k settings.
2.  **Ingestion:** `app/ingestion.py` handles normalization and cleaning.
3.  **Prompting:** The system uses a strict "answer using only provided context" prompt to minimize hallucinations.
4.  **Citations:** The response includes sources so you know exactly where the information came from.


---
