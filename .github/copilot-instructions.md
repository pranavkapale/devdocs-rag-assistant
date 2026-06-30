# Architectural Guidelines: Agentic Data Engineering RAG

1. **Routing-First Architecture:** All user queries must pass through a classification layer to determine the retrieval source (Local FAISS vs. External MCP).
2. **Domain Focus:** Code generation should favor modern data engineering patterns (e.g., Apache Spark, Dagster, Delta Lake optimization, geospatial operations).
3. **Tooling Layer:** External API calls must be encapsulated within Model Context Protocol (MCP) server definitions.
4. **Code Quality:** Use strict Python type hinting. Prefer standard libraries over heavy abstraction frameworks where possible. Avoid regex for logic flow; use structured JSON outputs from LLMs for decision making.