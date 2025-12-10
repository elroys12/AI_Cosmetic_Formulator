#!/bin/bash
# start.sh for Railway deployment

echo "🚀 Starting Novel Chemical ML Service..."
echo "🔧 Environment: $RAILWAY_ENVIRONMENT"
echo "🔧 PORT: $PORT"
echo "🔧 DATA_DIR: $DATA_DIR"

# Check if data directory exists
if [ -d "$DATA_DIR" ]; then
    echo "✅ Data directory exists: $DATA_DIR"
    echo "📁 Contents:"
    ls -la $DATA_DIR/
else
    echo "⚠️ Data directory not found: $DATA_DIR"
    mkdir -p $DATA_DIR
    echo "📁 Created data directory"
fi

# Start the application
echo "🚀 Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1