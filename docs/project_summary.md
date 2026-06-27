
# California Wildfire Early Warning System
## Project Summary

### Problem Statement
California wildfires cause billions in damage annually.
Current systems are REACTIVE — they detect fires after
ignition. Our system is PROACTIVE — it predicts risk
before ignition giving responders critical lead time.

### Solution
AI-powered multi-agent wildfire prediction system
running on AMD ROCm GPU via vLLM.

### Architecture

User Query

↓

Orchestrator Agent (Qwen3-30B-A3B on AMD GPU)

↓

┌─────────────────────────────────────────┐

│ Agent 1: Weather Intelligence           │

│   → Reads weather, calculates FWI       │

│   → Predicts wildfire probability       │

│                                         │

│ Agent 2: Alert Generation               │

│   → Generates emergency notifications  │

│   → Recommends specific actions         │

│                                         │

│ Agent 3: Infrastructure Assessment      │
│   → Scans nearby assets in radius      │

│   → Estimates population exposure      │

└─────────────────────────────────────────┘

↓

Real-time Streamlit Dashboard

### Key Metrics
| Metric              | Value          |
|---------------------|----------------|
| Test Pass Rate      | 100% (70/70)   |
| Risk Model AUC      | 0.80           |
| Risk Model Accuracy | 88%            |
| Pipeline Speed      | 7.84 seconds   |
| vLLM Latency        | 2.8 ms         |
| Cost per Assessment | $0.000329      |
| Weather Records     | 50,000         |
| Infrastructure      | 10,000 assets  |
| Historical Fires    | 5,000 incidents|

### Tech Stack
| Component      | Technology           |
|----------------|----------------------|
| LLM            | Qwen3-30B-A3B (MoE)  |
| LLM Serving    | vLLM                 |
| GPU            | AMD ROCm             |
| Agent Framework| Pydantic AI          |
| Risk Model     | XGBoost Classifier   |
| Plume Model    | XGBoost Regressor    |
| Geospatial     | GeoPy + Folium       |
| Dashboard      | Streamlit + Plotly   |

### Innovation Points
1. Multi-agent collaboration with reasoning trail
2. MCP protocol for standardized tool calling
3. Real-time risk simulation with auto-refresh
4. Geospatial fire spread visualization
5. End-to-end pipeline in under 8 seconds

### Future Roadmap
1. Real NASA/NOAA weather API integration
2. Satellite imagery fire detection
3. Evacuation route optimization
4. SMS/email alert broadcasting
5. Federal emergency API integration
