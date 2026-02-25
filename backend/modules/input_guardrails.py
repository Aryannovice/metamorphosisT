"""
Input Guardrails — prompt injection detection + toxicity filter.
Runs before PII Guard in the pipeline.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Common prompt injection / jailbreak patterns (case-insensitive)
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"forget\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"you\s+are\s+now\s+(in\s+)?(a\s+)?(different\s+)?(mode|model|persona)",
    r"pretend\s+(you\s+are|to\s+be)\s+",
    r"act\s+as\s+if\s+you\s+(are|were)\s+",
    r"system\s*:\s*",
    r"\[\[INST\]\]",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"human\s*:\s*.*\s*assistant\s*:\s*",
    r"override\s+(your|the)\s+(instructions|safety|rules)",
    r"bypass\s+(your|the)\s+(restrictions|safety|content\s+policy)",
    r"jailbreak",
    r"\.env\s*[=:]",
    r"sudo\s+",
    r"rm\s+-rf",
    r"eval\s*\(",
]

# Toxicity / harmful content blocklist (word-level, case-insensitive)
_TOXICITY_BLOCKLIST: List[str] = [
    # Violence
    "kill yourself", "kys", "commit suicide", "self-harm",
    "bomb instructions", "make explosives", "build a bomb",
    "how to hurt", "how to harm", "how to murder",
    # Hate
    "race war", "ethnic cleansing", "genocide of",
    # CSAM / illegal
    "child porn", "child sexual", "underage",
    # Extremely explicit (not exhaustive)
    "detailed sex with minors", "sexual abuse of children",
]


class InputGuardrails:
    """Detects prompt injection attempts and toxic/harmful input."""

    def __init__(self, injection_patterns: Optional[List[str]] = None):
        self._injection_re = [
            re.compile(p, re.IGNORECASE) for p in (injection_patterns or _INJECTION_PATTERNS)
        ]
        self._toxic_phrases = [p.lower() for p in _TOXICITY_BLOCKLIST]

    def check(self, prompt: str) -> Tuple[bool, str, Dict]:
        """
        Run input guardrails. Returns (passed, block_reason, metadata).
        If passed=False, block_reason explains why the prompt was blocked.
        """
        metadata: Dict = {
            "injection_detected": False,
            "injection_match": None,
            "toxicity_detected": False,
            "toxicity_match": None,
        }

        # 1. Prompt injection check
        prompt_lower = prompt.lower()
        for pattern in self._injection_re:
            if pattern.search(prompt):
                metadata["injection_detected"] = True
                metadata["injection_match"] = pattern.pattern[:50]
                return (
                    False,
                    "Prompt appears to contain manipulation or jailbreak attempts. Please rephrase your request.",
                    metadata,
                )

        # 2. Toxicity / harmful content check
        for phrase in self._toxic_phrases:
            if phrase in prompt_lower:
                metadata["toxicity_detected"] = True
                metadata["toxicity_match"] = phrase
                return (
                    False,
                    "Your request contains content that violates our safety policy.",
                    metadata,
                )

        return True, "", metadata
