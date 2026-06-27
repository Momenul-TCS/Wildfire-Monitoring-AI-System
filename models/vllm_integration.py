
import httpx
import asyncio
import time
from datetime import datetime
from typing import Optional
from configs.settings import settings

class VLLMIntegration:
    """
    Central vLLM integration manager.
    Handles health checks, token tracking,
    retry logic and model configuration.
    """

    def __init__(self):
        self.base_url  = settings.VLLM_BASE_URL
        self.api_key   = settings.VLLM_API_KEY
        self.model     = settings.LLM_MODEL_NAME
        self.headers   = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type" : "application/json",
        }
        self.token_log = []
        self.call_log  = []

    # ── Health Check ──────────────────────────────────────
    async def health_check(self) -> dict:
        """Check if vLLM server is running and responsive."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                start    = time.time()
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                latency  = round((time.time() - start) * 1000, 2)

                if response.status_code == 200:
                    models = response.json().get("data", [])
                    return {
                        "status"     : "healthy",
                        "latency_ms" : latency,
                        "models"     : [m["id"] for m in models],
                        "timestamp"  : datetime.now().isoformat(),
                    }
                else:
                    return {
                        "status"    : "unhealthy",
                        "error"     : f"HTTP {response.status_code}",
                        "timestamp" : datetime.now().isoformat(),
                    }
        except Exception as e:
            return {
                "status"   : "unreachable",
                "error"    : str(e),
                "timestamp": datetime.now().isoformat(),
            }

    # ── Token Tracker ─────────────────────────────────────
    def log_tokens(
        self,
        agent_name    : str,
        input_tokens  : int,
        output_tokens : int,
        model         : str = None,
    ):
        """Log token usage for monitoring."""
        model    = model or self.model
        cost_usd = self._estimate_cost(
            model, input_tokens, output_tokens
        )
        entry = {
            "timestamp"    : datetime.now().isoformat(),
            "agent"        : agent_name,
            "model"        : model,
            "input_tokens" : input_tokens,
            "output_tokens": output_tokens,
            "total_tokens" : input_tokens + output_tokens,
            "cost_usd"     : cost_usd,
        }
        self.token_log.append(entry)
        return entry

    def _estimate_cost(
        self, model: str,
        input_t: int, output_t: int
    ) -> float:
        """Estimate cost per 1M tokens."""
        pricing = {
            "Qwen3-30B-A3B"    : {"input": 0.10, "output": 0.30},
            "gpt-4o"           : {"input": 2.50, "output": 10.0},
            "gpt-4o-mini"      : {"input": 0.15, "output": 0.60},
        }
        p = pricing.get(model, {"input": 0.10, "output": 0.30})
        return round(
            (input_t * p["input"] + output_t * p["output"])
            / 1_000_000, 8
        )

    def get_token_summary(self) -> dict:
        """Get summary of all token usage."""
        if not self.token_log:
            return {"total_calls": 0, "total_tokens": 0,
                    "total_cost_usd": 0}
        total_input  = sum(e["input_tokens"]  for e in self.token_log)
        total_output = sum(e["output_tokens"] for e in self.token_log)
        total_cost   = sum(e["cost_usd"]      for e in self.token_log)
        by_agent     = {}
        for entry in self.token_log:
            ag = entry["agent"]
            if ag not in by_agent:
                by_agent[ag] = {"calls": 0, "tokens": 0}
            by_agent[ag]["calls"]  += 1
            by_agent[ag]["tokens"] += entry["total_tokens"]
        return {
            "total_calls"    : len(self.token_log),
            "total_input"    : total_input,
            "total_output"   : total_output,
            "total_tokens"   : total_input + total_output,
            "total_cost_usd" : round(total_cost, 6),
            "by_agent"       : by_agent,
        }

    # ── Retry Logic ───────────────────────────────────────
    async def run_with_retry(
        self,
        coro_fn,
        max_retries : int   = 3,
        delay_sec   : float = 2.0,
        agent_name  : str   = "unknown",
    ):
        """
        Run an async coroutine with retry logic.
        Retries on connection errors and timeouts.
        """
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                start  = time.time()
                result = await coro_fn()
                elapsed = round(time.time() - start, 2)
                self.call_log.append({
                    "agent"    : agent_name,
                    "attempt"  : attempt,
                    "success"  : True,
                    "elapsed_s": elapsed,
                    "timestamp": datetime.now().isoformat(),
                })
                return result
            except Exception as e:
                last_error = e
                self.call_log.append({
                    "agent"    : agent_name,
                    "attempt"  : attempt,
                    "success"  : False,
                    "error"    : str(e)[:100],
                    "timestamp": datetime.now().isoformat(),
                })
                if attempt < max_retries:
                    wait = delay_sec * attempt
                    print(f"   ⚠️  Attempt {attempt} failed. "
                          f"Retrying in {wait}s...")
                    await asyncio.sleep(wait)

        raise RuntimeError(
            f"Agent {agent_name} failed after "
            f"{max_retries} attempts: {last_error}"
        )

    # ── Model Info ────────────────────────────────────────
    async def get_model_info(self) -> dict:
        """Get detailed model information from vLLM."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    if models:
                        return {
                            "model_id"  : models[0]["id"],
                            "created"   : models[0].get("created"),
                            "owned_by"  : models[0].get("owned_by"),
                            "base_url"  : self.base_url,
                            "status"    : "loaded",
                        }
        except Exception as e:
            return {"status": "error", "error": str(e)}
        return {"status": "unknown"}

# ── Singleton instance ────────────────────────────────────
vllm_client = VLLMIntegration()
