# 📜 Scripts do Projeto

Scripts auxiliares para facilitar o desenvolvimento e execução do projeto.

## 📋 Scripts Disponíveis

### `setup.sh`

Configura o ambiente de desenvolvimento completo.

**O que faz:**
- Verifica se o `uv` está instalado
- Instala todas as dependências do projeto
- Cria o arquivo `.env` a partir do `.env.example` (se não existir)

**Uso:**
```bash
./scripts/setup.sh
```

**Quando usar:**
- Primeira vez configurando o projeto
- Após clonar o repositório
- Após adicionar novas dependências no `pyproject.toml`

---

### `dev.sh`

Inicia o servidor de desenvolvimento com hot-reload.

**O que faz:**
- Inicia o servidor usando `uvicorn` com a flag `--reload`
- Monitora mudanças nos arquivos e reinicia automaticamente
- Expõe o servidor em `0.0.0.0:8000` (acessível de outras máquinas)

**Uso:**
```bash
./scripts/dev.sh
```

**Quando usar:**
- Durante o desenvolvimento
- Quando você quer que o servidor reinicie automaticamente ao salvar arquivos
- Para testar a aplicação localmente

---

### `start.sh`

Inicia o servidor em modo produção.

**O que faz:**
- Inicia o servidor usando o arquivo `main.py`
- Não tem hot-reload (mais eficiente)
- Usa as configurações de produção

**Uso:**
```bash
./scripts/start.sh
```

**Quando usar:**
- Em ambiente de produção
- Quando não precisa de hot-reload
- Para testes de performance

---

## 🔧 Permissões

Se você encontrar o erro "Permission denied", execute:

```bash
chmod +x scripts/*.sh
```

## 💡 Dicas

1. **Use `make` para conveniência:**
   ```bash
   make dev    # ao invés de ./scripts/dev.sh
   make start  # ao invés de ./scripts/start.sh
   ```

2. **Scripts são wrapper de comandos uv:**
   - `./scripts/dev.sh` = `uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000`
   - `./scripts/start.sh` = `uv run python main.py`

3. **Customize conforme necessário:**
   - Os scripts são simples e podem ser editados para suas necessidades
   - Adicione variáveis de ambiente, flags extras, etc.

## 🆕 Criando Novos Scripts

Se você criar novos scripts:

1. Coloque-os neste diretório
2. Comece com o shebang: `#!/bin/bash`
3. Torne executável: `chmod +x scripts/seu_script.sh`
4. Documente aqui neste README
5. Adicione ao Makefile se for um comando comum

## 📚 Mais Informações

- [README.md principal](../README.md)
- [QUICKSTART_UV.md](../QUICKSTART_UV.md)
- [Makefile](../Makefile)
