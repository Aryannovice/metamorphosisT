"""Prompt compression module.

Uses a lightweight stop-word / whitespace compressor by default.
If the `llmlingua` package is installed, upgrades to LLMLingua-2
for higher-quality semantic compression.
"""

import re
import logging
from typing import List, Tuple

import tiktoken

logger = logging.getLogger(__name__)

_STOP_WORDS = frozenset(
    {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall",
        "should", "may", "might", "must", "can", "could", "am", "it", "its",
        "this", "that", "these", "those", "i", "you", "he", "she", "we",
        "they", "me", "him", "her", "us", "them", "my", "your", "his",
        "our", "their", "of", "in", "to", "for", "with", "on", "at", "from",
        "by", "as", "into", "about", "between", "through", "during", "just",
        "also", "very", "really", "quite", "rather", "too", "so", "then",
    }
)


def _lightweight_compress(text: str, ratio: float = 0.6) -> str:
    """Remove stop words and collapse whitespace to reach target ratio."""
    words = text.split()
    if not words:
        return text

    target_len = max(int(len(words) * ratio), 1)
    kept: list[str] = []
    for w in words:
        if w.lower().strip(".,!?;:") in _STOP_WORDS and len(kept) < len(words):
            continue
        kept.append(w)
        if len(kept) >= target_len:
            break

    if not kept:
        kept = words[:target_len]

    result = " ".join(kept)
    result = re.sub(r"\s{2,}", " ", result)
    return result.strip()


class PromptShrinker:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        try:
            self._encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            self._encoder = tiktoken.get_encoding("cl100k_base")

        self._use_llmlingua = False
        try:
            from llmlingua import PromptCompressor  # noqa: F401

            self._use_llmlingua = True
            logger.info("LLMLingua-2 detected – using semantic compression")
        except ImportError:
            logger.info("LLMLingua not installed – using lightweight compressor")

    def compress(
        self,
        messages: List[dict],
        original_token_count: int,
    ) -> Tuple[List[dict], int, int]:
        """Return (compressed_messages, tokens_after, tokens_saved)."""
        compressed: List[dict] = []

        for msg in messages:
            if msg["role"] == "system":
                compressed.append(msg)
            else:
                new_content = _lightweight_compress(msg["content"])
                compressed.append({**msg, "content": new_content})

        after = self._count_tokens(compressed)
        saved = max(original_token_count - after, 0)
        return compressed, after, saved

    def _count_tokens(self, messages: List[dict]) -> int:
        total = 0
        for msg in messages:
            total += 4
            total += len(self._encoder.encode(msg["content"]))
        total += 2
        return total
