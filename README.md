# Agentic Data Engineering Assistant 📖 🤖

## 📌 Overview
**Agentic Data Engineering Assistant** is a hybrid **Retrieval-Augmented Generation (RAG)** system built for complex data orchestration and engineering workflows. It intelligently routes developer queries between your local, proprietary documentation and live online documentation via the Model Context Protocol (MCP).

Instead of relying solely on static indexing, the assistant acts as an autonomous agent. It can read your internal architectural playbooks (e.g., geospatial ELT design, custom stateful graphs) and pull live, programmatic optimization rules from external ecosystems like Apache Spark, Delta Lake, and Dagster.

**Key Features:**
* **Intent-Driven Routing:** An LLM-powered router classifies queries to fetch data from either the local vector store or external MCP tools.
* **MCP Tool Integration:** Connects seamlessly to external APIs to retrieve up-to-date documentation for tools like Apache Spark, Snowflake, and dbt.
* **Local Document Ingestion:** Scans and processes `.md`, `.txt`, and `.pdf` files (ideal for internal project docs and pipeline schemas).
* **Semantic Search:** Uses `sentence-transformers` and **FAISS** for high-performance, local vector retrieval.
* **Flexible LLM Orchestration:** Works with any OpenAI-compatible API (e.g., GPT-4o, llama.cpp, Ollama) using strict typed Python logic.

---

## 🏗 Architecture
The system follows an **Agentic RAG** lifecycle:

1.  **Indexing Phase (Local Knowledge):**
    *   **Load & Chunk:** Scans `data/docs` and splits files into optimized segments.
    *   **Embed & Store:** Computes vectors using `all-MiniLM-L6-v2` and persists them in a FAISS index.

2.  **Execution Phase (Agentic Routing & Generation):**
    *   **Classify:** The `QueryRouter` inspects the user query to determine the intent (`LOCAL_DOCS` vs. `ONLINE_DOCS`).
    *   **Retrieve / Execute:** 
        *   If local: Queries the FAISS index for internal documentation.
        *   If online: Triggers the appropriate `BaseMCPTool` (e.g., `SparkMCPTool`) to fetch live API definitions or configurations.
    *   **Augment & Generate:** Merges the retrieved context (from either source) into a strict prompt and generates a grounded response.

### Project Structure
```text
devdocs-rag-assistant/
  ├─ app/
  │   ├─ agent/             
  │   │   └─ router.py      # LLM intent classification
  │   ├─ mcp_tools/         
  │   │   ├─ base.py        # Abstract BaseMCPTool contract
  │   │   └─ spark_tool.py  # Apache Spark MCP connector
  │   ├─ config.py          # Centralized settings and paths
  │   ├─ ingestion.py       # Document loading and chunking logic
  │   ├─ vector_store.py    # FAISS and embedding management
  │   ├─ rag_pipeline.py    # Main execution loop and orchestration
  │   ├─ api.py             # FastAPI HTTP endpoints
  │   └─ cli.py             # Command-line interface
  ├─ web/
  │   ├─ index.html         # Minimal chat UI
  │   └─ main.js            # Frontend logic
  ├─ data/
  │   ├─ docs/              # Drop your internal pipeline playbooks here
  │   └─ index/             # Generated FAISS index + metadata
  ├─ .env.example           # Environment variable template
  └─ requirements.txt       # Python dependencies
```

## 🛠 Tech Stack
| Layer             | Purpose                                      | Main Libs/Tools                           |
|-------------------|----------------------------------------------|-------------------------------------------|
| **Routing Layer** | Query classification and intent mapping      | Custom Python, LLM API                    |
| **Tooling Layer** | Standardized external API execution          | **MCP Protocol**, `httpx`, Pydantic       |
| **Ingestion**     | Load / parse / chunk internal docs           | `PyPDF2`, `python-stdlib`                 |
| **Vector Store**  | Similarity search over local embeddings      | **FAISS** (faiss-cpu)                     |
| **Serving**       | Expose HTTP API + simple web interface       | **FastAPI**, **Uvicorn**, HTML/JS         |

---

## 🚀 How to Run

### Prerequisites
* Python 3.9+ installed.
* An OpenAI-compatible API key (or local LLM server running).

### 1. Setup Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Add your LLM_API_KEY and LLM_API_BASE to .env
```

### 2. Build the Document Index
Place your internal documentation in `data/docs/`, then run:
```bash
python -m app.cli build-index
```

### 3. Start the Assistant
**Run CLI Query:**
```bash
python -m app.cli ask "What are the optimal shuffle partitions for a 500GB Delta table?"
```

**Launch Web UI:**
```bash
python -m app.cli serve --port 8000
# Open web/index.html in your browser
```