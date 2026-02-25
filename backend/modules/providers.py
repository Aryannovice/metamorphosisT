"""
MCP Provider Abstraction Layer

Provides abstract base class and concrete implementations for:
- LocalProvider (Ollama with Llama 3.2)
- OpenAIProvider
- GroqProvider

Uses provider_registry for dynamic selection based on routing decisions.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Type

import requests
import openai

from backend.config import (
    OPENAI_API_KEY,
    GROQ_API_KEY,
    OLLAMA_BASE_URL,
    LOCAL_MODEL,
    OPENAI_MODEL,
    GROQ_MODEL,
)
from backend.models.mcp_contracts import MCPRequest

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class MCPProvider(ABC):
    """
    Abstract base class for MCP-compliant inference providers.
    
    All providers must implement the infer method that takes an MCPRequest
    and returns the response content and token usage.
    """
    
    name: str = "base"
    
    @abstractmethod
    def infer(self, request: MCPRequest) -> Tuple[str, int]:
        """
        Execute inference using this provider.
        
        Args:
            request: MCPRequest containing messages and configuration
            
        Returns:
            Tuple of (response_content, tokens_used)
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is currently available."""
        pass
    
    def get_model(self) -> str:
        """Return the model identifier for this provider."""
        return ""


class LocalProvider(MCPProvider):
    """
    Ollama-based local inference provider using Llama 3.2.
    
    Provides maximum privacy by keeping inference on-premises.
    """
    
    name = "local"
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = LOCAL_MODEL):
        self._base_url = base_url
        self._model = model
    
    def get_model(self) -> str:
        return self._model
    
    def is_available(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            resp = requests.get(f"{self._base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
    
    def infer(self, request: MCPRequest) -> Tuple[str, int]:
        """Execute local inference via Ollama."""
        messages = request.compressed_messages or request.messages
        
        try:
            resp = requests.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": request.model or self._model,
                    "messages": messages,
                    "stream": False,
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data.get("message", {}).get("content", "")
            tokens = data.get("eval_count", 0)
            return content, tokens
            
        except requests.ConnectionError:
            logger.error("Ollama is not reachable at %s", self._base_url)
            return (
                "[Error] Local model unavailable — Ollama is not running. "
                "Start it with `ollama serve` and pull a model.",
                0,
            )
        except Exception as exc:
            logger.exception("Ollama inference failed")
            return f"[Error] Local inference failed: {exc}", 0


class OpenAIProvider(MCPProvider):
    """
    OpenAI cloud inference provider.
    
    Requires OPENAI_API_KEY configuration.
    """
    
    name = "openai"
    
    def __init__(self, api_key: str = OPENAI_API_KEY, model: str = OPENAI_MODEL):
        self._client = openai.OpenAI(api_key=api_key) if api_key else None
        self._model = model
    
    def get_model(self) -> str:
        return self._model
    
    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return self._client is not None
    
    def infer(self, request: MCPRequest) -> Tuple[str, int]:
        """Execute inference via OpenAI API."""
        if not self._client:
            return (
                "[Error] No OPENAI_API_KEY configured. "
                "Set it in your .env file to use OpenAI cloud routing.",
                0,
            )
        
        messages = request.compressed_messages or request.messages
        
        try:
            resp = self._client.chat.completions.create(
                model=request.model or self._model,
                messages=messages,
            )
            content = resp.choices[0].message.content or ""
            tokens = resp.usage.total_tokens if resp.usage else 0
            return content, tokens
            
        except Exception as exc:
            logger.exception("OpenAI inference failed")
            return f"[Error] OpenAI inference failed: {exc}", 0


class GroqProvider(MCPProvider):
    """
    Groq cloud inference provider (fast inference, free tier available).
    
    Requires GROQ_API_KEY configuration.
    """
    
    name = "groq"
    
    def __init__(self, api_key: str = GROQ_API_KEY, model: str = GROQ_MODEL):
        self._client = (
            openai.OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
            if api_key
            else None
        )
        self._model = model
    
    def get_model(self) -> str:
        return self._model
    
    def is_available(self) -> bool:
        """Check if Groq API key is configured."""
        return self._client is not None
    
    def infer(self, request: MCPRequest) -> Tuple[str, int]:
        """Execute inference via Groq API."""
        if not self._client:
            return (
                "[Error] No GROQ_API_KEY configured. "
                "Get a free key at console.groq.com/keys and add it to .env",
                0,
            )
        
        messages = request.compressed_messages or request.messages
        
        try:
            resp = self._client.chat.completions.create(
                model=request.model or self._model,
                messages=messages,
            )
            content = resp.choices[0].message.content or ""
            tokens = resp.usage.total_tokens if resp.usage else 0
            return content, tokens
            
        except Exception as exc:
            logger.exception("Groq inference failed")
            return f"[Error] Groq inference failed: {exc}", 0


class ProviderRegistry:
    """
    Registry for dynamic provider selection.
    
    Enables runtime provider lookup based on routing decisions
    while supporting failover between providers.
    """
    
    def __init__(self):
        self._providers: Dict[str, MCPProvider] = {}
        self._fallback_order = ["local", "groq", "openai"]
    
    def register(self, provider: MCPProvider) -> None:
        """Register a provider instance."""
        self._providers[provider.name.lower()] = provider
    
    def get(self, name: str) -> Optional[MCPProvider]:
        """Get a provider by name."""
        return self._providers.get(name.lower())
    
    def get_for_route(self, route: str, cloud_provider: str = "groq") -> Optional[MCPProvider]:
        """
        Get appropriate provider based on route decision.
        
        Args:
            route: "LOCAL" or "CLOUD"
            cloud_provider: Which cloud provider to use if route is CLOUD
            
        Returns:
            The appropriate provider instance or None
        """
        if route.upper() == "LOCAL":
            return self.get("local")
        return self.get(cloud_provider.lower())
    
    def get_fallback(
        self,
        current: str,
        policy_whitelist: Optional[List[str]] = None
    ) -> Optional[MCPProvider]:
        """
        Get next available fallback provider.
        
        Args:
            current: Current provider name that failed
            policy_whitelist: List of allowed providers from policy
            
        Returns:
            Next available provider or None
        """
        whitelist = policy_whitelist or self._fallback_order
        current_idx = -1
        
        for i, name in enumerate(self._fallback_order):
            if name.lower() == current.lower():
                current_idx = i
                break
        
        # Try providers after current in fallback order
        for name in self._fallback_order[current_idx + 1:]:
            if name.lower() in [w.lower() for w in whitelist]:
                provider = self.get(name)
                if provider and provider.is_available():
                    return provider
        
        return None
    
    def list_available(self) -> List[str]:
        """List all available (configured) providers."""
        return [
            name for name, provider in self._providers.items()
            if provider.is_available()
        ]


# ── Global registry instance ────────────────────────────────────────

def create_provider_registry() -> ProviderRegistry:
    """Create and populate the global provider registry."""
    registry = ProviderRegistry()
    registry.register(LocalProvider())
    registry.register(OpenAIProvider())
    registry.register(GroqProvider())
    return registry


provider_registry = create_provider_registry()
