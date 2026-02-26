import logging
from typing import List, Tuple

import requests
import openai
import google.generativeai as genai

from backend.config import GEMINI_API_KEY, GROQ_API_KEY, OLLAMA_BASE_URL, GEMINI_MODEL

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class InferenceEngine:
    def __init__(self):
        self._gemini_available = bool(GEMINI_API_KEY)
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        self._gemini_model_name = GEMINI_MODEL
        self._groq = (
            openai.OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
            if GROQ_API_KEY
            else None
        )
        self._ollama_url = OLLAMA_BASE_URL
        self._ollama_available = self._check_ollama_available()
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            resp = requests.get(f"{self._ollama_url}/api/version", timeout=2)
            return resp.status_code == 200
        except:
            return False
    
    def is_ollama_available(self) -> bool:
        """Public method to check Ollama availability."""
        return self._ollama_available

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

    # ── OpenAI (cloud – backed by Gemini) ─────────────────────────────

    @staticmethod
    def _convert_messages(messages: List[dict]):
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

    def _call_openai(self, messages: List[dict], model: str) -> Tuple[str, int]:
        if not self._gemini_available:
            return (
                "[Error] No OPENAI_API_KEY configured. "
                "Set it in your .env file to use OpenAI cloud routing.",
                0,
            )
        try:
            system_instruction, contents = self._convert_messages(messages)
            requested_model = (model or self._gemini_model_name or "").strip()
            if not requested_model.lower().startswith(("gemini", "models/")):
                requested_model = self._gemini_model_name
            model_kwargs = {}
            if system_instruction:
                model_kwargs["system_instruction"] = system_instruction
            gemini_model = genai.GenerativeModel(
                requested_model,
                **model_kwargs,
            )
            resp = gemini_model.generate_content(contents)
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
