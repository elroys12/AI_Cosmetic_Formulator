#!/bin/bash
# start.sh - Startup script for ML Service

echo "🚀 Starting Novel Chemical ML Service..."
echo "=================================================="

# Display environment info
echo "📋 Environment Information:"
echo "   Service: $APP_NAME"
echo "   Version: $APP_VERSION"
echo "   Environment: ${RAILWAY_ENVIRONMENT:-local}"
echo "   Port: $PORT"
echo "   Data Directory: ${DATA_DIR:-data}"
echo "   Debug Mode: ${DEBUG:-false}"
echo "   Gemini API: ${GEMINI_API_KEY:+✅ SET}${GEMINI_API_KEY:-❌ NOT SET}"

# Check data directory
DATA_DIR="${DATA_DIR:-data}"
echo -e "\n📂 Checking data directory: $DATA_DIR"

if [ -d "$DATA_DIR" ]; then
    echo "✅ Data directory exists"
    echo "📁 Contents:"
    ls -la "$DATA_DIR/" || echo "   (Could not list contents)"
else
    echo "⚠️  Data directory not found: $DATA_DIR"
    echo "   Creating directory..."
    mkdir -p "$DATA_DIR"
fi

# Check for required CSV files
REQUIRED_FILES=(
    "chemicals_with_embeddings.csv"
    "products_with_embeddings.csv"
    "relations_with_embeddings.csv"
)

echo -e "\n🔍 Checking required data files:"
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$DATA_DIR/$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ⚠️  $file (not found - system will use fallback)"
    fi
done

# Determine mode
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "\n⚡ MODE: REAL DATA FALLBACK"
    echo "   System will use CSV data without Gemini API"
else
    echo -e "\n⚡ MODE: GEMINI + CREWAI"
    echo "   System will use Gemini API with CrewAI"
fi

# Start the application
echo -e "\n🚀 Starting application..."
echo "=================================================="

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --timeout-keep-alive 300 \
    --log-level info