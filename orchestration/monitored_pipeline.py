
import time

from orchestration.pipeline   import run_wildfire_pipeline
from orchestration.state      import WildfireSystemState
from models.vllm_integration  import vllm_client

async def run_monitored_pipeline(
    latitude     : float,
    longitude    : float,
    location_name: str = "Unknown Location",
    max_retries  : int = 3,
) -> tuple[WildfireSystemState, dict]:
    """
    Enhanced pipeline with token tracking,
    retry logic and performance monitoring.
    """
    print(f"\n🔍 Health check before pipeline...")
    health = await vllm_client.health_check()
    print(f"   vLLM Status : {health['status'].upper()}")
    print(f"   Latency     : {health.get('latency_ms', 'N/A')} ms")

    if health["status"] != "healthy":
        raise RuntimeError(
            f"vLLM server not healthy: {health.get('error')}"
        )

    # ── Run pipeline with retry ───────────────────────────
    start = time.time()
    state = await vllm_client.run_with_retry(
        coro_fn    = lambda: run_wildfire_pipeline(
            latitude      = latitude,
            longitude     = longitude,
            location_name = location_name,
        ),
        max_retries = max_retries,
        agent_name  = "full_pipeline",
    )
    elapsed = round(time.time() - start, 2)

    # ── Performance metrics ───────────────────────────────
    metrics = {
        "location"         : location_name,
        "pipeline_time_sec": elapsed,
        "agents_run"       : 3,
        "steps_completed"  : len(state.reasoning_trail),
        "risk_category"    : state.risk_category,
        "vllm_latency_ms"  : health.get("latency_ms"),
        "timestamp"        : state.completed_at,
    }

    print(f"\n⚡ Performance Metrics:")
    print(f"   Pipeline time : {elapsed}s")
    print(f"   Steps done    : {len(state.reasoning_trail)}")
    print(f"   vLLM latency  : {health.get('latency_ms')} ms")

    return state, metrics
