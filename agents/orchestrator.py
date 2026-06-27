
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
from configs.settings import settings
from orchestration.pipeline import run_wildfire_pipeline
from orchestration.state    import WildfireSystemState

# ── Output Schema ─────────────────────────────────────────
class OrchestratorOutput(BaseModel):
    location_name    : str
    risk_category    : str
    fire_probability : float
    alert_severity   : str
    alert_headline   : str
    total_assets     : int
    population_at_risk: int
    spread_radius_km : float
    plume_direction  : str
    final_summary    : str
    steps_completed  : int

# ── Model Setup ───────────────────────────────────────────
def get_agent_model():
    provider = OpenAIProvider(
        base_url = settings.VLLM_BASE_URL,
        api_key  = settings.VLLM_API_KEY,
    )
    return OpenAIChatModel(settings.LLM_MODEL_NAME, provider=provider)

# ── Orchestrator Agent ────────────────────────────────────
orchestrator_agent = Agent(
    model       = get_agent_model(),
    output_type = OrchestratorOutput,
    system_prompt = """
You are the Orchestrator Agent for the California
Wildfire Early Warning System.

You manage the complete wildfire assessment pipeline.
Given a location (latitude, longitude, name), you
coordinate all sub-agents and produce a final
comprehensive assessment.

Return an OrchestratorOutput with:
- All risk metrics from the weather assessment
- Alert severity and headline from alert agent
- Infrastructure counts from infra agent
- A clear final_summary of the situation
- steps_completed = number of pipeline steps run

Be precise with all numeric values.
Write final_summary in plain English for emergency
responders — clear, concise, actionable.
""",
)

async def run_orchestrator(
    latitude     : float,
    longitude    : float,
    location_name: str = "Unknown Location",
) -> tuple[OrchestratorOutput, WildfireSystemState]:
    """
    Main entry point for the wildfire system.
    Runs complete pipeline and returns structured output.
    """
    # Run full pipeline
    state = await run_wildfire_pipeline(
        latitude      = latitude,
        longitude     = longitude,
        location_name = location_name,
    )

    # Ask orchestrator agent to summarise
    prompt = f"""
    Wildfire assessment completed for {location_name}.
    Here are the results:

    Risk Category   : {state.risk_category}
    Fire Probability: {state.fire_probability:.1%}
    FWI Score       : {state.fwi_score}
    Spread Radius   : {state.spread_radius_km} km
    Alert Severity  : {state.alert_severity}
    Alert Headline  : {state.alert_headline}
    Total Assets    : {state.total_assets}
    Houses          : {state.houses}
    Hospitals       : {state.hospitals}
    Schools         : {state.schools}
    Population      : {state.estimated_population}
    Plume Direction : {state.plume_direction}
    Steps Completed : {len(state.reasoning_trail)}

    Produce a final OrchestratorOutput summarising
    this assessment for emergency responders.
    """

    async with orchestrator_agent.run_mcp_servers():
        result = await orchestrator_agent.run(prompt)

    return result.output, state
