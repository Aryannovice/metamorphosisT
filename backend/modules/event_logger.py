"""
Structured Event Logger

Provides emit_event function for appending structured logs to MCPRequest.audit_trail.
Each pipeline stage emits events with:
- stage name
- timestamp
- duration
- route decision
- provider
- token metrics
- additional metadata
"""

import logging
import time
from datetime import datetime
from typing import Any, Optional, Callable, TypeVar
from functools import wraps

from backend.models.mcp_contracts import MCPRequest, AuditEntry

logger = logging.getLogger(__name__)

T = TypeVar("T")


def emit_event(
    stage: str,
    request: MCPRequest,
    duration_ms: float = 0.0,
    route_decision: Optional[str] = None,
    provider: Optional[str] = None,
    token_count: Optional[int] = None,
    **extra: Any,
) -> None:
    """
    Emit a structured event to the request's audit trail.
    
    This function appends a standardized audit entry to the MCPRequest,
    enabling full traceability and compliance logging.
    
    Args:
        stage: Pipeline stage identifier (e.g., "input_guardrails", "pii_guard")
        request: MCPRequest to append audit entry to
        duration_ms: Time spent in this stage
        route_decision: Routing decision if applicable
        provider: Provider name if applicable
        token_count: Token count after this stage
        **extra: Additional metadata to include
        
    Example:
        emit_event(
            "pii_guard",
            request,
            duration_ms=15.3,
            token_count=150,
            redaction_count=3
        )
    """
    request.add_audit(
        stage=stage,
        duration_ms=duration_ms,
        route_decision=route_decision,
        provider=provider,
        token_count=token_count,
        **extra,
    )
    
    # Also log to standard logger for debugging
    logger.debug(
        "[%s] stage=%s duration=%.2fms route=%s provider=%s tokens=%s",
        request.request_id[:8],
        stage,
        duration_ms,
        route_decision or "-",
        provider or "-",
        token_count or "-",
    )


def emit_start(stage: str, request: MCPRequest, **extra: Any) -> None:
    """
    Emit a stage start event (duration=0, used for tracking entry).
    """
    emit_event(stage, request, duration_ms=0.0, status="started", **extra)


def emit_complete(
    stage: str,
    request: MCPRequest,
    duration_ms: float,
    success: bool = True,
    **extra: Any,
) -> None:
    """
    Emit a stage completion event with success/failure status.
    """
    emit_event(
        stage,
        request,
        duration_ms=duration_ms,
        status="completed" if success else "failed",
        **extra,
    )


def emit_error(
    stage: str,
    request: MCPRequest,
    error: str,
    duration_ms: float = 0.0,
    **extra: Any,
) -> None:
    """
    Emit an error event for a failed stage.
    """
    emit_event(
        stage,
        request,
        duration_ms=duration_ms,
        status="error",
        error=error,
        **extra,
    )
    logger.error("[%s] %s error: %s", request.request_id[:8], stage, error)


def emit_fallback(
    stage: str,
    request: MCPRequest,
    from_provider: str,
    to_provider: str,
    reason: str,
    **extra: Any,
) -> None:
    """
    Emit a fallback event when switching providers.
    """
    emit_event(
        stage,
        request,
        status="fallback",
        from_provider=from_provider,
        to_provider=to_provider,
        fallback_reason=reason,
        **extra,
    )
    logger.info(
        "[%s] Fallback: %s -> %s (%s)",
        request.request_id[:8],
        from_provider,
        to_provider,
        reason,
    )


class StageTimer:
    """
    Context manager for timing pipeline stages and emitting events.
    
    Usage:
        with StageTimer("pii_guard", request) as timer:
            result = pii_guard.mask(prompt)
            timer.set_metadata(redaction_count=result.count)
    """
    
    def __init__(
        self,
        stage: str,
        request: MCPRequest,
        auto_emit: bool = True,
        **initial_metadata: Any,
    ):
        self.stage = stage
        self.request = request
        self.auto_emit = auto_emit
        self.metadata = initial_metadata
        self._start: float = 0
        self._duration_ms: float = 0
        self._success: bool = True
        self._error: Optional[str] = None
    
    def __enter__(self) -> "StageTimer":
        self._start = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self._duration_ms = (time.perf_counter() - self._start) * 1000
        
        if exc_type is not None:
            self._success = False
            self._error = str(exc_val)
        
        if self.auto_emit:
            if self._success:
                emit_complete(
                    self.stage,
                    self.request,
                    self._duration_ms,
                    success=True,
                    **self.metadata,
                )
            else:
                emit_error(
                    self.stage,
                    self.request,
                    self._error or "Unknown error",
                    self._duration_ms,
                    **self.metadata,
                )
        
        return False  # Don't suppress exceptions
    
    def set_metadata(self, **kwargs: Any) -> None:
        """Add or update metadata for this stage's event."""
        self.metadata.update(kwargs)
    
    @property
    def duration_ms(self) -> float:
        """Get elapsed duration (can be called during stage)."""
        if self._duration_ms > 0:
            return self._duration_ms
        return (time.perf_counter() - self._start) * 1000


def timed_stage(stage: str):
    """
    Decorator for automatically timing and logging a function as a pipeline stage.
    
    The decorated function must accept an MCPRequest as its first argument.
    
    Usage:
        @timed_stage("pii_guard")
        def mask_pii(request: MCPRequest, prompt: str) -> PIIResult:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(request: MCPRequest, *args: Any, **kwargs: Any) -> T:
            with StageTimer(stage, request):
                return func(request, *args, **kwargs)
        return wrapper
    return decorator


# ── Stage name constants ────────────────────────────────────────────

class Stages:
    """Standard stage names for consistency."""
    POLICY_FETCH = "policy_fetch"
    INPUT_GUARDRAILS = "input_guardrails"
    PII_GUARD = "pii_guard"
    MEMORY_RETRIEVAL = "memory_retrieval"
    PROMPT_BUILD = "prompt_build"
    PROMPT_COMPRESS = "prompt_compress"
    ROUTING = "routing"
    INFERENCE = "inference"
    OUTPUT_GUARDRAILS = "output_guardrails"
    POST_PROCESS = "post_process"
    MEMORY_STORE = "memory_store"
    DATAHAVEN_LOG = "datahaven_log"
