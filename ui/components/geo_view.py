
import streamlit as st
import folium
from streamlit_folium import st_folium
from tools.infra_tools    import find_nearby_assets
from tools.wildfire_tools import estimate_fire_spread
from tools.weather_tools  import get_latest_weather
import math

def render_geo_view(lat: float, lon: float, loc_name: str):
    st.markdown(
        "<div class='main-header'>🗺️ Geospatial View</div>",
        unsafe_allow_html=True
    )
    st.markdown(f"#### 📍 {loc_name}")
    st.markdown("---")

    # ── Controls ──────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        radius = st.slider("Search Radius (km)", 1.0, 25.0, 5.0, 0.5)
    with col2:
        show_assets = st.checkbox("Show Assets", True)
    with col3:
        show_plume  = st.checkbox("Show Plume Zone", True)

    # ── Load Data ─────────────────────────────────────────
    with st.spinner("Loading map data..."):
        weather = get_latest_weather.function(lat, lon)
        spread  = estimate_fire_spread.function(
            wind_speed    = weather["wind_speed"],
            humidity      = weather["humidity"],
            temperature   = weather["temperature"],
            drought_index = weather["drought_index"],
        )
        assets  = find_nearby_assets.function(
            lat, lon, radius_km=radius
        )

    # ── Build Map ─────────────────────────────────────────
    m = folium.Map(
        location  = [lat, lon],
        zoom_start = 11,
        tiles      = "CartoDB dark_matter",
    )

    # Fire origin
    folium.Marker(
        location = [lat, lon],
        popup    = folium.Popup(
            f"<b>🔥 Fire Origin</b><br>{loc_name}",
            max_width=200
        ),
        icon     = folium.Icon(color="red", icon="fire", prefix="fa"),
    ).add_to(m)

    # Spread radius
    folium.Circle(
        location     = [lat, lon],
        radius       = spread["spread_radius_km"] * 1000,
        color        = "#FF4B4B",
        fill         = True,
        fill_color   = "#FF4B4B",
        fill_opacity = 0.15,
        tooltip      = f"Fire Spread: {spread['spread_radius_km']} km",
    ).add_to(m)

    # Search radius
    folium.Circle(
        location   = [lat, lon],
        radius     = radius * 1000,
        color      = "#FFD700",
        fill       = False,
        dash_array = "10",
        tooltip    = f"Search Radius: {radius} km",
    ).add_to(m)

    # Assets
    if show_assets:
        asset_colors = {
            "house"           : "blue",
            "hospital"        : "red",
            "school"          : "orange",
            "transformer"     : "purple",
            "power_line"      : "gray",
            "shelter"         : "green",
            "emergency_center": "darkred",
        }
        for atype, asset_list in assets["nearest_assets"].items():
            color = asset_colors.get(atype, "blue")
            for asset in asset_list:
                folium.CircleMarker(
                    location     = [asset["latitude"], asset["longitude"]],
                    radius       = 6,
                    color        = color,
                    fill         = True,
                    fill_color   = color,
                    fill_opacity = 0.8,
                    tooltip      = f"{atype}: {asset['distance_km']}km",
                    popup        = folium.Popup(
                        f"<b>{atype.title()}</b><br>"
                        f"ID: {asset['asset_id']}<br>"
                        f"Distance: {asset['distance_km']} km",
                        max_width=200,
                    ),
                ).add_to(m)

    # Plume
    if show_plume:
        wind_dir_rad = math.radians(weather.get("wind_direction", 45))
        plume_dist   = spread["spread_radius_km"] * 0.01
        plume_lat    = lat + plume_dist * math.cos(wind_dir_rad)
        plume_lon    = lon + plume_dist * math.sin(wind_dir_rad)
        folium.PolyLine(
            locations  = [[lat, lon], [plume_lat, plume_lon]],
            color      = "#FF8C00",
            weight     = 4,
            dash_array = "10",
            tooltip    = "Smoke Plume Direction",
        ).add_to(m)
        folium.Circle(
            location     = [lat, lon],
            radius       = spread["impact_zones"]["extended_km"] * 1000,
            color        = "#FF8C00",
            fill         = True,
            fill_color   = "#FF8C00",
            fill_opacity = 0.08,
            tooltip      = "Smoke Plume Zone",
        ).add_to(m)

    # ── Display ───────────────────────────────────────────
    st_folium(m, width=1200, height=550)

    # ── Asset Summary ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🏗️ Assets Within Search Radius")
    counts = assets["counts_by_type"]
    icons  = {
        "house"           : "🏠",
        "hospital"        : "🏥",
        "school"          : "🏫",
        "transformer"     : "⚡",
        "power_line"      : "🔌",
        "shelter"         : "⛺",
        "emergency_center": "🚨",
    }
    if counts:
        cols = st.columns(len(counts))
        for i, (atype, count) in enumerate(counts.items()):
            icon = icons.get(atype, "📍")
            with cols[i]:
                st.metric(f"{icon} {atype.title()}", count)
    else:
        st.info("No assets found within search radius.")
