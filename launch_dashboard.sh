#!/bin/bash
# Launch California Wildfire Dashboard locally (outside Docker)
# Run from the wildfire_system/ directory

echo "🔥 Starting California Wildfire Dashboard..."
echo "📍 URL: http://localhost:8501"
echo ""

streamlit run ui/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --theme.base dark \
    --theme.primaryColor "#FF4B4B" \
    --theme.backgroundColor "#0E1117" \
    --theme.secondaryBackgroundColor "#1E1E2E" \
    --theme.textColor "#FAFAFA"
