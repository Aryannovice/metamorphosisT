import re
import logging
from typing import Dict, Tuple

# Optional spacy import
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False

from backend.config import SPACY_MODEL

logger = logging.getLogger(__name__)

_REGEX_PATTERNS: Dict[str, str] = {
    "EMAIL": r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
    "PHONE": r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "CREDIT_CARD": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}

_SPACY_LABEL_MAP = {
    "PERSON": "NAME",
    "ORG": "ORG",
    "GPE": "LOCATION",
}


class PIIGuard:
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                # Only keep the NER pipe — tagger/parser/lemmatizer etc. are unused
                # and add significant per-call overhead.
                self.nlp = spacy.load(
                    SPACY_MODEL,
                    exclude=["tagger", "parser", "senter", "attribute_ruler", "lemmatizer"],
                )
            except OSError:
                logger.warning(
                    "spaCy model '%s' not found – falling back to regex-only PII detection. "
                    "Run:  python -m spacy download %s",
                    SPACY_MODEL,
                    SPACY_MODEL,
                )
                self.nlp = None
        else:
            logger.warning("spaCy not installed – using regex-only PII detection")
        self._redaction_store: Dict[str, Dict[str, str]] = {}

    def mask(self, text: str, request_id: str) -> Tuple[str, Dict]:
        redaction_map: Dict[str, str] = {}
        counters: Dict[str, int] = {}
        masked = text

        # Regex pass
        for entity_type, pattern in _REGEX_PATTERNS.items():
            for match in re.finditer(pattern, masked):
                original = match.group()
                if original in redaction_map.values():
                    continue
                count = counters.get(entity_type, 0) + 1
                counters[entity_type] = count
                placeholder = f"<{entity_type}_{count}>"
                redaction_map[placeholder] = original
                masked = masked.replace(original, placeholder, 1)

        # spaCy NER pass
        if self.nlp:
            doc = self.nlp(masked)
            for ent in doc.ents:
                mapped_type = _SPACY_LABEL_MAP.get(ent.label_)
                if not mapped_type:
                    continue
                if ent.text.startswith("<") and ent.text.endswith(">"):
                    continue
                count = counters.get(mapped_type, 0) + 1
                counters[mapped_type] = count
                placeholder = f"<{mapped_type}_{count}>"
                redaction_map[placeholder] = ent.text
                masked = masked.replace(ent.text, placeholder, 1)

        self._redaction_store[request_id] = redaction_map

        return masked, {
            "redaction_count": len(redaction_map),
            "redaction_types": dict(counters),
            "redaction_map": redaction_map,
        }

    def unmask(self, text: str, request_id: str) -> str:
        redaction_map = self._redaction_store.get(request_id, {})
        result = text
        for placeholder, original in redaction_map.items():
            result = result.replace(placeholder, original)
        return result

    def clear(self, request_id: str) -> None:
        self._redaction_store.pop(request_id, None)
