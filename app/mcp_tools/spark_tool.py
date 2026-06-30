from __future__ import annotations

from typing import Any, Dict

from app.mcp_tools.base import BaseMCPTool


class SparkMCPTool(BaseMCPTool):
    """MCP tool for retrieving live Apache Spark documentation details."""

    @property
    def name(self) -> str:
        return "spark_doc_lookup"

    @property
    def description(self) -> str:
        return (
            "Look up official Apache Spark configuration properties, tuning parameters, "
            "and programmatic optimization rules (for example Adaptive Query Execution and memory management)."
        )

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        config_key: Any = arguments.get("config_key")
        if not config_key:
            return {"status": "error", "message": "Missing required argument: 'config_key'"}

        try:
            endpoint: str = f"{self.base_url}/api/v1/spark/config/{config_key}"
            response = self.client.get(endpoint)

            if response.status_code == 404:
                return {
                    "status": "not_found",
                    "message": f"Configuration '{config_key}' not found in live Spark documentation.",
                }

            response.raise_for_status()
            return {"status": "success", "data": response.json()}

        except Exception as exc:  # pragma: no cover - defensive fallback
            return {
                "status": "error",
                "message": f"Failed to retrieve Spark documentation via MCP: {str(exc)}",
            }