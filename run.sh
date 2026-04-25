#!/usr/bin/env bash
set -e

echo "Starting Discord RAG Chatbot App..."

if docker compose -f docker/docker_compose.yml ps -q | grep -q .; then
    docker compose -f docker/docker_compose.yml start
else
    docker compose -f docker/docker_compose.yml up -d
fi

echo ""
echo " - Application is running"
echo ""
echo "- Backend API:"
echo "   http://localhost:8000"
echo "   http://localhost:8000/docs"
echo ""
echo "- Prometheus API:"
echo "   http://localhost:9090"
echo ""
echo "- Grafana API:"
echo "   http://localhost:3000"
echo ""
echo ""
echo "- To stop the app run:"
echo "   ./stop.sh"
echo ""