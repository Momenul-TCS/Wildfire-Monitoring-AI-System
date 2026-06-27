<div align="center">

# 🔥 California Wildfire Early Warning System

**AI-powered proactive wildfire prediction and emergency response platform**

*Forecasting fire risk before ignition — giving emergency responders the lead time they need*

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![Pydantic AI](https://img.shields.io/badge/Pydantic_AI-Multi--Agent-orange)](https://docs.pydantic.dev/latest/concepts/pydantic_ai/)
[![vLLM](https://img.shields.io/badge/vLLM-Qwen3--30B-purple)](https://docs.vllm.ai)
[![XGBoost](https://img.shields.io/badge/XGBoost-AUC_0.80-green)](https://xgboost.readthedocs.io)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![AMD ROCm](https://img.shields.io/badge/GPU-AMD_ROCm-ED1C24?logo=amd&logoColor=white)](https://rocm.docs.amd.com)

</div>

---

## The Problem

Traditional wildfire systems are **reactive** — they detect fires *after* ignition. By then, evacuation windows are dangerously narrow and infrastructure is already at risk.

This system is **proactive**. It analyzes weather patterns, terrain conditions, and historical fire data to forecast risk *before* a fire starts — giving emergency responders critical lead time for evacuation planning and resource pre-positioning.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WILDFIRE EARLY WARNING PIPELINE                   │
│                                                                       │
│  Input: (latitude, longitude, location_name)                         │
│                          │                                           │
│                          ▼                                           │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  STEP 1 — WEATHER AGENT                                       │   │
│  │  • Retrieves real-time weather data                           │   │
│  │  • Calculates Fire Weather Index (FWI)                        │   │
│  │  • Predicts wildfire risk probability via XGBoost             │   │
│  │  • Estimates fire spread radius                               │   │
│  └────────────────────────────┬──────────────────────────────────┘   │
│                               ▼                                      │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  STEP 2 — ALERT AGENT                                         │   │
│  │  • Evaluates risk category (Low / Medium / High / Critical)   │   │
│  │  • Generates structured alert with severity & headline        │   │
│  │  • Produces recommended emergency response actions            │   │
│  └────────────────────────────┬──────────────────────────────────┘   │
│                               ▼                                      │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  STEP 3 — INFRASTRUCTURE AGENT                                │   │
│  │  • Finds all assets within fire spread radius                 │   │
│  │  • Counts houses, hospitals, schools at risk                  │   │
│  │  • Estimates population exposure                              │   │
│  │  • Calculates smoke plume direction                           │   │
│  └────────────────────────────┬──────────────────────────────────┘   │
│                               ▼                                      │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  ORCHESTRATOR — Synthesizes all agent outputs into final      │   │
│  │  report with full reasoning trail for explainability          │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  Output: Risk Score · Alert · Assets at Risk · Population · Report   │
└─────────────────────────────────────────────────────────────────────┘
```

**4 specialized AI agents** collaborate using the Pydantic AI framework, each powered by **Qwen3-30B-A3B** (Mixture of Experts, 3B active parameters) served via vLLM on AMD ROCm GPU.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Pipeline execution time | **7.84 seconds** |
| vLLM inference latency | **2.8 ms** |
| Cost per assessment | **$0.000329** |
| Test suite pass rate | **100%** |
| Risk Model AUC | **0.80** |
| Risk Model Accuracy | **88%** |
| Plume Model RMSE | **1.63 km** |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM Serving** | vLLM + Qwen3-30B-A3B (MoE) |
| **Agent Framework** | Pydantic AI (multi-agent orchestration) |
| **Risk Prediction** | XGBoost Classifier |
| **Smoke Plume Model** | XGBoost Regressor |
| **Geospatial** | GeoPy · Shapely · Folium |
| **Dashboard** | Streamlit · Plotly |
| **GPU Backend** | AMD ROCm |
| **Data Processing** | Pandas · NumPy · SciPy · Scikit-Learn |
| **Containerization** | Docker + Docker Compose |
| **Local LLM** | Ollama (development) |

---

## Quick Start

### Option 1 — Docker (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd wildfire_system

# Copy environment config
cp .env.example .env

# Start all services (Ollama + Dashboard)
docker compose -f docker/docker-compose.yml up --build
```

Dashboard available at `http://localhost:8501`

---

### Option 2 — Local Setup

#### Prerequisites

- Python 3.11+
- AMD ROCm GPU (for vLLM) **or** Ollama (CPU/any GPU)
- GDAL system library

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y gdal-bin libgdal-dev

# Install Python dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
```

#### Step 1 — Start the LLM Server

**Option A: vLLM with AMD ROCm GPU (Production)**

```bash
VLLM_USE_TRITON_FLASH_ATTN=0 \
vllm serve Qwen/Qwen3-30B-A3B \
    --served-model-name Qwen3-30B-A3B \
    --api-key abc-123 \
    --port 8000 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --trust-remote-code
```

**Option B: Ollama (Development)**

```bash
ollama pull qwen2.5:7b
ollama serve
```

#### Step 2 — Launch the Dashboard

```bash
python run_dashboard.py
```

#### Step 3 — Run a Programmatic Assessment

```python
import asyncio
from agents.orchestrator import run_orchestrator

async def main():
    output, state = await run_orchestrator(
        latitude=34.05,
        longitude=-118.25,
        location_name="Los Angeles, CA"
    )
    print(state.final_report)

asyncio.run(main())
```

---

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# LLM Endpoint — use Ollama URL for local dev, vLLM URL for production
VLLM_BASE_URL=http://localhost:11434/v1
VLLM_API_KEY=abc-123

# Model selection
LLM_MODEL_NAME=qwen2.5:7b          # Ollama dev
# LLM_MODEL_NAME=Qwen3-30B-A3B    # vLLM production

# Data paths (defaults work out of the box)
DATASET_DIR=datasets/
MODEL_DIR=models/saved/
```

---

## Project Structure

```
wildfire_system/
├── agents/                  # Pydantic AI agent definitions
│   ├── orchestrator.py      # Master coordinator
│   ├── weather_agent.py     # Weather intelligence
│   ├── alert_agent.py       # Alert generation
│   └── infra_agent.py       # Infrastructure assessment
│
├── orchestration/           # Pipeline & state management
│   ├── pipeline.py          # 3-step async pipeline
│   ├── state.py             # Shared state across agents
│   └── monitored_pipeline.py
│
├── models/
│   ├── saved/               # Pre-trained ML models
│   │   ├── risk_model.pkl   # XGBoost risk classifier
│   │   └── plume_model.pkl  # XGBoost plume regressor
│   └── vllm_integration.py  # vLLM health checks & token tracking
│
├── tools/                   # Pydantic AI tool functions
│   ├── weather_tools.py     # Weather data + FWI calculation
│   ├── wildfire_tools.py    # Risk & spread prediction
│   ├── alert_tools.py       # Alert template generation
│   └── infra_tools.py       # Asset proximity & population queries
│
├── configs/
│   ├── settings.py          # Pydantic settings (env-based)
│   ├── features.py          # ML feature definitions
│   └── vllm_config.py       # AMD ROCm configuration
│
├── datasets/
│   ├── weather_data.csv     # 50,000 CA weather records
│   ├── infrastructure_data.csv  # 10,000 CA infrastructure assets
│   ├── historical_fires.csv # 5,000 historical fire incidents
│   └── generate_datasets.py # Synthetic data generator
│
├── ui/                      # Streamlit dashboard
│   ├── app.py               # Main app with 4 navigation pages
│   └── components/
│       ├── overview.py      # Risk metrics overview
│       ├── live_monitor.py  # Real-time monitoring
│       └── geo_view.py      # Geospatial map visualization
│
├── docker/
│   ├── Dockerfile           # Python 3.11-slim image
│   ├── docker-compose.yml   # Ollama + App services
│   └── entrypoint.sh
│
├── tests/
│   ├── test_agents.py
│   └── test_models.py
│
├── docs/
│   └── project_summary.md   # Architecture & metrics overview
│
├── requirements.txt
├── .env.example
└── run_dashboard.py
```

---

## Datasets

| Dataset | Records | Description |
|---------|---------|-------------|
| `weather_data.csv` | 50,000 | California weather conditions with fire ignition labels |
| `infrastructure_data.csv` | 10,000 | CA infrastructure assets (houses, hospitals, schools, utilities) with lat/lon |
| `historical_fires.csv` | 5,000 | Historical California fire incident records |

Generate fresh synthetic datasets:

```bash
python datasets/generate_datasets.py
```

---

## ML Models

### Risk Classifier (XGBoost)

Predicts fire ignition probability from 10 engineered features:

| Feature | Description |
|---------|-------------|
| `heat_index` | Combined temperature + humidity stress |
| `wind_drought` | Wind speed × drought severity interaction |
| `fire_weather` | Composite fire weather score |
| `temp_humidity_ratio` | Dryness indicator |
| `wind_temp` | Wind-temperature combined risk |
| + 5 more | Seasonal, historical, terrain features |

**Performance**: AUC 0.80 · Accuracy 88%

### Plume Regressor (XGBoost)

Estimates smoke plume spread radius in km from 7 weather features.

**Performance**: RMSE 1.63 km · R² 0.20

---

## Risk Thresholds

| Category | Fire Probability | Response |
|----------|-----------------|----------|
| **Low** | < 25% | Routine monitoring |
| **Medium** | 25% – 50% | Heightened awareness, pre-position resources |
| **High** | 50% – 75% | Active preparation, notify emergency services |
| **Critical** | > 90% | Immediate evacuation, full emergency response |

---

## Dashboard Features

The Streamlit dashboard provides 4 navigation pages:

| Page | Features |
|------|----------|
| **Overview** | Risk score cards, FWI index, alert summary |
| **Live Monitor** | Auto-refreshing real-time assessment view |
| **Geospatial View** | Interactive Folium map with asset overlays and plume visualization |
| **Agent Monitor** | Per-agent reasoning trail, token usage, cost breakdown |

Pre-configured locations: Los Angeles · San Francisco · San Diego · Sacramento · Fresno · Santa Barbara · Bakersfield · Redding

---

## Assessment Output

Each pipeline run produces a structured `OrchestratorOutput`:

```python
{
  "risk_category": "HIGH",
  "fire_probability": 0.72,
  "fwi_score": 38.4,
  "spread_radius_km": 4.2,
  "plume_direction": "NE",

  "alert": {
    "alert_id": "WF-20260627-LA-001",
    "severity": "HIGH",
    "headline": "Elevated wildfire risk detected near Los Angeles",
    "recommended_actions": ["Pre-position air tankers", "Notify evacuation routes", ...]
  },

  "infrastructure": {
    "houses_at_risk": 1842,
    "hospitals_at_risk": 3,
    "schools_at_risk": 7,
    "total_assets": 2109,
    "estimated_population": 4320
  },

  "reasoning_trail": ["Weather analysis complete...", "Alert generated...", ...]
}
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Roadmap

- [ ] NASA/NOAA real-time satellite weather API integration
- [ ] Satellite imagery analysis for vegetation moisture
- [ ] Automated evacuation route optimization
- [ ] SMS/push alert notifications for residents
- [ ] Historical accuracy benchmarking against real CA fire events
- [ ] Multi-county simultaneous risk assessment

---

## License

This project is for research and emergency response planning purposes.

---

<div align="center">

**Built to protect communities before the fire starts.**

*Pydantic AI · vLLM · XGBoost · Streamlit · AMD ROCm*

</div>