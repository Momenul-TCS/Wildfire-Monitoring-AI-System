import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    Central configuration for the Wildfire System.
    All values can be overridden via environment variables.
    """

    # ── Project ───────────────────────────────────────
    PROJECT_NAME: str = "California Wildfire Early Warning System"
    VERSION: str = "1.0.0"
    BASE_DIR: str = "/app"

    # ── LLM (Ollama / OpenAI-compatible) ─────────────
    VLLM_BASE_URL: str = Field(
        default="http://localhost:11434/v1",
        description="Ollama (or any OpenAI-compatible) server URL"
    )
    VLLM_API_KEY: str = Field(
        default="ollama",
        description="API key — Ollama accepts any value"
    )
    LLM_MODEL_NAME: str = Field(
        default="qwen2.5:7b",
        description="Model name served by Ollama"
    )

    # ── Datasets ──────────────────────────────────────
    DATASET_DIR: str = Field(default="/app/datasets")
    WEATHER_DATASET: str = "weather_data.csv"
    INFRA_DATASET: str = "infrastructure_data.csv"
    FIRE_DATASET: str = "historical_fires.csv"

    # ── Model ─────────────────────────────────────────
    MODEL_DIR: str = Field(default="/app/models/saved")
    RISK_MODEL_FILE: str = "risk_model.pkl"
    PLUME_MODEL_FILE: str = "plume_model.pkl"

    # ── Risk Thresholds ───────────────────────────────
    RISK_LOW_THRESHOLD: float = 0.25
    RISK_MEDIUM_THRESHOLD: float = 0.50
    RISK_HIGH_THRESHOLD: float = 0.75
    RISK_CRITICAL_THRESHOLD: float = 0.90

    # ── Geospatial ────────────────────────────────────
    CA_LAT_MIN: float = 32.5
    CA_LAT_MAX: float = 42.0
    CA_LON_MIN: float = -124.5
    CA_LON_MAX: float = -114.0
    DEFAULT_SEARCH_RADIUS_KM: float = 5.0

    # ── GPU ───────────────────────────────────────────
    USE_GPU: bool = False
    GPU_DEVICE: str = "cpu"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Singleton instance
settings = Settings()
