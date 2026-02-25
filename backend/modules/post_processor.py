from backend.config import COST_PER_1K_INPUT, COST_PER_1K_OUTPUT
from backend.models.schemas import TokenStats


def estimate_cost(token_stats: TokenStats, usage_tokens: int, route: str) -> float:
    if route == "LOCAL":
        return 0.0
    input_cost = (token_stats.compressed / 1000) * COST_PER_1K_INPUT
    output_cost = (usage_tokens / 1000) * COST_PER_1K_OUTPUT
    return round(input_cost + output_cost, 6)


def determine_privacy_level(route: str, redaction_count: int) -> str:
    if route == "LOCAL":
        return "HIGH"
    if redaction_count > 0:
        return "BALANCED"
    return "CLOUD_HEAVY"
