#!/bin/bash
set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
MODEL="${LLM_MODEL_NAME:-qwen2.5:7b}"

echo "Waiting for Ollama at $OLLAMA_HOST..."
until curl -sf "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; do
    echo "  Ollama not ready yet, retrying in 3s..."
    sleep 3
done
echo "Ollama is up."

echo "Pulling model: $MODEL (this may take a while on first run)..."
curl -sf "$OLLAMA_HOST/api/pull" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$MODEL\"}" \
    --no-buffer \
    | grep -E '"status"' | tail -1 || true

echo "Model ready. Starting Streamlit dashboard..."
exec streamlit run ui/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --theme.base=dark \
    "--theme.primaryColor=#FF4B4B" \
    "--theme.backgroundColor=#0E1117" \
    "--theme.secondaryBackgroundColor=#1E1E2E" \
    "--theme.textColor=#FAFAFA"
