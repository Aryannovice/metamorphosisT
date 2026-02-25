"""
MCP (Model Context Protocol) Standardized Contracts

These models ensure consistent data flow through the entire pipeline.
All modules pass MCPRequest/MCPResponse objects for audit-ready compliance.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class PolicyMode(str, Enum):
    STRICT = "STRICT"
    BALANCED = "BALANCED"
    PERFORMANCE = "PERFORMANCE"


class MCPPolicy(BaseModel):
    """Enterprise policy object fetched via DataHaven."""
    mode: PolicyMode = PolicyMode.BALANCED
    allow_cloud: bool = True
    max_tokens: int = 4096
    require_pii_masking: bool = True
    compression_enabled: bool = True
    whitelisted_providers: List[str] = Field(
        default_factory=lambda: ["local", "groq", "openai", "mistral", "openrouter"]
    )
    
    @classmethod
    def default(cls) -> "MCPPolicy":
        """Return default permissive policy."""
        return cls()
    
    def allows_provider(self, provider: str) -> bool:
        """Check if a provider is allowed by this policy."""
        return provider.lower() in [p.lower() for p in self.whitelisted_providers]


class AuditEntry(BaseModel):
    """Structured audit trail entry for compliance logging."""
    stage: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    duration_ms: float = 0.0
    route_decision: Optional[str] = None
    provider: Optional[str] = None
    token_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MCPTokenStats(BaseModel):
    """Token statistics tracked through the pipeline."""
    original: int = 0
    after_pii: int = 0
    after_memory: int = 0
    after_compression: int = 0
    inference_used: int = 0
    saved: int = 0
    compression_ratio: float = 0.0


class MCPRequest(BaseModel):
    """
    Standardized MCP-compliant request object.
    
    Passed through all pipeline stages, accumulating metadata and audit trail.
    """
    request_id: str
    user_id: Optional[str] = None
    prompt: str
    masked_prompt: Optional[str] = None
    policy: MCPPolicy = Field(default_factory=MCPPolicy.default)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    token_stats: MCPTokenStats = Field(default_factory=MCPTokenStats)
    audit_trail: List[AuditEntry] = Field(default_factory=list)
    
    # Pipeline state (accumulated during processing)
    pii_map: Dict[str, str] = Field(default_factory=dict)
    context_snippets: List[str] = Field(default_factory=list)
    messages: List[dict] = Field(default_factory=list)
    compressed_messages: List[dict] = Field(default_factory=list)
    route: Optional[str] = None
    model: Optional[str] = None
    cloud_provider: str = "GROQ"
    
    def add_audit(
        self,
        stage: str,
        duration_ms: float = 0.0,
        route_decision: Optional[str] = None,
        provider: Optional[str] = None,
        token_count: Optional[int] = None,
        **extra: Any
    ) -> None:
        """Append a structured audit entry."""
        self.audit_trail.append(
            AuditEntry(
                stage=stage,
                duration_ms=round(duration_ms, 2),
                route_decision=route_decision,
                provider=provider,
                token_count=token_count,
                metadata=extra,
            )
        )


class MCPLatencyStats(BaseModel):
    """Latency breakdown per pipeline stage."""
    policy_fetch_ms: float = 0.0
    input_guardrails_ms: float = 0.0
    pii_ms: float = 0.0
    memory_ms: float = 0.0
    prompt_build_ms: float = 0.0
    compression_ms: float = 0.0
    routing_ms: float = 0.0
    inference_ms: float = 0.0
    output_guardrails_ms: float = 0.0
    post_process_ms: float = 0.0
    total_ms: float = 0.0


class MCPGuardrailResult(BaseModel):
    """Guardrail evaluation results."""
    input_blocked: bool = False
    input_reason: str = ""
    output_filtered: bool = False
    output_reason: str = ""


class MCPRedactionInfo(BaseModel):
    """PII redaction summary."""
    count: int = 0
    types: Dict[str, int] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    """
    Standardized MCP-compliant response object.
    
    Contains full audit trail and compliance metadata for enterprise use.
    """
    request_id: str
    response: str
    route: str
    provider: str
    model_used: str
    token_stats: MCPTokenStats
    latency_stats: MCPLatencyStats
    privacy_level: str = "BALANCED"
    cost_estimate: float = 0.0
    redaction: MCPRedactionInfo = Field(default_factory=MCPRedactionInfo)
    guardrails: MCPGuardrailResult = Field(default_factory=MCPGuardrailResult)
    audit_trail: List[AuditEntry] = Field(default_factory=list)
    policy_applied: MCPPolicy = Field(default_factory=MCPPolicy.default)
    
    @classmethod
    def blocked(
        cls,
        request_id: str,
        reason: str,
        latency_stats: MCPLatencyStats,
        audit_trail: List[AuditEntry],
    ) -> "MCPResponse":
        """Create a blocked response for guardrail violations."""
        return cls(
            request_id=request_id,
            response=reason,
            route="BLOCKED",
            provider="",
            model_used="",
            token_stats=MCPTokenStats(),
            latency_stats=latency_stats,
            privacy_level="BLOCKED",
            guardrails=MCPGuardrailResult(input_blocked=True, input_reason=reason),
            audit_trail=audit_trail,
        )
    
    @classmethod
    def error(
        cls,
        request_id: str,
        error_msg: str,
        latency_stats: MCPLatencyStats,
        audit_trail: List[AuditEntry],
    ) -> "MCPResponse":
        """Create an error response for failures."""
        return cls(
            request_id=request_id,
            response=f"[Error] {error_msg}",
            route="ERROR",
            provider="",
            model_used="",
            token_stats=MCPTokenStats(),
            latency_stats=latency_stats,
            privacy_level="ERROR",
            audit_trail=audit_trail,
        )
