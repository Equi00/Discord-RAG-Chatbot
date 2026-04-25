#!/usr/bin/env bash
set -e

echo "Starting Discord RAG Chatbot App..."

docker compose -f docker/docker_compose.yml up --build -d

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