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

import json
import requests
import openai

import google.generativeai as genai

from backend.config import (
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GEMINI_API_KEY,
    MISTRAL_API_KEY,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    OPENROUTER_SITE_URL,
    OPENROUTER_APP_NAME,
    OLLAMA_BASE_URL,
    LOCAL_MODEL,
    OPENAI_MODEL,
    GROQ_MODEL,
    GEMINI_MODEL,
    MISTRAL_MODEL,
    MISTRAL_BASE_URL,
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
    Cloud inference provider branded as OpenAI, backed by Google Gemini.

    Requires GEMINI_API_KEY configuration.
    """

    name = "openai"

    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self._api_key = api_key
        self._model = model
        self._available = bool(api_key)
        if api_key:
            genai.configure(api_key=api_key)

    def get_model(self) -> str:
        return self._model

    def is_available(self) -> bool:
        return self._available

    @staticmethod
    def _convert_messages(messages: List[dict]):
        """Convert OpenAI-style messages to Gemini format.

        Returns (system_instruction, contents) where *contents* is a list of
        ``{"role": role, "parts": [text]}`` dicts understood by Gemini.
        """
        system_parts: List[str] = []
        contents: List[dict] = []

        for msg in messages:
            role = msg.get("role", "user")
            text = msg.get("content", "")
            if role == "system":
                system_parts.append(text)
            else:
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({"role": gemini_role, "parts": [text]})

        system_instruction = "\n".join(system_parts) if system_parts else None
        return system_instruction, contents

    def infer(self, request: MCPRequest) -> Tuple[str, int]:
        """Execute inference via Gemini API (presented externally as OpenAI)."""
        if not self._available:
            return (
                "[Error] No OPENAI_API_KEY configured. "
                "Set it in your .env file to use OpenAI cloud routing.",
                0,
            )

        messages = request.compressed_messages or request.messages
        system_instruction, contents = self._convert_messages(messages)

        try:
            requested_model = (request.model or self._model or "").strip()
            # Pipeline may still pass an OpenAI model name (e.g. gpt-3.5-turbo).
            # Since this provider is Gemini-backed, coerce non-Gemini identifiers
            # to the configured Gemini model.
            if not requested_model.lower().startswith(("gemini", "models/")):
                requested_model = self._model

            model_kwargs = {}
            if system_instruction:
                model_kwargs["system_instruction"] = system_instruction

            model = genai.GenerativeModel(
                requested_model,
                **model_kwargs,
            )
            resp = model.generate_content(contents)
            content = resp.text or ""
            tokens = 0
            if resp.usage_metadata:
                tokens = (
                    getattr(resp.usage_metadata, "total_token_count", 0)
                    or (
                        getattr(resp.usage_metadata, "prompt_token_count", 0)
                        + getattr(resp.usage_metadata, "candidates_token_count", 0)
                    )
                )
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


class MistralProvider(MCPProvider):
    """
    Mistral cloud inference provider.

    Uses Mistral's OpenAI-compatible chat completions API.
    Requires MISTRAL_API_KEY configuration.
    """

    name = "mistral"

    def __init__(
        self,
        api_key: str = MISTRAL_API_KEY,
        model: str = MISTRAL_MODEL,
        base_url: str = MISTRAL_BASE_URL,
    ):
        self._api_key = api_key
        self._model = model
        self._base_url = (base_url or "https://api.mistral.ai/v1").rstrip("/")

    def get_model(self) -> str:
        return self._model

    def is_available(self) -> bool:
        return bool(self._api_key)

    @staticmethod
    def _normalize_content(content) -> str:
        """
        Mistral may return `message.content` as a string *or* a structured
        list of content blocks. Normalize it to plain text for the gateway UI.
        """
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if item is None:
                    continue
                if isinstance(item, str):
                    parts.append(item)
                    continue
                if isinstance(item, dict):
                    if item.get("type") == "text" and item.get("text") is not None:
                        parts.append(str(item.get("text")))
                    elif item.get("text") is not None:
                        parts.append(str(item.get("text")))
                    elif item.get("content") is not None:
                        parts.append(str(item.get("content")))
                    else:
                        parts.append(json.dumps(item, ensure_ascii=False))
                    continue
                parts.append(str(item))
            return "".join(parts).strip()
        if isinstance(content, dict):
            if content.get("type") == "text" and content.get("text") is not None:
                return str(content.get("text"))
            if content.get("text") is not None:
                return str(content.get("text"))
            if content.get("content") is not None:
                return str(content.get("content"))
            return json.dumps(content, ensure_ascii=False)
        return str(content)

    def infer(self, request: MCPRequest) -> Tuple[str, int]:
        if not self._api_key:
            return (
                "[Error] No MISTRAL_API_KEY configured. "
                "Set it in your .env file to use Mistral cloud routing.",
                0,
            )

        messages = request.compressed_messages or request.messages
        model = (request.model or self._model or "").strip() or self._model

        try:
            resp = requests.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                },
                timeout=120,
            )
            if resp.status_code >= 400:
                # Try to surface a useful error message
                try:
                    err = resp.json()
                except Exception:
                    err = {"error": {"message": resp.text}}
                msg = (
                    (err.get("error") or {}).get("message")
                    or err.get("message")
                    or f"HTTP {resp.status_code}"
                )
                return f"[Error] Mistral inference failed: {msg}", 0

            data = resp.json()
            message = ((data.get("choices") or [{}])[0].get("message") or {})
            content = self._normalize_content(message.get("content"))

            # If the model responded with tool calls and no user-facing content,
            # expose the tool call payload as text so the UI doesn't show [object Object].
            if not content and message.get("tool_calls") is not None:
                content = json.dumps(message.get("tool_calls"), ensure_ascii=False)

            usage = data.get("usage") or {}
            tokens = usage.get("total_tokens") or (
                (usage.get("prompt_tokens") or 0) + (usage.get("completion_tokens") or 0)
            )
            return content, int(tokens or 0)

        except Exception as exc:
            logger.exception("Mistral inference failed")
            return f"[Error] Mistral inference failed: {exc}", 0


class OpenRouterProvider(MCPProvider):
    """
    OpenRouter cloud inference provider.

    OpenRouter is OpenAI-compatible; use it to access models (including Mistral)
    via a single endpoint.
    """

    name = "openrouter"

    def __init__(
        self,
        api_key: str = OPENROUTER_API_KEY,
        base_url: str = OPENROUTER_BASE_URL,
        default_model: str = OPENROUTER_MODEL,
        site_url: str = OPENROUTER_SITE_URL,
        app_name: str = OPENROUTER_APP_NAME,
    ):
        self._client = (
            openai.OpenAI(
                api_key=api_key,
                base_url=base_url,
                default_headers={
                    # Optional attribution headers (safe to omit if empty)
                    **({"HTTP-Referer": site_url} if site_url else {}),
                    **({"X-Title": app_name} if app_name else {}),
                },
            )
            if api_key
            else None
        )
        self._default_model = default_model

    def get_model(self) -> str:
        return self._default_model

    def is_available(self) -> bool:
        return self._client is not None

    def infer(self, request: MCPRequest) -> Tuple[str, int]:
        if not self._client:
            return (
                "[Error] No OPENROUTER_API_KEY configured. "
                "Set it in your .env file to use OpenRouter cloud routing.",
                0,
            )

        messages = request.compressed_messages or request.messages
        model = (request.model or self._default_model or "").strip() or self._default_model

        try:
            resp = self._client.chat.completions.create(
                model=model,
                messages=messages,
            )
            content = resp.choices[0].message.content or ""
            tokens = resp.usage.total_tokens if resp.usage else 0
            return content, tokens

        except Exception as exc:
            logger.exception("OpenRouter inference failed")
            return f"[Error] OpenRouter inference failed: {exc}", 0


class ProviderRegistry:
    """
    Registry for dynamic provider selection.
    
    Enables runtime provider lookup based on routing decisions
    while supporting failover between providers.
    """
    
    def __init__(self):
        self._providers: Dict[str, MCPProvider] = {}
        self._fallback_order = ["local", "groq", "mistral", "openrouter", "openai"]
    
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
    registry.register(MistralProvider())
    registry.register(OpenRouterProvider())
    return registry


provider_registry = create_provider_registry()
