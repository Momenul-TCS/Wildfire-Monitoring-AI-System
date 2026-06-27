
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
from datetime import datetime
from tools.weather_tools  import get_latest_weather, get_fire_weather_index
from tools.wildfire_tools import predict_wildfire_risk, estimate_fire_spread

def _simulate_dynamic_weather(base_weather: dict) -> dict:
    """Simulate changing weather conditions."""
    # Use current second to create variation
    seed = int(time.time() / 15)  # changes every 15 seconds
    rng  = np.random.RandomState(seed)

    # Randomly pick a scenario
    scenario = rng.choice(["critical", "high", "medium", "low"])

    scenarios = {
        "critical": {
            "temperature"   : round(rng.uniform(38, 45), 1),
            "humidity"      : round(rng.uniform(5,  15), 1),
            "wind_speed"    : round(rng.uniform(60, 100), 1),
            "wind_direction": round(rng.uniform(0, 360), 1),
            "rainfall"      : round(rng.uniform(0, 0.5), 2),
            "pressure"      : round(rng.uniform(998, 1005), 1),
            "drought_index" : round(rng.uniform(8.5, 10), 2),
        },
        "high": {
            "temperature"   : round(rng.uniform(32, 38), 1),
            "humidity"      : round(rng.uniform(15, 30), 1),
            "wind_speed"    : round(rng.uniform(35, 60), 1),
            "wind_direction": round(rng.uniform(0, 360), 1),
            "rainfall"      : round(rng.uniform(0, 2), 2),
            "pressure"      : round(rng.uniform(1003, 1010), 1),
            "drought_index" : round(rng.uniform(6.5, 8.5), 2),
        },
        "medium": {
            "temperature"   : round(rng.uniform(25, 32), 1),
            "humidity"      : round(rng.uniform(30, 50), 1),
            "wind_speed"    : round(rng.uniform(15, 35), 1),
            "wind_direction": round(rng.uniform(0, 360), 1),
            "rainfall"      : round(rng.uniform(1, 5), 2),
            "pressure"      : round(rng.uniform(1008, 1015), 1),
            "drought_index" : round(rng.uniform(4, 6.5), 2),
        },
        "low": {
            "temperature"   : round(rng.uniform(10, 25), 1),
            "humidity"      : round(rng.uniform(55, 90), 1),
            "wind_speed"    : round(rng.uniform(0, 15), 1),
            "wind_direction": round(rng.uniform(0, 360), 1),
            "rainfall"      : round(rng.uniform(5, 30), 2),
            "pressure"      : round(rng.uniform(1013, 1025), 1),
            "drought_index" : round(rng.uniform(0, 4), 2),
        },
    }

    w = base_weather.copy()
    w.update(scenarios[scenario])
    return w, scenario

