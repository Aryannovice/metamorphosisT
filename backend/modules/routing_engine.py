import logging
from backend.config import (
    TOKEN_THRESHOLD,
    LOCAL_MODEL,
    OPENAI_MODEL,
    GROQ_MODEL,
    MISTRAL_MODEL,
    OPENROUTER_MODEL,
)

logger = logging.getLogger(__name__)


class RoutingEngine:
    def __init__(self):
        self.token_threshold = TOKEN_THRESHOLD
        self.local_model = LOCAL_MODEL
        self.cloud_models = {
            "OPENAI": OPENAI_MODEL,
            "GROQ": GROQ_MODEL,
            "MISTRAL": MISTRAL_MODEL,
            "OPENROUTER": OPENROUTER_MODEL,
        }

    def decide(self, user_mode: str, token_count: int, cloud_provider: str = "GROQ") -> dict:
        cloud_model = self.cloud_models.get(cloud_provider, GROQ_MODEL)

        if user_mode == "STRICT":
            return {"route": "LOCAL", "model": self.local_model}

        is_lightweight = token_count < self.token_threshold

        if user_mode == "BALANCED":
            if is_lightweight:
                return {"route": "LOCAL", "model": self.local_model}
            return {"route": "CLOUD", "model": cloud_model}

        # PERFORMANCE – always prefer cloud
        return {"route": "CLOUD", "model": cloud_model}
