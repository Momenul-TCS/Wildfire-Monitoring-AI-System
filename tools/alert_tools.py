
from datetime import datetime
from pydantic_ai import Tool
from configs.settings import settings

# ── Tool 1: Generate Alert ────────────────────────────────
@Tool
def generate_alert(
    risk_category  : str,
    probability    : float,
    location_name  : str,
    spread_radius  : float,
    population_at_risk: int = 0,
) -> dict:
    """
    Generate a structured emergency alert message
    based on wildfire risk assessment results.
    Returns formatted alert with severity, message,
    and recommended emergency actions.
    Args:
        risk_category: One of Low/Medium/High/Critical
        probability: Wildfire probability (0.0 to 1.0)
        location_name: Name of the affected location
        spread_radius: Estimated fire spread in km
        population_at_risk: Estimated affected population
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    alert_templates = {
        "Critical": {
            "severity" : "CRITICAL",
            "color"    : "RED",
            "emoji"    : "🔴",
            "headline" : f"CRITICAL WILDFIRE ALERT — {location_name.upper()}",
            "message"  : (
                f"CRITICAL wildfire risk detected near {location_name}. "
                f"Ignition probability: {probability*100:.1f}%. "
                f"Estimated fire spread radius: {spread_radius:.1f} km. "
                f"Approximately {population_at_risk:,} people at risk. "
                f"IMMEDIATE action required."
            ),
            "actions"  : [
                "🚨 Evacuate all residents within spread radius immediately",
                "🚒 Deploy all available fire suppression units",
                "🏥 Alert hospitals and medical centers",
                "📻 Broadcast emergency alerts on all channels",
                "🛣️  Open designated evacuation routes",
            ]
        },
        "High": {
            "severity" : "HIGH",
            "color"    : "ORANGE",
            "emoji"    : "🟠",
            "headline" : f"HIGH WILDFIRE RISK ALERT — {location_name}",
            "message"  : (
                f"High wildfire risk detected near {location_name}. "
                f"Ignition probability: {probability*100:.1f}%. "
                f"Estimated spread: {spread_radius:.1f} km. "
                f"Emergency services should prepare immediately."
            ),
            "actions"  : [
                "🚒 Fire departments move to highest alert level",
                "📋 Activate evacuation plans for high-risk zones",
                "🏫 Alert schools and hospitals to prepare",
                "📡 Monitor weather conditions continuously",
            ]
        },
        "Medium": {
            "severity" : "MEDIUM",
            "color"    : "YELLOW",
            "emoji"    : "🟡",
            "headline" : f"MODERATE WILDFIRE RISK — {location_name}",
            "message"  : (
                f"Moderate wildfire risk detected near {location_name}. "
                f"Ignition probability: {probability*100:.1f}%. "
                f"Estimated spread: {spread_radius:.1f} km. "
                f"Authorities should remain on standby."
            ),
            "actions"  : [
                "👀 Increase monitoring frequency",
                "🚒 Fire departments on standby",
                "📢 Issue public awareness notifications",
            ]
        },
        "Low": {
            "severity" : "LOW",
            "color"    : "GREEN",
            "emoji"    : "🟢",
            "headline" : f"LOW WILDFIRE RISK — {location_name}",
            "message"  : (
                f"Low wildfire risk near {location_name}. "
                f"Ignition probability: {probability*100:.1f}%. "
                f"Continue routine monitoring."
            ),
            "actions"  : [
                "📊 Continue routine weather monitoring",
                "✅ No immediate action required",
            ]
        },
    }

    cat      = risk_category if risk_category in alert_templates else "Low"
    template = alert_templates[cat]

    return {
        "alert_id"          : f"WFA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp"         : timestamp,
        "severity"          : template["severity"],
        "color"             : template["color"],
        "emoji"             : template["emoji"],
        "headline"          : template["headline"],
        "message"           : template["message"],
        "recommended_actions": template["actions"],
        "location"          : location_name,
        "probability_pct"   : round(probability * 100, 1),
        "spread_radius_km"  : round(spread_radius, 2),
        "population_at_risk": population_at_risk,
    }

# ── Tool 2: Format Final Report ───────────────────────────
@Tool
def format_final_report(
    location_name  : str,
    risk_category  : str,
    probability    : float,
    spread_radius  : float,
    population     : int,
    asset_counts   : str,
    alert_message  : str,
) -> str:
    """
    Format a comprehensive final wildfire assessment
    report combining all agent outputs into a
    human-readable summary for display on dashboard.
    Args:
        location_name: Affected location name
        risk_category: Risk level (Low/Medium/High/Critical)
        probability: Fire probability 0-1
        spread_radius: Spread radius in km
        population: Estimated affected population
        asset_counts: String summary of nearby assets
        alert_message: Generated alert message
    """
    emoji_map = {
        "Critical": "🔴", "High": "🟠",
        "Medium"  : "🟡", "Low" : "🟢"
    }
    emoji = emoji_map.get(risk_category, "⚪")
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""
╔══════════════════════════════════════════════════════╗
║    CALIFORNIA WILDFIRE EARLY WARNING SYSTEM          ║
║    Assessment Report — {ts}        ║
╚══════════════════════════════════════════════════════╝

{emoji} RISK ASSESSMENT
   Location       : {location_name}
   Risk Category  : {risk_category}
   Probability    : {probability*100:.1f}%
   Spread Radius  : {spread_radius:.1f} km

👥 POPULATION IMPACT
   People at Risk : {population:,}
   Assets Nearby  : {asset_counts}

🚨 ALERT
   {alert_message}

📋 Generated by: California Wildfire Early Warning System
"""
    return report.strip()
