import json
import logging
from typing import Any, List, cast

import requests

from .agent.router import QueryRouter, RoutingDecision
from .config import settings
from .models import ChunkMetadata
from .mcp_tools.spark_tool import SparkMCPTool
from .vector_store import get_vector_store

logger = logging.getLogger(__name__)


class RagLLMClient:
    def chat(self, messages: list[dict[str, str]]) -> str:
        prompt: str = "\n\n".join(
            f"{message['role']}: {message['content']}" for message in messages
        )
        return call_llm(prompt)


def fetch_chunk_texts(meta_list: List[ChunkMetadata]) -> List[str]:
    texts: List[str] = []
    for meta in meta_list:
        try:
            with open(meta.source, "r", encoding="utf-8", errors="ignore") as f:
                texts.append(f.read())
        except Exception:
            texts.append("")
    return texts


def assemble_context(meta_list: List[ChunkMetadata]) -> str:
    contexts: List[str] = []
    for meta, full_text in zip(meta_list, fetch_chunk_texts(meta_list)):
        snippet: str = full_text[:1000]
        contexts.append(f"[Source: {meta.source}]\n{snippet}")
    merged: str = "\n\n".join(contexts)
    return merged[: settings.max_context_chars]


def build_prompt(question: str, context: str) -> str:
    return (
        "You are a helpful assistant for a software developer. "
        "Answer the question using only the information from the context. "
        "If the answer is not in the context, say you do not know.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )


def call_llm(prompt: str) -> str:
    url: str = f"{settings.llm_api_base}/chat/completions"
    headers: dict[str, str] = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload: dict[str, object] = {
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
    response_data: Any = resp.json()
    choices: Any = response_data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("LLM response did not include any choices")

    first_choice: Any = choices[0]
    message: Any = first_choice.get("message")
    content: Any = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str):
        raise ValueError("LLM response content was not a string")
    return content.strip()


def build_online_docs_prompt(question: str, tool_payload: dict[str, Any]) -> str:
    payload_text: str = json.dumps(tool_payload, indent=2, ensure_ascii=False)
    return (
        "You are a helpful assistant for a software developer. "
        "Use the live MCP tool output below as documentation context. "
        "Answer the user question using that information when available.\n\n"
        f"Tool payload:\n{payload_text}\n\n"
        f"Question: {question}\nAnswer:"
    )


def build_spark_tool_arguments(question: str) -> dict[str, str]:
    lowered_question: str = question.lower()
    if "memory" in lowered_question:
        return {"config_key": "spark.memory.fraction"}
    if "shuffle" in lowered_question:
        return {"config_key": "spark.sql.shuffle.partitions"}
    if "partition" in lowered_question:
        return {"config_key": "spark.sql.files.maxPartitionBytes"}
    return {"config_key": "spark.sql.adaptive.enabled"}


def answer_question(question: str) -> tuple[str, List[ChunkMetadata]]:
    router: QueryRouter = QueryRouter(RagLLMClient())
    decision: RoutingDecision = router.route(question)

    if decision.intent == "ONLINE_DOCS":
        if decision.target_entity.lower() == "spark":
            tool: SparkMCPTool = SparkMCPTool(base_url=settings.mcp_base_url)
            try:
                tool_arguments: dict[str, str] = build_spark_tool_arguments(question)
                tool_payload: dict[str, Any] = tool.execute(tool_arguments)
                prompt: str = build_online_docs_prompt(question, tool_payload)
                answer: str = call_llm(prompt)
                return answer, []
            finally:
                tool.close()

        logger.warning("MCP Tool execution pending")
        return "MCP Tool execution pending", []

    store = get_vector_store()
    if not store.is_built():
        raise RuntimeError("Index does not exist, please build it first.")
    hits = store.search(question, settings.top_k)
    metas: List[ChunkMetadata] = [m for m, _ in hits]
    context: str = assemble_context(metas)
    prompt: str = build_prompt(question, context)
    answer: str = call_llm(prompt)
    return answer, metas
