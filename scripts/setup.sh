#!/bin/bash
# Script para configurar o ambiente de desenvolvimento

echo "📦 Instalando dependências com uv..."

# Verifica se uv está instalado
if ! command -v uv &> /dev/null; then
    echo "❌ uv não está instalado!"
    echo "Instale com: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Sincroniza dependências
uv sync

# Cria arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
fi

echo "✅ Ambiente configurado com sucesso!"
echo ""
echo "Para iniciar o servidor:"
echo "  ./scripts/dev.sh"
echo ""
echo "Ou manualmente:"
echo "  uv run python main.py"
