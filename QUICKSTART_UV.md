# ⚡ Início Rápido com UV

Guia rápido para começar a usar o projeto com `uv`.

## 🚀 Primeiros Passos

### 1. Instale o uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone e Configure

```bash
# Entre no diretório do projeto
cd todoist34

# Instale as dependências (cria ambiente virtual automaticamente)
uv sync

# Ou use o script de setup
./scripts/setup.sh
```

### 3. Execute a Aplicação

**Opção A - Usando Make (mais fácil):**
```bash
make dev
```

**Opção B - Usando script:**
```bash
./scripts/dev.sh
```

**Opção C - Comando direto:**
```bash
uv run python main.py
```

### 4. Acesse

Abra o navegador em: http://localhost:8000

## 📦 Comandos Essenciais

### Gerenciar Dependências

```bash
# Adicionar pacote
uv add fastapi

# Adicionar pacote de desenvolvimento
uv add --dev pytest

# Remover pacote
uv remove <pacote>

# Atualizar todas as dependências
uv sync --upgrade

# Ver dependências instaladas
uv pip list
```

### Executar Comandos

```bash
# Executar Python
uv run python script.py

# Executar uvicorn com hot-reload
uv run uvicorn main:app --reload

# Executar qualquer comando no ambiente
uv run <comando>
```

### Atalhos com Make

```bash
make install    # Instala dependências
make dev        # Inicia servidor de desenvolvimento
make start      # Inicia servidor em produção
make test       # Executa testes
make clean      # Limpa arquivos temporários
make add PKG=requests  # Adiciona nova dependência
```

## 🎯 Por que UV é Melhor?

| Recurso | pip + venv | uv |
|---------|-----------|-----|
| Velocidade | Lento (minutos) | Ultrarrápido (segundos) |
| Criação de venv | Manual | Automático |
| Lock file | requirements.txt | uv.lock (determinístico) |
| Resolução de deps | Básica | Avançada e inteligente |
| Cache | Limitado | Global e eficiente |
| Linguagem | Python | Rust (mais performático) |

## 🔄 Migrando de pip

Se você já usava pip:

```bash
# Remova o ambiente virtual antigo
rm -rf venv/

# Instale com uv
uv sync

# Pronto! Continue trabalhando normalmente
```

## 📚 Recursos

- [Documentação do uv](https://docs.astral.sh/uv/)
- [README.md](README.md) - Documentação completa do projeto
- [MIGRATION_UV.md](MIGRATION_UV.md) - Detalhes da migração
- [START.md](START.md) - Guia de início rápido

## 💡 Dicas

1. **Não precisa ativar o ambiente virtual**: Use `uv run` para executar comandos
2. **Cache global**: O uv mantém um cache global, instalações subsequentes são instantâneas
3. **Lock file**: O `uv.lock` garante que todos tenham as mesmas versões
4. **Compatível com pip**: Pode usar `uv pip install` se precisar
5. **Make é seu amigo**: Use `make` para comandos comuns

## ❓ Problemas Comuns

### "uv: command not found"

Reinicie o terminal após instalar o uv, ou adicione ao PATH:

```bash
# macOS/Linux
export PATH="$HOME/.cargo/bin:$PATH"
```

### Conflito com ambiente virtual antigo

```bash
rm -rf venv/ .venv/
uv sync
```

### Dependência não encontrada

```bash
# Atualiza o lock file
uv lock

# Sincroniza novamente
uv sync
```

---

**Pronto para começar!** Execute `make dev` ou `uv run python main.py` 🚀
