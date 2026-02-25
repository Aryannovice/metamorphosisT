"""
Backend Modules Package

Exports all pipeline modules for the AI Optimization Gateway.
"""

# Core pipeline modules
from backend.modules.rate_limiter import SlidingWindowRateLimiter
from backend.modules.input_guardrails import InputGuardrails
from backend.modules.pii_guard import PIIGuard
from backend.modules.memory_layer import MemoryLayer
from backend.modules.prompt_builder import PromptBuilder
from backend.modules.prompt_shrinker import PromptShrinker
from backend.modules.routing_engine import RoutingEngine
from backend.modules.inference import InferenceEngine
from backend.modules.output_guardrails import OutputGuardrails
from backend.modules.post_processor import estimate_cost, determine_privacy_level

# MCP components
from backend.modules.providers import (
    MCPProvider,
    LocalProvider,
    OpenAIProvider,
    GroqProvider,
    ProviderRegistry,
    provider_registry,
    create_provider_registry,
)
from backend.modules.policy_engine import PolicyEngine, get_policy_engine
from backend.modules.datahaven_sdk import (
    DataHavenClient,
    DataHavenError,
    get_datahaven_client,
)
from backend.modules.event_logger import (
    emit_event,
    emit_start,
    emit_complete,
    emit_error,
    emit_fallback,
    StageTimer,
    timed_stage,
    Stages,
)

__all__ = [
    # Core pipeline
    "SlidingWindowRateLimiter",
    "InputGuardrails",
    "PIIGuard",
    "MemoryLayer",
    "PromptBuilder",
    "PromptShrinker",
    "RoutingEngine",
    "InferenceEngine",
    "OutputGuardrails",
    "estimate_cost",
    "determine_privacy_level",
    # MCP Providers
    "MCPProvider",
    "LocalProvider",
    "OpenAIProvider",
    "GroqProvider",
    "ProviderRegistry",
    "provider_registry",
    "create_provider_registry",
    # Policy Engine
    "PolicyEngine",
    "get_policy_engine",
    # DataHaven SDK
    "DataHavenClient",
    "DataHavenError",
    "get_datahaven_client",
    # Event Logger
    "emit_event",
    "emit_start",
    "emit_complete",
    "emit_error",
    "emit_fallback",
    "StageTimer",
    "timed_stage",
    "Stages",
]

