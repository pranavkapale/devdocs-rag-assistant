from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol


class LLMClientProtocol(Protocol):
    def chat(self, messages: list[dict[str, str]]) -> str:
        ...


@dataclass(frozen=True)
class RoutingDecision:
    intent: str
    target_entity: str = ""


class QueryRouter:
    def __init__(self, llm_client: LLMClientProtocol) -> None:
        self.llm_client = llm_client

    def route(self, query: str) -> RoutingDecision:
        system_prompt: str = (
            "You are a routing classifier for a documentation assistant. "
            "Classify the user query into exactly one of these intents: "
            '"LOCAL_DOCS" for private/internal documentation, playbooks, notes, or architecture docs; '
            '"ONLINE_DOCS" for live API syntax, reference docs, or questions about external tools like Spark, Snowflake, or Dagster. '
            "If the intent is ONLINE_DOCS, include a 'target_entity' field with a short identifier such as 'spark' or 'snowflake'. "
            "Return ONLY valid JSON with keys 'intent' and optionally 'target_entity'."
        )
        user_prompt: str = (
            f"User query: {query}\n"
            'Respond with strict JSON, for example: {"intent": "LOCAL_DOCS"} or {"intent": "ONLINE_DOCS", "target_entity": "spark"}'
        )
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        raw_response: str = self.llm_client.chat(messages)
        try:
            payload: dict[str, Any] = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid JSON for routing intent.") from exc

        intent: str = str(payload.get("intent", ""))
        if intent not in {"LOCAL_DOCS", "ONLINE_DOCS"}:
            raise ValueError("LLM routing intent must be LOCAL_DOCS or ONLINE_DOCS.")
        target_entity: str = str(payload.get("target_entity", ""))
        return RoutingDecision(intent=intent, target_entity=target_entity)
