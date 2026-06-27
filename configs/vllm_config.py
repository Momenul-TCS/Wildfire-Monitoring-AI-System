
"""
vLLM Model Configuration for AMD ROCm GPU.
Documents the model setup and optimization flags.
"""

import os

VLLM_CONFIG = {
    "model"             : "Qwen/Qwen3-30B-A3B",
    "served_model_name" : "Qwen3-30B-A3B",
    "api_key"           : os.getenv("VLLM_API_KEY", "ollama"),
    "port"              : 8000,
    "device"            : "cuda",      # ROCm uses CUDA API
    "gpu_type"          : "AMD ROCm",

    # ── Performance Flags ─────────────────────────────────
    "env_flags": {
        "VLLM_USE_TRITON_FLASH_ATTN": "0",  # Disable for ROCm
    },

    # ── Serve Command ─────────────────────────────────────
    "serve_command": (
        "VLLM_USE_TRITON_FLASH_ATTN=0 "
        "vllm serve Qwen/Qwen3-30B-A3B "
        "--served-model-name Qwen3-30B-A3B "
        f"--api-key {os.getenv('VLLM_API_KEY', 'ollama')} "
        "--port 8000 "
        "--enable-auto-tool-choice "
        "--tool-call-parser hermes "
        "--trust-remote-code"
    ),

    # ── Model Specs ───────────────────────────────────────
    "model_specs": {
        "parameters"      : "30B",
        "active_params"   : "3B",      # MoE — only 3B active
        "architecture"    : "MoE",     # Mixture of Experts
        "context_length"  : 32768,
        "tool_calling"    : True,
        "tool_call_format": "hermes",
    },

    # ── API Integration ───────────────────────────────────
    "api": {
        "base_url"        : "http://localhost:8000/v1",
        "compatible_with" : "OpenAI API",
        "endpoints": [
            "/v1/models",
            "/v1/chat/completions",
        ],
    },
}

# ── AMD ROCm Optimization Notes ───────────────────────────
ROCM_NOTES = """
AMD ROCm Optimization for vLLM:

1. VLLM_USE_TRITON_FLASH_ATTN=0
   Disables Triton Flash Attention
   Prevents runtime errors on ROCm GPUs

2. Qwen3-30B-A3B (MoE Architecture)
   Only 3B parameters active per forward pass
   Efficient on AMD GPU memory
   Fast inference despite 30B total params

3. --tool-call-parser hermes
   Qwen3 uses Hermes tool calling format
   Required for agent tool use

4. OpenAI-compatible API
   Pydantic AI connects via OpenAI SDK
   No code changes needed to swap models
"""