def render_overview(lat: float, lon: float, loc_name: str):
    st.markdown(
        "<div class='main-header'>🔥 California Wildfire Early Warning System</div>",
        unsafe_allow_html=True
    )
    st.markdown(f"#### 📍 {loc_name}")

    # ── Auto refresh ──────────────────────────────────────
    col_title, col_refresh = st.columns([4, 1])
    with col_refresh:
        refresh = st.button("🔄 Refresh Now")
    st.markdown("---")

    # ── Auto-refresh every 15 seconds ────────────────────
    refresh_interval = 15
    placeholder = st.empty()

    # ── Load base weather once ────────────────────────────
    with st.spinner("Loading weather data..."):
        base_weather = get_latest_weather.function(lat, lon)
        weather, scenario = _simulate_dynamic_weather(base_weather)

        fwi   = get_fire_weather_index.function(
            weather["temperature"], weather["humidity"],
            weather["wind_speed"],  weather["rainfall"],
            weather["drought_index"]
        )
        risk  = predict_wildfire_risk.function(
            temperature    = weather["temperature"],
            humidity       = weather["humidity"],
            wind_speed     = weather["wind_speed"],
            wind_direction = weather["wind_direction"],
            rainfall       = weather["rainfall"],
            pressure       = weather["pressure"],
            drought_index  = weather["drought_index"],
        )
        spread = estimate_fire_spread.function(
            wind_speed    = weather["wind_speed"],
            humidity      = weather["humidity"],
            temperature   = weather["temperature"],
            drought_index = weather["drought_index"],
        )

    # ── Timestamp ─────────────────────────────────────────
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(
        f"🕐 Last updated: {now}  |  "
        f"🔄 Auto-refreshes every {refresh_interval}s  |  "
        f"📡 Simulated scenario: **{scenario.upper()}**"
    )

    # ── Risk Badge ────────────────────────────────────────
    cat       = risk["risk_category"]
    css_class = f"risk-{cat.lower()}"
    emoji_map = {
        "Critical": "🔴", "High"  : "🟠",
        "Medium"  : "🟡", "Low"   : "🟢"
    }
    emoji = emoji_map.get(cat, "⚪")
    pct   = risk["percentage"]

    st.markdown(
        f"<div class='{css_class}'>"
        f"{emoji} {cat.upper()} WILDFIRE RISK — "
        f"{pct}% Probability"
        f"</div>",
        unsafe_allow_html=True
    )
    st.markdown("")

    # ── Key Metrics ───────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🌡️ Temperature",  f"{weather['temperature']}°C")
    c2.metric("💧 Humidity",      f"{weather['humidity']}%")
    c3.metric("💨 Wind Speed",    f"{weather['wind_speed']} km/h")
    c4.metric("🌵 Drought Index", f"{weather['drought_index']}/10")
    c5.metric("🔥 FWI Score",     f"{fwi['fwi_score']}")

    st.markdown("---")

    # ── Charts ────────────────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.markdown("### 📊 Fire Weather Components")
        components = fwi["components"]
        fig = go.Figure(go.Bar(
            x           = list(components.values()),
            y           = list(components.keys()),
            orientation = "h",
            marker_color = [
                "#FF4B4B" if v > 60 else
                "#FF8C00" if v > 40 else
                "#FFD700" if v > 20 else "#32CD32"
                for v in components.values()
            ],
        ))
        fig.update_layout(
            title         = "FWI Component Scores (0-100)",
            xaxis         = dict(range=[0, 100]),
            height        = 300,
            paper_bgcolor = "rgba(0,0,0,0)",
            plot_bgcolor  = "rgba(0,0,0,0)",
            font          = dict(color="white"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("### 💨 Impact Zones")
        zones  = spread["impact_zones"]
        labels = ["Immediate", "Nearby", "Extended"]
        vals   = [
            zones["immediate_km"],
            zones["nearby_km"],
            zones["extended_km"],
        ]
        colors = ["#FF4B4B", "#FF8C00", "#FFD700"]
        fig2   = go.Figure()
        for label, val, color in zip(labels, vals, colors):
            fig2.add_trace(go.Bar(
                x            = [label],
                y            = [val],
                name         = f"{label}: {val}km",
                marker_color = color,
            ))
        fig2.update_layout(
            title         = "Impact Zone Radii (km)",
            height        = 300,
            paper_bgcolor = "rgba(0,0,0,0)",
            plot_bgcolor  = "rgba(0,0,0,0)",
            font          = dict(color="white"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Alert ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🚨 Current Alert Status")
    action = risk["recommended_action"]

    if cat == "Critical":
        st.error(f"🔴 CRITICAL: {action}")
    elif cat == "High":
        st.warning(f"🟠 HIGH RISK: {action}")
    elif cat == "Medium":
        st.warning(f"🟡 MEDIUM RISK: {action}")
    else:
        st.success(f"🟢 LOW RISK: {action}")

    # ── Spread ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔥 Fire Spread Estimate")
    s1, s2, s3 = st.columns(3)
    s1.metric("Immediate Zone", f"{zones['immediate_km']} km")
    s2.metric("Nearby Zone",    f"{zones['nearby_km']} km")
    s3.metric("Extended Zone",  f"{zones['extended_km']} km")

    # ── Auto-refresh trigger ──────────────────────────────
    st.markdown("---")
    st.caption(
        f"⏱️ Next auto-refresh in ~{refresh_interval} seconds. "
        f"Or click 🔄 Refresh Now above."
    )
    time.sleep(refresh_interval)
    st.rerun()
