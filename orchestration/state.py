
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class WildfireSystemState:
    """
    Shared state passed between all agents
    by the Orchestrator. Maintains full
    workflow context and reasoning trail.
    """
    # ── Input ──────────────────────────────────────────
    latitude          : float = 0.0
    longitude         : float = 0.0
    location_name     : str   = ""
    triggered_at      : str   = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # ── Agent 1 Output ─────────────────────────────────
    temperature       : float = 0.0
    humidity          : float = 0.0
    wind_speed        : float = 0.0
    wind_direction    : float = 0.0
    drought_index     : float = 0.0
    fwi_score         : float = 0.0
    fire_probability  : float = 0.0
    risk_category     : str   = "Unknown"
    spread_radius_km  : float = 0.0
    weather_summary   : str   = ""

    # ── Agent 2 Output ─────────────────────────────────
    alert_id          : str       = ""
    alert_severity    : str       = ""
    alert_headline    : str       = ""
    alert_message     : str       = ""
    alert_actions     : list      = field(default_factory=list)

    # ── Agent 3 Output ─────────────────────────────────
    total_assets      : int   = 0
    houses            : int   = 0
    hospitals         : int   = 0
    schools           : int   = 0
    estimated_population: int = 0
    plume_direction   : str   = ""
    impact_summary    : str   = ""

    # ── Orchestrator ───────────────────────────────────
    reasoning_trail   : list  = field(default_factory=list)
    final_report      : str   = ""
    completed_at      : str   = ""

    def add_reasoning(self, step: str, detail: str):
        """Add a step to the reasoning trail."""
        self.reasoning_trail.append({
            "step"     : step,
            "detail"   : detail,
            "timestamp": datetime.now().isoformat(),
        })

    def to_summary(self) -> str:
        return (
            f"Location : {self.location_name}\n"
            f"Risk     : {self.risk_category} "
            f"({self.fire_probability:.1%})\n"
            f"Spread   : {self.spread_radius_km} km\n"
            f"People   : {self.estimated_population:,}\n"
            f"Alert    : {self.alert_severity}"
        )
