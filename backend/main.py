import time
import uuid
import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SEC
from backend.models.schemas import (
    GatewayRequest,
    GatewayResponse,
    TokenStats,
    LatencyStats,
    RedactionInfo,
    GuardrailInfo,
)
from backend.modules.pii_guard import PIIGuard
from backend.modules.memory_layer import MemoryLayer
from backend.modules.prompt_builder import PromptBuilder
from backend.modules.prompt_shrinker import PromptShrinker
from backend.modules.routing_engine import RoutingEngine
from backend.modules.inference import InferenceEngine
from backend.modules.post_processor import estimate_cost, determine_privacy_level
from backend.modules.input_guardrails import InputGuardrails
from backend.modules.output_guardrails import OutputGuardrails
from backend.modules.rate_limiter import SlidingWindowRateLimiter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Metamorphosis – AI Optimization Gateway",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Module singletons ──────────────────────────────────────────────

input_guardrails = InputGuardrails()
output_guardrails = OutputGuardrails()
pii_guard = PIIGuard()
memory = MemoryLayer()
prompt_builder = PromptBuilder()
shrinker = PromptShrinker()
router_engine = RoutingEngine()
inference = InferenceEngine()
rate_limiter = SlidingWindowRateLimiter(
    max_requests=RATE_LIMIT_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SEC,
)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host or "unknown"


# ── Rate limit middleware ────────────────────────────────────────

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path != "/gateway":
        return await call_next(request)
    ip = _client_ip(request)
    allowed, retry_after = rate_limiter.is_allowed(ip)
    if not allowed:
        return Response(
            content='{"detail":"Rate limit exceeded. Try again later."}',
            status_code=429,
            headers={"Retry-After": str(retry_after)},
            media_type="application/json",
        )
    response = await call_next(request)
    if response.status_code == 200:
        rate_limiter.record(ip)
    return response


# ── Health check ────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "memory_entries": memory.count()}


# ── Main pipeline ──────────────────────────────────────────────────

@app.post("/gateway", response_model=GatewayResponse)
def gateway(req: GatewayRequest, request: Request):
    request_id = str(uuid.uuid4())
    t_start = time.perf_counter()

    # ─── [1] Input Guardrails ───────────────────────────────────
    t0 = time.perf_counter()
    input_ok, input_block_reason, input_guard_meta = input_guardrails.check(
        req.prompt
    )
    input_guardrails_ms = (time.perf_counter() - t0) * 1000

    if not input_ok:
        total_ms = (time.perf_counter() - t_start) * 1000
        return GatewayResponse(
            request_id=request_id,
            response=input_block_reason,
            route="BLOCKED",
            model_used="",
            token_stats=TokenStats(),
            latency=LatencyStats(
                input_guardrails_ms=round(input_guardrails_ms, 2),
                total_ms=round(total_ms, 2),
            ),
            estimated_cost=0.0,
            redaction=RedactionInfo(),
            privacy_level="BLOCKED",
            guardrails=GuardrailInfo(
                input_blocked=True,
                input_reason=input_block_reason,
            ),
        )

    # ─── [2] PII Guard ──────────────────────────────────────────
    t0 = time.perf_counter()
    masked_prompt, pii_info = pii_guard.mask(req.prompt, request_id)
    pii_ms = (time.perf_counter() - t0) * 1000

    # ─── [3] Memory Layer ───────────────────────────────────────
    t0 = time.perf_counter()
    context_snippets = memory.retrieve(masked_prompt)
    memory_ms = (time.perf_counter() - t0) * 1000

    # ─── [4] Prompt Builder ─────────────────────────────────────
    messages, tokens_before = prompt_builder.build(
        masked_prompt, context_snippets or None
    )

    # ─── [5] Prompt Shrinker ────────────────────────────────────
    t0 = time.perf_counter()
    compressed_msgs, tokens_after, tokens_saved = shrinker.compress(
        messages, tokens_before
    )
    compression_ms = (time.perf_counter() - t0) * 1000

    token_stats = TokenStats(
        original=tokens_before,
        compressed=tokens_after,
        saved=tokens_saved,
        compression_ratio=round(
            tokens_saved / tokens_before if tokens_before else 0, 3
        ),
    )

    # ─── [6] Routing Engine ─────────────────────────────────────
    cloud_prov = req.cloud_provider.value
    decision = router_engine.decide(req.mode.value, tokens_after, cloud_prov)

    # ─── [7] Inference ──────────────────────────────────────────
    t0 = time.perf_counter()
    raw_response, usage_tokens = inference.run(
        compressed_msgs, decision["route"], decision["model"], cloud_prov
    )
    inference_ms = (time.perf_counter() - t0) * 1000

    # ─── [8] Output Guardrails ────────────────────────────────────
    t0 = time.perf_counter()
    output_ok, final_response_candidate, output_guard_meta = (
        output_guardrails.check(raw_response)
    )
    output_guardrails_ms = (time.perf_counter() - t0) * 1000

    if not output_ok:
        final_response = final_response_candidate
        output_filtered = True
        output_reason = final_response_candidate
    else:
        final_response = final_response_candidate
        output_filtered = False
        output_reason = ""

    # ─── [9] Post-processing ──────────────────────────────────
    final_response = pii_guard.unmask(final_response, request_id)
    pii_guard.clear(request_id)

    cost = estimate_cost(token_stats, usage_tokens, decision["route"])
    privacy_level = determine_privacy_level(
        decision["route"], pii_info["redaction_count"]
    )

    total_ms = (time.perf_counter() - t_start) * 1000

    # Store interaction in memory (use sanitized response if output was filtered)
    content_to_store = final_response[:300] if output_filtered else raw_response[:300]
    memory.store(
        f"Q: {masked_prompt}\nA: {content_to_store}",
        request_id,
        {"route": decision["route"], "mode": req.mode.value},
    )

    return GatewayResponse(
        request_id=request_id,
        response=final_response,
        route=decision["route"],
        model_used=decision["model"],
        token_stats=token_stats,
        latency=LatencyStats(
            input_guardrails_ms=round(input_guardrails_ms, 2),
            pii_ms=round(pii_ms, 2),
            memory_ms=round(memory_ms, 2),
            compression_ms=round(compression_ms, 2),
            inference_ms=round(inference_ms, 2),
            output_guardrails_ms=round(output_guardrails_ms, 2),
            total_ms=round(total_ms, 2),
        ),
        estimated_cost=cost,
        redaction=RedactionInfo(
            count=pii_info["redaction_count"],
            types=pii_info["redaction_types"],
        ),
        privacy_level=privacy_level,
        guardrails=GuardrailInfo(
            input_blocked=False,
            output_filtered=output_filtered,
            output_reason=output_reason,
        ),
    )
