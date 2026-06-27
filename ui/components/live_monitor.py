
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

def render_live_monitor(lat: float, lon: float, loc_name: str):
    st.markdown(
        "<div class='main-header'>📡 Live Agent Monitoring</div>",
        unsafe_allow_html=True
    )
    st.markdown(f"#### 📍 Monitoring: {loc_name}")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            "Click **Run Full Assessment** to trigger "
            "all agents and see real-time output."
        )
    with col2:
        run_btn = st.button("🚀 Run Full Assessment", type="primary")

    if run_btn:
        st.markdown("---")
        st.markdown("### 🔄 Agent Pipeline Running...")

        progress = st.progress(0)
        status   = st.empty()

        # ── Agent 1 ───────────────────────────────────────
        status.markdown("**[1/3] 🌤️ Weather Intelligence Agent...**")
        progress.progress(10)
        with st.expander("🌤️ Weather Intelligence Agent", expanded=True):
            with st.spinner("Running..."):
                from tools.weather_tools  import (
                    get_latest_weather, get_fire_weather_index
                )
                from tools.wildfire_tools import (
                    predict_wildfire_risk, estimate_fire_spread
                )
                weather = get_latest_weather.function(lat, lon)
                fwi     = get_fire_weather_index.function(
                    weather["temperature"], weather["humidity"],
                    weather["wind_speed"],  weather["rainfall"],
                    weather["drought_index"]
                )
                risk    = predict_wildfire_risk.function(
                    temperature    = weather["temperature"],
                    humidity       = weather["humidity"],
                    wind_speed     = weather["wind_speed"],
                    wind_direction = weather["wind_direction"],
                    rainfall       = weather["rainfall"],
                    pressure       = weather["pressure"],
                    drought_index  = weather["drought_index"],
                )
                spread  = estimate_fire_spread.function(
                    wind_speed    = weather["wind_speed"],
                    humidity      = weather["humidity"],
                    temperature   = weather["temperature"],
                    drought_index = weather["drought_index"],
                )
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Temperature",   f"{weather['temperature']}°C")
            c2.metric("Humidity",      f"{weather['humidity']}%")
            c3.metric("Risk Category", risk["risk_category"])
            c4.metric("Probability",   f"{risk['percentage']}%")
            st.success(
                f"✅ Risk: {risk['risk_category']} "
                f"({risk['percentage']}%) | "
                f"Spread: {spread['spread_radius_km']} km"
            )

        progress.progress(40)

        # ── Agent 2 ───────────────────────────────────────
        status.markdown("**[2/3] 🚨 Alert Generation Agent...**")
        with st.expander("🚨 Alert Generation Agent", expanded=True):
            with st.spinner("Generating alert..."):
                from tools.alert_tools import generate_alert
                alert = generate_alert.function(
                    risk_category      = risk["risk_category"],
                    probability        = risk["probability"],
                    location_name      = loc_name,
                    spread_radius      = spread["spread_radius_km"],
                    population_at_risk = 0,
                )
            st.markdown(f"**{alert['emoji']} {alert['headline']}**")
            st.markdown(alert["message"])
            for action in alert["recommended_actions"]:
                st.markdown(f"- {action}")

        progress.progress(70)

        # ── Agent 3 ───────────────────────────────────────
        status.markdown("**[3/3] 🏗️ Infrastructure Agent...**")
        with st.expander("🏗️ Infrastructure Agent", expanded=True):
            with st.spinner("Scanning infrastructure..."):
                from tools.infra_tools import (
                    find_nearby_assets,
                    estimate_population_exposure
                )
                assets   = find_nearby_assets.function(
                    lat, lon,
                    radius_km = spread["spread_radius_km"]
                )
                exposure = estimate_population_exposure.function(
                    lat, lon,
                    radius_km = spread["spread_radius_km"]
                )
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Assets", assets["total_assets"])
            c2.metric("Houses",
                assets["counts_by_type"].get("house", 0))
            c3.metric("Hospitals",
                assets["counts_by_type"].get("hospital", 0))
            c4.metric("Population",
                exposure["estimated_population"])

        progress.progress(100)
        status.markdown("**✅ Pipeline Complete!**")

        st.session_state["last_risk"]    = risk
        st.session_state["last_weather"] = weather
        st.session_state["last_alert"]   = alert
        st.session_state["last_assets"]  = assets

        st.markdown("---")
        st.success(
            f"🎉 Assessment complete for {loc_name}! "
            f"Risk: **{risk['risk_category']}** "
            f"({risk['percentage']}%)"
        )

    # ── Historical Chart ──────────────────────────────────
    st.markdown("---")
    st.markdown("### 📈 30-Day FWI Score Trend")
    np.random.seed(42)
    dates  = pd.date_range(end=datetime.now(), periods=30, freq="D")
    scores = np.clip(
        np.random.normal(45, 15, 30) + np.linspace(0, 20, 30),
        0, 100
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x         = dates,
        y         = scores,
        mode      = "lines+markers",
        name      = "FWI Score",
        line      = dict(color="#FF4B4B", width=2),
        fill      = "tozeroy",
        fillcolor = "rgba(255,75,75,0.1)",
    ))
    fig.add_hline(
        y=60, line_dash="dash",
        line_color="orange",
        annotation_text="High Risk Threshold"
    )
    fig.add_hline(
        y=80, line_dash="dash",
        line_color="red",
        annotation_text="Critical Threshold"
    )
    fig.update_layout(
        title         = "30-Day FWI Score Trend",
        xaxis_title   = "Date",
        yaxis_title   = "FWI Score",
        height        = 350,
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        font          = dict(color="white"),
    )
    st.plotly_chart(fig, use_container_width=True)
