"""
Backend Models Package

Exports all Pydantic models for the AI Optimization Gateway.
"""

from backend.models.schemas import (
    UserMode,
    CloudProvider,
    GatewayRequest,
    GatewayResponse,
    TokenStats,
    LatencyStats,
    GuardrailInfo,
    RedactionInfo,
    PIIResult,
    MemoryResult,
    PromptPackage,
    CompressionResult,
    RouteDecision,
    InferenceResult,
)

from backend.models.mcp_contracts import (
    PolicyMode,
    MCPPolicy,
    AuditEntry,
    MCPTokenStats,
    MCPRequest,
    MCPLatencyStats,
    MCPGuardrailResult,
    MCPRedactionInfo,
    MCPResponse,
)

__all__ = [
    # Legacy schemas
    "UserMode",
    "CloudProvider",
    "GatewayRequest",
    "GatewayResponse",
    "TokenStats",
    "LatencyStats",
    "GuardrailInfo",
    "RedactionInfo",
    "PIIResult",
    "MemoryResult",
    "PromptPackage",
    "CompressionResult",
    "RouteDecision",
    "InferenceResult",
    # MCP contracts
    "PolicyMode",
    "MCPPolicy",
    "AuditEntry",
    "MCPTokenStats",
    "MCPRequest",
    "MCPLatencyStats",
    "MCPGuardrailResult",
    "MCPRedactionInfo",
    "MCPResponse",
]

