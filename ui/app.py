
import streamlit as st

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title = "CA Wildfire Early Warning System",
    page_icon  = "🔥",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        padding: 1rem 0;
    }
    .risk-critical {
        background: #FF4B4B;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .risk-high {
        background: #FF8C00;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .risk-medium {
        background: #FFD700;
        color: black;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .risk-low {
        background: #32CD32;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .metric-card {
        background: #1E1E2E;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .stButton button {
        background: #FF4B4B;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ── Imports ───────────────────────────────────────────────
from ui.components.overview     import render_overview
from ui.components.live_monitor import render_live_monitor
from ui.components.geo_view     import render_geo_view

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔥 Wildfire System")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "📡 Live Monitoring",
            "🗺️  Geospatial View",
            "🤖 Agent Monitor",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 📍 Location")

    # California locations
    location_options = {
        "Los Angeles, CA"      : (34.05, -118.25),
        "San Francisco, CA"    : (37.77, -122.42),
        "San Diego, CA"        : (32.72, -117.16),
        "Sacramento, CA"       : (38.58, -121.49),
        "Fresno, CA"           : (36.74, -119.79),
        "Santa Barbara, CA"    : (34.42, -119.70),
        "Bakersfield, CA"      : (35.37, -119.02),
        "Redding, CA"          : (40.59, -122.39),
        "Custom Location"      : None,
    }

    selected_loc = st.selectbox(
        "Select Location",
        list(location_options.keys())
    )

    if selected_loc == "Custom Location":
        lat = st.number_input(
            "Latitude",  min_value=32.5,
            max_value=42.0, value=36.0
        )
        lon = st.number_input(
            "Longitude", min_value=-124.5,
            max_value=-114.0, value=-119.0
        )
        loc_name = st.text_input("Location Name", "Custom Location")
    else:
        lat, lon = location_options[selected_loc]
        loc_name = selected_loc

    st.session_state["latitude"]  = lat
    st.session_state["longitude"] = lon
    st.session_state["loc_name"]  = loc_name

    st.markdown("---")
    st.markdown("### ⚙️ System Info")
    import os
    st.markdown(f"**Model:** {os.environ.get('LLM_MODEL_NAME', 'qwen2.5:7b')}")
    st.markdown(f"**Backend:** Ollama")
    st.markdown(f"**API:** localhost:11434")

# ── Page Routing ──────────────────────────────────────────
if page == "🏠 Overview":
    render_overview(lat, lon, loc_name)

elif page == "📡 Live Monitoring":
    render_live_monitor(lat, lon, loc_name)

elif page == "🗺️  Geospatial View":
    render_geo_view(lat, lon, loc_name)

elif page == "🤖 Agent Monitor":
    st.markdown(
        "<div class=\'main-header\'>🤖 Agent Monitor</div>",
        unsafe_allow_html=True
    )
    st.markdown("### Agent Status")

    agents = [
        {"name": "Weather Intelligence", "icon": "🌤️",
         "status": "Ready", "color": "green"},
        {"name": "Alert Generation",     "icon": "🚨",
         "status": "Ready", "color": "green"},
        {"name": "Infrastructure",       "icon": "🏗️",
         "status": "Ready", "color": "green"},
        {"name": "Orchestrator",         "icon": "🎯",
         "status": "Ready", "color": "green"},
    ]

    cols = st.columns(4)
    for i, agent in enumerate(agents):
        with cols[i]:
            st.markdown(f"### {agent['icon']} {agent['name']}")
            st.success(f"✅ {agent['status']}")
            st.markdown(f"**Model:** {os.environ.get('LLM_MODEL_NAME', 'qwen2.5:7b')}")
            st.markdown(f"**Backend:** Ollama")

    # Show reasoning trail if available
    if "last_state" in st.session_state:
        state = st.session_state["last_state"]
        st.markdown("---")
        st.markdown("### 🧠 Last Reasoning Trail")
        for step in state.reasoning_trail:
            st.markdown(
                f"**[{step['step']}]** {step['detail']}"
            )
