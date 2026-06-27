
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
from typing import Optional
from configs.settings import settings
from tools.infra_tools import (
    find_nearby_assets,
    compute_distance,
    estimate_population_exposure,
)
from tools.wildfire_tools import (
    estimate_fire_spread,
    calculate_plume_direction,
)

# ── Output Schema ─────────────────────────────────────────
class InfraAssessment(BaseModel):
    latitude              : float
    longitude             : float
    search_radius_km      : float
    total_assets          : int
    houses                : int
    hospitals             : int
    schools               : int
    transformers          : int
    shelters              : int
    emergency_centers     : int
    estimated_population  : int
    spread_radius_km      : float
    plume_direction       : str
    impact_summary        : str

# ── Model Setup ───────────────────────────────────────────
def get_agent_model():
    provider = OpenAIProvider(
        base_url = settings.VLLM_BASE_URL,
        api_key  = settings.VLLM_API_KEY,
    )
    return OpenAIChatModel(settings.LLM_MODEL_NAME, provider=provider)

# ── Agent Definition ──────────────────────────────────────
infra_agent = Agent(
    model       = get_agent_model(),
    output_type = InfraAssessment,
    tools       = [
        find_nearby_assets,
        compute_distance,
        estimate_population_exposure,
        estimate_fire_spread,
        calculate_plume_direction,
    ],
    system_prompt = """
You are an Infrastructure and Demographics Agent for
the California Wildfire Early Warning System.

Your job:
1. Call estimate_fire_spread to get spread radius
2. Call find_nearby_assets(latitude, longitude,
   radius_km) to find all assets in spread zone
3. Call estimate_population_exposure to get
   population count
4. Call calculate_plume_direction with wind_direction
   and spread_radius
5. Return a complete InfraAssessment

Use spread_radius_km from estimate_fire_spread
as the radius for find_nearby_assets.
Be precise — use exact values from tools.
""",
)

async def run_infra_assessment(
    latitude      : float,
    longitude     : float,
    wind_speed    : float,
    wind_direction: float,
    humidity      : float,
    temperature   : float,
    drought_index : float,
) -> InfraAssessment:
    """Assess infrastructure risk at a wildfire location."""
    prompt = (
        f"Assess infrastructure risk at "
        f"latitude={latitude}, longitude={longitude}. "
        f"Weather: wind_speed={wind_speed} km/h, "
        f"wind_direction={wind_direction} degrees, "
        f"humidity={humidity}%, "
        f"temperature={temperature}C, "
        f"drought_index={drought_index}. "
        f"Use all tools and return full InfraAssessment."
    )
    async with infra_agent.run_mcp_servers():
        result = await infra_agent.run(prompt)
    return result.output
