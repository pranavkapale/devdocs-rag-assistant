from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

import httpx


class BaseMCPTool(ABC):
    """Abstract base class for MCP-backed documentation tools."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url: str = base_url
        self.timeout: float = timeout
        self.client: httpx.Client = httpx.Client(timeout=timeout)

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the unique identifier for the MCP tool."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Returns a detailed description of what the tool does for the LLM context."""

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the tool's core logic and returns a structured payload."""

    def close(self) -> None:
        """Closes the underlying HTTP client session safely."""
        self.client.close()