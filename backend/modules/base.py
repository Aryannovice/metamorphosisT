"""
Abstraction layer — base classes for swappable pipeline modules.
Any implementation can be swapped without changing the orchestrator.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class InputGuard(ABC):
    """Abstract base for input-level guards (PII, injection, toxicity)."""

    @abstractmethod
    def process(self, text: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Process input; return (processed_text, metadata)."""
        pass


class OutputGuard(ABC):
    """Abstract base for output-level guards (safety, policy)."""

    @abstractmethod
    def check(self, text: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check output; return (pass, message). If pass=False, message explains why."""
        pass


class MemoryStore(ABC):
    """Abstract base for memory/context retrieval."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> List[str]:
        pass

    @abstractmethod
    def store(self, text: str, doc_id: str, metadata: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class InferenceProvider(ABC):
    """Abstract base for inference backends (Ollama, OpenAI, Groq, etc.)."""

    @abstractmethod
    def run(
        self,
        messages: List[dict],
        model: str,
        **kwargs,
    ) -> Tuple[str, int]:
        """Return (content, usage_tokens)."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class RateLimiterBackend(ABC):
    """Abstract base for rate limiting backends (in-memory, Redis, etc.)."""

    @abstractmethod
    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """Return (allowed, retry_after_seconds)."""
        pass

    @abstractmethod
    def record(self, key: str) -> None:
        """Record a request for the given key."""
        pass
