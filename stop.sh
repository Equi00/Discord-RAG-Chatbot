#!/usr/bin/env bash
set -e

echo "Stopping Discord RAG Chatbot App..."

docker compose -f docker/docker_compose.yml down

echo "App stopped"