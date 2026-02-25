from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum


class UserMode(str, Enum):
    STRICT = "STRICT"
    BALANCED = "BALANCED"
    PERFORMANCE = "PERFORMANCE"


class CloudProvider(str, Enum):
    GROQ = "GROQ"
    OPENAI = "OPENAI"


# ── Request / Response ──────────────────────────────────────────────

class GatewayRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    mode: UserMode = UserMode.BALANCED
    cloud_provider: CloudProvider = CloudProvider.GROQ


class TokenStats(BaseModel):
    original: int = 0
    compressed: int = 0
    saved: int = 0
    compression_ratio: float = 0.0


class LatencyStats(BaseModel):
    input_guardrails_ms: float = 0.0
    pii_ms: float = 0.0
    memory_ms: float = 0.0
    compression_ms: float = 0.0
    inference_ms: float = 0.0
    output_guardrails_ms: float = 0.0
    total_ms: float = 0.0


class GuardrailInfo(BaseModel):
    input_blocked: bool = False
    output_filtered: bool = False
    input_reason: str = ""
    output_reason: str = ""


class RedactionInfo(BaseModel):
    count: int = 0
    types: Dict[str, int] = {}


class DataHavenVerification(BaseModel):
    """Cryptographic verification proof from DataHaven."""
    verified: bool = False
    log_id: str = ""
    content_hash: str = ""
    merkle_leaf: str = ""
    merkle_root: str = ""
    signature: str = ""
    algorithm: str = ""
    chain: str = ""
    timestamp: str = ""
    status: str = "pending"


class GatewayResponse(BaseModel):
    request_id: str
    response: str
    route: str
    model_used: str
    token_stats: TokenStats
    latency: LatencyStats
    estimated_cost: float = 0.0
    redaction: RedactionInfo
    privacy_level: str = "BALANCED"
    guardrails: GuardrailInfo = GuardrailInfo()
    datahaven_proof: Optional[DataHavenVerification] = None


# ── Internal pipeline DTOs ──────────────────────────────────────────

class PIIResult(BaseModel):
    masked_prompt: str
    redaction_count: int
    redaction_types: Dict[str, int]
    redaction_map: Dict[str, str]


class MemoryResult(BaseModel):
    retrieved_context: List[str] = []


class PromptPackage(BaseModel):
    messages: List[dict]
    token_count: int


class CompressionResult(BaseModel):
    compressed_messages: List[dict]
    stats: TokenStats


class RouteDecision(BaseModel):
    route: str          # LOCAL | CLOUD
    model: str


class InferenceResult(BaseModel):
    content: str
    usage_tokens: int
