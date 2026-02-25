"""
Output Guardrails — safety check on model response before returning.
Detects leaked instructions, harmful content, and policy violations.
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Patterns indicating leaked system prompt or internal instructions
_LEAK_PATTERNS = [
    r"as an AI (assistant|language model)",
    r"I (am|cannot|can't) (provide|assist|help) with",
    r"OpenAI|Anthropic|Claude|GPT[- ]?\d",
    r"my (instructions|guidelines|programming) (say|state|require)",
    r"according to my (system|training) (prompt|instructions)",
    r"I'm (sorry|unable).*(policy|guidelines|safety)",
]

# Harmful content in output
_OUTPUT_HARMFUL_PATTERNS = [
    r"how\s+to\s+(build|make|create)\s+(a\s+)?(bomb|explosive|weapon)",
    r"step\s+by\s+step.*(kill|murder|harm)",
    r"child\s+(porn|sexual|abuse)",
    r"detailed\s+instructions\s+for\s+(violence|self-harm)",
]


class OutputGuardrails:
    """Validates model output before returning to user."""

    def __init__(self):
        self._leak_re = [re.compile(p, re.IGNORECASE) for p in _LEAK_PATTERNS]
        self._harmful_re = [
            re.compile(p, re.IGNORECASE) for p in _OUTPUT_HARMFUL_PATTERNS
        ]

    def check(self, response: str) -> Tuple[bool, str, Dict]:
        """
        Run output guardrails. Returns (passed, sanitized_or_block_reason, metadata).
        If passed=False, we return a generic safe message instead of the raw response.
        """
        metadata: Dict = {
            "leak_detected": False,
            "harmful_detected": False,
            "sanitized": False,
        }

        # Skip check for error messages (they don't come from the model)
        if response.strip().startswith("[Error]"):
            return True, response, metadata

        # 1. Leak detection — often benign (model saying "I'm an AI"), log but don't block
        for pattern in self._leak_re:
            if pattern.search(response):
                metadata["leak_detected"] = True
                # Don't block on leak — just flag. Many models say "I'm an AI assistant"
                break

        # 2. Harmful content detection — block and replace
        for pattern in self._harmful_re:
            if pattern.search(response):
                metadata["harmful_detected"] = True
                return (
                    False,
                    "The model's response was filtered for safety. Please try a different prompt.",
                    metadata,
                )

        return True, response, metadata
