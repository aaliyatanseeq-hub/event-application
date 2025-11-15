#!/bin/bash

echo "🚀 Deploying Event Intelligence Platform..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one from .env.example"
    exit 1
fi

# Build and start containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "✅ Deployment complete!"
echo "🌐 Frontend: http://localhost"
echo "📡 API: http://localhost:8000"
echo "📊 Check logs: docker-compose logs -f"