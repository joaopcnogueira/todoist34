# 🚀 Migração para UV

Este documento explica a migração do projeto de `pip` + `requirements.txt` para `uv` + `pyproject.toml`.

## O que é o UV?

O [uv](https://docs.astral.sh/uv/) é um gerenciador de pacotes Python extremamente rápido, escrito em Rust pela Astral (criadores do Ruff). Ele é:

- **10-100x mais rápido** que pip
- **Gerencia ambientes virtuais automaticamente**
- **Compatível com pip** (usa o mesmo formato de dependências)
- **Lock file nativo** para builds reproduzíveis
- **Suporta workspaces** para monorepos

## Mudanças Realizadas

### 1. Criado `pyproject.toml`

Substituído `requirements.txt` por um arquivo `pyproject.toml` moderno seguindo a PEP 621:

```toml
[project]
name = "todoist"
version = "1.0.0"
description = "Gerenciador de tarefas com autenticação de usuários"
requires-python = ">=3.8"
dependencies = [...]
```

### 2. Atualizado `.gitignore`

Adicionadas as seguintes entradas:
- `.venv/` - ambiente virtual do uv
- `.python-version` - arquivo de versão Python
- `uv.lock` - lock file do uv

### 3. Atualizado `README.md`

Documentação atualizada com:
- Instruções de instalação do uv
- Comandos usando `uv sync` e `uv run`
- Remoção de referências ao pip

## Comandos Principais

### Instalação de Dependências

```bash
# Instala todas as dependências e cria o ambiente virtual
uv sync

# Adicionar nova dependência
uv add <pacote>

# Adicionar dependência de desenvolvimento
uv add --dev <pacote>

# Remover dependência
uv remove <pacote>
```

### Execução de Comandos

```bash
# Executar Python sem ativar o ambiente
uv run python main.py

# Executar uvicorn
uv run uvicorn main:app --reload

# Executar qualquer comando no ambiente
uv run <comando>
```

### Gerenciamento de Ambiente

```bash
# Atualizar todas as dependências
uv sync --upgrade

# Criar lock file
uv lock

# Mostrar dependências instaladas
uv pip list

# Ativar ambiente virtual manualmente (se preferir)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

## Compatibilidade com pip

O `uv` é compatível com pip. Se necessário, você ainda pode usar comandos pip:

```bash
uv pip install <pacote>
uv pip freeze
uv pip list
```

## Vantagens da Migração

✅ **Velocidade**: Instalação de dependências muito mais rápida
✅ **Simplicidade**: Não precisa criar/ativar ambiente virtual manualmente
✅ **Reproduzibilidade**: Lock file garante builds idênticos
✅ **Moderno**: Usa padrões atuais do Python (PEP 621)
✅ **Melhor DX**: Comandos mais simples e intuitivos

## Mantendo `requirements.txt` (Opcional)

Se você precisa manter `requirements.txt` para CI/CD legado ou outras ferramentas:

```bash
# Gerar requirements.txt a partir do pyproject.toml
uv pip compile pyproject.toml -o requirements.txt

# Ou exportar o lock file
uv export --format requirements-txt > requirements.txt
```

## Troubleshooting

### Conflitos com ambiente virtual antigo

Se você tinha um ambiente virtual antigo:

```bash
# Remova o ambiente antigo
rm -rf venv/

# Recrie com uv
uv sync
```

### Problemas com versões do Python

```bash
# Ver versão do Python sendo usada
uv python --version

# Usar versão específica do Python
uv python pin 3.11
```

## Recursos

- [Documentação oficial do uv](https://docs.astral.sh/uv/)
- [Guia de migração do pip](https://docs.astral.sh/uv/pip/compatibility/)
- [PEP 621 - Metadata do projeto](https://peps.python.org/pep-0621/)
