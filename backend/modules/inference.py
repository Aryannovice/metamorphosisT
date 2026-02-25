import logging
from typing import List, Tuple

import requests
import openai

from backend.config import OPENAI_API_KEY, GROQ_API_KEY, OLLAMA_BASE_URL

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class InferenceEngine:
    def __init__(self):
        self._openai = (
            openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        )
        self._groq = (
            openai.OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
            if GROQ_API_KEY
            else None
        )
        self._ollama_url = OLLAMA_BASE_URL

    def run(
        self,
        messages: List[dict],
        route: str,
        model: str,
        cloud_provider: str = "GROQ",
    ) -> Tuple[str, int]:
        if route == "LOCAL":
            return self._call_ollama(messages, model)
        if cloud_provider == "GROQ":
            return self._call_groq(messages, model)
        return self._call_openai(messages, model)

    # ── Ollama (local SLM) ──────────────────────────────────────────

    def _call_ollama(self, messages: List[dict], model: str) -> Tuple[str, int]:
        try:
            resp = requests.post(
                f"{self._ollama_url}/api/chat",
                json={"model": model, "messages": messages, "stream": False},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data.get("message", {}).get("content", "")
            tokens = data.get("eval_count", 0)
            return content, tokens
        except requests.ConnectionError:
            logger.error("Ollama is not reachable at %s", self._ollama_url)
            return (
                "[Error] Local model unavailable — Ollama is not running. "
                "Start it with `ollama serve` and pull a model.",
                0,
            )
        except Exception as exc:
            logger.exception("Ollama inference failed")
            return f"[Error] Local inference failed: {exc}", 0

    # ── Groq (cloud, free tier) ─────────────────────────────────────

    def _call_groq(self, messages: List[dict], model: str) -> Tuple[str, int]:
        if not self._groq:
            return (
                "[Error] No GROQ_API_KEY configured. "
                "Get a free key at console.groq.com/keys and add it to .env",
                0,
            )
        try:
            resp = self._groq.chat.completions.create(
                model=model,
                messages=messages,
            )
            content = resp.choices[0].message.content or ""
            tokens = resp.usage.total_tokens if resp.usage else 0
            return content, tokens
        except Exception as exc:
            logger.exception("Groq inference failed")
            return f"[Error] Groq inference failed: {exc}", 0

    # ── OpenAI (cloud) ──────────────────────────────────────────────

    def _call_openai(self, messages: List[dict], model: str) -> Tuple[str, int]:
        if not self._openai:
            return (
                "[Error] No OPENAI_API_KEY configured. "
                "Set it in your .env file to use OpenAI cloud routing.",
                0,
            )
        try:
            resp = self._openai.chat.completions.create(
                model=model,
                messages=messages,
            )
            content = resp.choices[0].message.content or ""
            tokens = resp.usage.total_tokens if resp.usage else 0
            return content, tokens
        except Exception as exc:
            logger.exception("OpenAI inference failed")
            return f"[Error] OpenAI inference failed: {exc}", 0
