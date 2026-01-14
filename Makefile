.PHONY: help install dev start test clean

help:
	@echo "🚀 Comandos disponíveis:"
	@echo ""
	@echo "  make install    - Instala dependências com uv"
	@echo "  make dev        - Inicia servidor de desenvolvimento"
	@echo "  make start      - Inicia servidor em modo produção"
	@echo "  make test       - Executa testes da API"
	@echo "  make clean      - Remove arquivos temporários"
	@echo "  make lock       - Atualiza uv.lock"
	@echo "  make add        - Adiciona dependência (use: make add PKG=nome-pacote)"
	@echo ""

install:
	@echo "📦 Instalando dependências com uv..."
	@uv sync
	@echo "✅ Dependências instaladas!"

dev:
	@echo "🚀 Iniciando servidor de desenvolvimento..."
	@uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

start:
	@echo "🚀 Iniciando servidor..."
	@uv run python main.py

test:
	@echo "🧪 Executando testes da API..."
	@chmod +x test_api.sh
	@./test_api.sh

clean:
	@echo "🧹 Limpando arquivos temporários..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "✅ Limpeza concluída!"

lock:
	@echo "🔒 Atualizando lock file..."
	@uv lock
	@echo "✅ Lock file atualizado!"

add:
	@if [ -z "$(PKG)" ]; then \
		echo "❌ Erro: especifique um pacote. Uso: make add PKG=nome-pacote"; \
		exit 1; \
	fi
	@echo "📦 Adicionando $(PKG)..."
	@uv add $(PKG)
	@echo "✅ $(PKG) adicionado!"
