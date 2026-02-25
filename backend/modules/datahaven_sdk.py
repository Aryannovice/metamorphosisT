"""
DataHaven SDK Client for Python

HTTP client that communicates with the DataHaven Node.js microservice.
Provides async methods for policy fetching, user data retrieval, and logging.

IMPORTANT: This client NEVER sends raw prompts or PII to DataHaven.
Only metadata flows through these endpoints.
"""

import logging
import os
from typing import Optional, Dict, Any

import httpx

from backend.models.mcp_contracts import MCPPolicy, MCPRequest

logger = logging.getLogger(__name__)

DATAHAVEN_SERVICE_URL = os.getenv("DATAHAVEN_SERVICE_URL", "http://localhost:3001")
DATAHAVEN_TIMEOUT = float(os.getenv("DATAHAVEN_TIMEOUT", "5.0"))


class DataHavenError(Exception):
    """Exception raised for DataHaven service errors."""
    pass


class DataHavenClient:
    """
    HTTP client for DataHaven microservice integration.
    
    Uses httpx for synchronous HTTP calls to the Express service.
    Includes graceful fallback on service unavailability.
    """
    
    def __init__(
        self,
        base_url: str = DATAHAVEN_SERVICE_URL,
        timeout: float = DATAHAVEN_TIMEOUT,
    ):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(timeout=timeout)
        self._available: Optional[bool] = None
    
    def is_available(self) -> bool:
        """
        Check if DataHaven service is reachable.
        
        Caches result after first successful check to avoid repeated calls.
        """
        if self._available is not None:
            return self._available
            
        try:
            resp = self._client.get(f"{self._base_url}/health")
            self._available = resp.status_code == 200
            return self._available
        except Exception:
            self._available = False
            return False
    
    def fetch_policy(self, user_id: Optional[str] = None) -> MCPPolicy:
        """
        Fetch policy configuration for a user from DataHaven.
        
        Args:
            user_id: User identifier. Defaults to 'default' if not provided.
            
        Returns:
            MCPPolicy object with user's policy configuration.
            Falls back to default policy on failure.
        """
        user_id = user_id or "default"
        
        try:
            resp = self._client.get(f"{self._base_url}/policy/{user_id}")
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success") and data.get("policy"):
                    policy_data = data["policy"]
                    return MCPPolicy(
                        mode=policy_data.get("mode", "BALANCED"),
                        allow_cloud=policy_data.get("allow_cloud", True),
                        max_tokens=policy_data.get("max_tokens", 4096),
                        require_pii_masking=policy_data.get("require_pii_masking", True),
                        compression_enabled=policy_data.get("compression_enabled", True),
                        whitelisted_providers=policy_data.get(
                            "whitelisted_providers", ["local", "groq", "openai"]
                        ),
                    )
            
            logger.warning(
                "DataHaven policy fetch returned non-200: %s", resp.status_code
            )
            return MCPPolicy.default()
            
        except httpx.ConnectError:
            logger.warning("DataHaven service not reachable, using default policy")
            return MCPPolicy.default()
        except Exception as exc:
            logger.warning("DataHaven policy fetch failed: %s", exc)
            return MCPPolicy.default()
    
    def fetch_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch authorized user data/metadata from DataHaven.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user data. Empty dict on failure.
        """
        try:
            resp = self._client.get(f"{self._base_url}/userdata/{user_id}")
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return data.get("data", {})
            
            return {}
            
        except Exception as exc:
            logger.warning("DataHaven user data fetch failed: %s", exc)
            return {}
    
    def log_inference(
        self,
        request: MCPRequest,
        response_route: str,
        provider: str,
        model: str,
        token_count: int,
        latency_ms: float,
        privacy_level: str,
        cost_estimate: float,
    ) -> bool:
        """
        Log inference metadata to DataHaven for compliance.
        
        IMPORTANT: This method NEVER sends raw prompts or PII.
        Only metadata is transmitted.
        
        Args:
            request: MCPRequest with audit trail
            response_route: Route decision (LOCAL/CLOUD)
            provider: Provider used (local/groq/openai)
            model: Model identifier
            token_count: Tokens used
            latency_ms: Total latency
            privacy_level: Privacy classification
            cost_estimate: Estimated cost
            
        Returns:
            True if logging succeeded, False otherwise
        """
        try:
            log_entry = {
                "request_id": request.request_id,
                "user_id": request.user_id or "anonymous",
                "route": response_route,
                "provider": provider,
                "model": model,
                "token_count": token_count,
                "latency_ms": round(latency_ms, 2),
                "privacy_level": privacy_level,
                "cost_estimate": round(cost_estimate, 6),
                "policy_mode": request.policy.mode.value,
            }
            
            resp = self._client.post(f"{self._base_url}/log", json=log_entry)
            
            if resp.status_code == 200:
                return True
            
            logger.warning("DataHaven log returned non-200: %s", resp.status_code)
            return False
            
        except httpx.ConnectError:
            logger.debug("DataHaven service not reachable for logging")
            return False
        except Exception as exc:
            logger.warning("DataHaven logging failed: %s", exc)
            return False
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()


# ── Global client instance ──────────────────────────────────────────

_datahaven_client: Optional[DataHavenClient] = None


def get_datahaven_client() -> DataHavenClient:
    """Get or create the global DataHaven client instance."""
    global _datahaven_client
    if _datahaven_client is None:
        _datahaven_client = DataHavenClient()
    return _datahaven_client
