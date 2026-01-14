#!/bin/bash
# Script para iniciar o servidor de desenvolvimento com uv

echo "🚀 Iniciando servidor de desenvolvimento..."
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
