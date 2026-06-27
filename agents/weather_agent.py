
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
from typing import Optional
from configs.settings import settings
from tools.weather_tools  import (
    get_latest_weather,
    get_weather_forecast,
    get_fire_weather_index,
)
from tools.wildfire_tools import (
    predict_wildfire_risk,
    estimate_fire_spread,
)

# ── Output Schema ─────────────────────────────────────────
class WeatherAssessment(BaseModel):
    location_lat      : float
    location_lon      : float
    temperature       : float
    humidity          : float
    wind_speed        : float
    drought_index     : float
    fwi_score         : float
    fire_probability  : float
    risk_category     : str
    spread_radius_km  : float
    summary           : str

# ── Model Setup ───────────────────────────────────────────
def get_agent_model():
    provider = OpenAIProvider(
        base_url = settings.VLLM_BASE_URL,
        api_key  = settings.VLLM_API_KEY,
    )
    return OpenAIChatModel(settings.LLM_MODEL_NAME, provider=provider)

# ── Agent Definition ──────────────────────────────────────
weather_agent = Agent(
    model       = get_agent_model(),
    output_type = WeatherAssessment,
    tools       = [
        get_latest_weather,
        get_weather_forecast,
        get_fire_weather_index,
        predict_wildfire_risk,
        estimate_fire_spread,
    ],
    system_prompt = """
You are a Weather Intelligence Agent for the California
Wildfire Early Warning System.

Your job:
1. Call get_latest_weather(latitude, longitude)
2. Call get_fire_weather_index with the weather values
3. Call predict_wildfire_risk with the weather values
4. Call estimate_fire_spread with weather values
5. Return a WeatherAssessment with all findings

Always use exact values from tool results.
Be precise with numbers. Do not guess or estimate —
use tool outputs only.
""",
)

async def run_weather_assessment(
    latitude : float,
    longitude: float,
) -> WeatherAssessment:
    """Run weather intelligence assessment for a location."""
    prompt = (
        f"Assess wildfire risk for location: "
        f"latitude={latitude}, longitude={longitude}. "
        f"Use all available tools and return full assessment."
    )
    async with weather_agent.run_mcp_servers():
        result = await weather_agent.run(prompt)
    return result.output
