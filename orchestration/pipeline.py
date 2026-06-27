
import asyncio
from datetime import datetime

from orchestration.state  import WildfireSystemState
from agents.weather_agent import run_weather_assessment
from agents.alert_agent   import run_alert_generation
from agents.infra_agent   import run_infra_assessment

async def run_wildfire_pipeline(
    latitude     : float,
    longitude    : float,
    location_name: str = "Unknown Location",
) -> WildfireSystemState:
    """
    Main pipeline — runs all 3 agents in sequence
    and aggregates results into WildfireSystemState.
    """
    state              = WildfireSystemState()
    state.latitude     = latitude
    state.longitude    = longitude
    state.location_name= location_name
    state.triggered_at = datetime.now().isoformat()

    print(f"\n{'='*55}")
    print(f"  🔥 WILDFIRE PIPELINE STARTED")
    print(f"  📍 Location : {location_name}")
    print(f"  🌐 Coords   : {latitude}, {longitude}")
    print(f"  🕐 Time     : {state.triggered_at}")
    print(f"{'='*55}")

    # ── STEP 1: Weather Intelligence Agent ────────────────
    print(f"\n[STEP 1/3] 🌤️  Weather Intelligence Agent...")
    state.add_reasoning(
        "Step 1", f"Running Weather Agent for {location_name}"
    )
    try:
        weather = await run_weather_assessment(latitude, longitude)

        # Store in state
        state.temperature      = weather.temperature
        state.humidity         = weather.humidity
        state.wind_speed       = weather.wind_speed
        state.wind_direction   = getattr(weather, "wind_direction", 45.0)
        state.drought_index    = weather.drought_index
        state.fwi_score        = weather.fwi_score
        state.fire_probability = weather.fire_probability
        state.risk_category    = weather.risk_category
        state.spread_radius_km = weather.spread_radius_km
        state.weather_summary  = weather.summary

        state.add_reasoning(
            "Step 1 Complete",
            f"Risk={weather.risk_category} "
            f"Prob={weather.fire_probability:.1%} "
            f"Spread={weather.spread_radius_km}km"
        )
        print(f"   ✅ Risk     : {weather.risk_category} "
              f"({weather.fire_probability:.1%})")
        print(f"   ✅ Spread   : {weather.spread_radius_km} km")
        print(f"   ✅ FWI Score: {weather.fwi_score}")

    except Exception as e:
        state.add_reasoning("Step 1 Failed", str(e))
        print(f"   ❌ Weather Agent failed: {e}")
        raise

    # ── STEP 2: Alert Generation Agent ────────────────────
    print(f"\n[STEP 2/3] 🚨  Alert Generation Agent...")
    state.add_reasoning(
        "Step 2",
        f"Generating alert for {state.risk_category} risk"
    )
    try:
        alert = await run_alert_generation(
            risk_category      = state.risk_category,
            probability        = state.fire_probability,
            location_name      = location_name,
            spread_radius      = state.spread_radius_km,
            population_at_risk = 0,  # updated after step 3
        )

        # Store in state
        state.alert_id       = alert.alert_id
        state.alert_severity = alert.severity
        state.alert_headline = alert.headline
        state.alert_message  = alert.message
        state.alert_actions  = alert.recommended_actions

        state.add_reasoning(
            "Step 2 Complete",
            f"Alert={alert.severity} ID={alert.alert_id}"
        )
        print(f"   ✅ Alert ID : {alert.alert_id}")
        print(f"   ✅ Severity : {alert.severity}")
        print(f"   ✅ Headline : {alert.headline[:60]}...")

    except Exception as e:
        state.add_reasoning("Step 2 Failed", str(e))
        print(f"   ❌ Alert Agent failed: {e}")
        raise

    # ── STEP 3: Infrastructure Agent ──────────────────────
    print(f"\n[STEP 3/3] 🏗️   Infrastructure Agent...")
    state.add_reasoning(
        "Step 3",
        f"Assessing infrastructure within "
        f"{state.spread_radius_km}km radius"
    )
    try:
        infra = await run_infra_assessment(
            latitude       = latitude,
            longitude      = longitude,
            wind_speed     = state.wind_speed,
            wind_direction = state.wind_direction,
            humidity       = state.humidity,
            temperature    = state.temperature,
            drought_index  = state.drought_index,
        )

        # Store in state
        state.total_assets           = infra.total_assets
        state.houses                 = infra.houses
        state.hospitals              = infra.hospitals
        state.schools                = infra.schools
        state.estimated_population   = infra.estimated_population
        state.plume_direction        = infra.plume_direction
        state.impact_summary         = infra.impact_summary

        state.add_reasoning(
            "Step 3 Complete",
            f"Assets={infra.total_assets} "
            f"Population={infra.estimated_population} "
            f"Plume={infra.plume_direction}"
        )
        print(f"   ✅ Assets   : {infra.total_assets} found")
        print(f"   ✅ Population: {infra.estimated_population:,}")
        print(f"   ✅ Plume    : Moving {infra.plume_direction}")

    except Exception as e:
        state.add_reasoning("Step 3 Failed", str(e))
        print(f"   ❌ Infra Agent failed: {e}")
        raise

    # ── STEP 4: Aggregate Final Report ────────────────────
    print(f"\n[FINAL] 📋  Aggregating Results...")
    state.final_report  = _build_final_report(state)
    state.completed_at  = datetime.now().isoformat()
    state.add_reasoning(
        "Pipeline Complete",
        f"Report generated at {state.completed_at}"
    )
    print(state.final_report)

    return state


def _build_final_report(state: WildfireSystemState) -> str:
    """Build comprehensive final report from state."""
    emoji_map = {
        "Critical": "🔴", "High"  : "🟠",
        "Medium"  : "🟡", "Low"   : "🟢"
    }
    emoji = emoji_map.get(state.risk_category, "⚪")

    actions_str = "\n".join(
        f"      {a}" for a in state.alert_actions
    )

    report = f"""
╔══════════════════════════════════════════════════════╗
║     CALIFORNIA WILDFIRE EARLY WARNING SYSTEM         ║
║     FINAL ASSESSMENT REPORT                          ║
╚══════════════════════════════════════════════════════╝

📍 LOCATION
   Name           : {state.location_name}
   Coordinates    : {state.latitude}, {state.longitude}
   Assessment Time: {state.completed_at}

{emoji} RISK ASSESSMENT
   Risk Category  : {state.risk_category}
   Fire Probability: {state.fire_probability:.1%}
   FWI Score      : {state.fwi_score}
   Spread Radius  : {state.spread_radius_km} km
   Plume Direction: {state.plume_direction}

🌤️  WEATHER CONDITIONS
   Temperature    : {state.temperature}°C
   Humidity       : {state.humidity}%
   Wind Speed     : {state.wind_speed} km/h
   Drought Index  : {state.drought_index}/10

🏗️  INFRASTRUCTURE IMPACT
   Total Assets   : {state.total_assets}
   Houses         : {state.houses}
   Hospitals      : {state.hospitals}
   Schools        : {state.schools}
   Population     : {state.estimated_population:,} at risk

🚨 ALERT — {state.alert_severity}
   {state.alert_headline}
   {state.alert_message}

📋 RECOMMENDED ACTIONS
{actions_str}

🧠 REASONING TRAIL ({len(state.reasoning_trail)} steps)
"""
    for step in state.reasoning_trail:
        report += f"   [{step['step']}] {step['detail']}\n"

    report += f"""
{'─'*54}
Generated by: California Wildfire Early Warning System
Powered by  : Pydantic AI + vLLM + AMD ROCm GPU
{'─'*54}
"""
    return report.strip()
