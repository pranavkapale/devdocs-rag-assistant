from __future__ import annotations

from typing import Any

from app.agent.router import QueryRouter
from app.rag_pipeline import answer_question


class DummyLLMClient:
    def __init__(self, response: str) -> None:
        self.response = response

    def chat(self, messages: list[dict[str, str]]) -> str:
        return self.response


class DummyStore:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def is_built(self) -> bool:
        return True

    def search(self, query: str, k: int) -> list[tuple[Any, float]]:
        self.calls.append(query)
        return []


def test_query_router_returns_strict_json_structure(monkeypatch: Any) -> None:
    class StrictLLM(DummyLLMClient):
        def chat(self, messages: list[dict[str, str]]) -> str:
            return '{"intent": "LOCAL_DOCS"}'

    router = QueryRouter(StrictLLM('{"intent": "LOCAL_DOCS"}'))
    result = router.route("How should I structure my docs?")

    assert result.intent == "LOCAL_DOCS"
    assert result.target_entity == ""


def test_answer_question_routes_online_queries_to_mock_response(monkeypatch: Any) -> None:
    store = DummyStore()

    class DummySparkTool:
        def __init__(self, base_url: str) -> None:
            self.base_url = base_url

        def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
            return {"status": "success", "data": {"config_key": arguments["config_key"]}}

        def close(self) -> None:
            return None

    monkeypatch.setattr("app.rag_pipeline.get_vector_store", lambda: store)
    monkeypatch.setattr("app.rag_pipeline.call_llm", lambda prompt: "Spark docs context answer")
    monkeypatch.setattr("app.rag_pipeline.SparkMCPTool", DummySparkTool)

    router = QueryRouter(DummyLLMClient('{"intent": "ONLINE_DOCS", "target_entity": "spark"}'))
    monkeypatch.setattr("app.rag_pipeline.QueryRouter", lambda llm_client: router)

    answer, metas = answer_question("How do I use Spark SQL?")

    assert answer == "Spark docs context answer"
    assert metas == []
    assert store.calls == []
