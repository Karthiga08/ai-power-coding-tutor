#!/bin/bash
# Production startup script for FastAPI backend

set -e  # Exit on error

echo "🚀 Starting AI Power Coding Tutor Backend..."

# Check required environment variables
required_vars=("DATABASE_URL" "JWT_SECRET" "AI_PROVIDER")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set"
        exit 1
    fi
done

echo "✓ Environment variables verified"

# Run database migrations (only if Alembic is initialized)
if [ -d "alembic" ]; then
    echo "📊 Running database migrations..."
    alembic upgrade head
    echo "✓ Migrations complete"
else
    echo "ℹ️  Alembic migrations not initialized (optional for development)"
fi

# Start the application
echo "🌐 Starting FastAPI application..."
echo "   Listening on 0.0.0.0:${PORT:-8000}"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-1} \
    --loop uvloop \
    --log-level ${LOG_LEVEL:-info}
