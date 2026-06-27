FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libgdal-dev \
    gdal-bin \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV VLLM_BASE_URL=http://ollama:11434/v1
ENV LLM_MODEL_NAME=qwen2.5:7b
ENV VLLM_API_KEY=ollama
ENV DATASET_DIR=/app/datasets
ENV MODEL_DIR=/app/models/saved
ENV OPENAI_API_KEY=ollama

EXPOSE 8501

RUN chmod +x docker/entrypoint.sh

ENTRYPOINT ["docker/entrypoint.sh"]
