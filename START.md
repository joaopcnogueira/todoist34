# 🚀 Início Rápido - Todoist

## Para Iniciar a Aplicação

### 1. Instalar uv (primeira vez)

Se você ainda não tem o `uv` instalado:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Configurar Ambiente (primeira vez)

Execute o script de setup que faz tudo automaticamente:

```bash
./scripts/setup.sh
```

Ou manualmente:
```bash
uv sync
```

### 3. Iniciar o Servidor

**Opção 1 - Com script:**
```bash
./scripts/dev.sh
```

**Opção 2 - Comando direto:**
```bash
uv run python main.py
```

O servidor estará rodando em: **http://localhost:8000**

### 4. Acessar a Aplicação

Abra seu navegador e acesse:
```
http://localhost:8000
```

## 📝 Uso Rápido

### Primeira vez usando:

1. Clique em "Registre-se"
2. Crie sua conta com usuário, email e senha
3. Faça login com suas credenciais
4. Comece a adicionar tarefas!

### Funcionalidades:

- ✅ **Adicionar tarefas**: Digite o título e descrição (opcional)
- ☑️ **Marcar como concluída**: Clique no checkbox
- ✏️ **Editar**: Clique no botão "Editar"
- 🗑️ **Excluir**: Clique no botão "Excluir"

## 🧪 Testar a API

Execute o script de teste automatizado:

```bash
./test_api.sh
```

Ou teste manualmente usando a documentação interativa:
```
http://localhost:8000/docs
```

## 📚 Documentação Completa

Veja o arquivo [README.md](README.md) para documentação completa.

## 🛑 Para Parar o Servidor

Pressione `CTRL+C` no terminal onde o servidor está rodando.

---

**Pronto para começar!** 🎉
