
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
from typing import Optional
from configs.settings import settings
from tools.alert_tools import generate_alert, format_final_report

# ── Output Schema ─────────────────────────────────────────
class AlertOutput(BaseModel):
    alert_id          : str
    severity          : str
    headline          : str
    message           : str
    recommended_actions: list[str]
    probability_pct   : float
    spread_radius_km  : float
    population_at_risk: int

# ── Model Setup ───────────────────────────────────────────
def get_agent_model():
    provider = OpenAIProvider(
        base_url = settings.VLLM_BASE_URL,
        api_key  = settings.VLLM_API_KEY,
    )
    return OpenAIChatModel(settings.LLM_MODEL_NAME, provider=provider)

# ── Agent Definition ──────────────────────────────────────
alert_agent = Agent(
    model       = get_agent_model(),
    output_type = AlertOutput,
    tools       = [generate_alert],
    system_prompt = """
You are an Alert Generation Agent for the California
Wildfire Early Warning System.

Your job:
1. Receive risk_category, probability, location,
   spread_radius and population_at_risk
2. Call generate_alert tool with these values
3. Return a structured AlertOutput

Always call generate_alert tool.
Use exact values provided — do not modify them.
Return all fields from the tool result.
""",
)

async def run_alert_generation(
    risk_category     : str,
    probability       : float,
    location_name     : str,
    spread_radius     : float,
    population_at_risk: int = 0,
) -> AlertOutput:
    """Generate emergency alert based on risk assessment."""
    prompt = (
        f"Generate a wildfire alert for {location_name}. "
        f"Risk category: {risk_category}. "
        f"Fire probability: {probability:.1%}. "
        f"Estimated spread radius: {spread_radius:.2f} km. "
        f"Population at risk: {population_at_risk:,}. "
        f"Call generate_alert tool and return AlertOutput."
    )
    async with alert_agent.run_mcp_servers():
        result = await alert_agent.run(prompt)
    return result.output
