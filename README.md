# 📝 Todoist - Gerenciador de Tarefas

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)

Aplicação web completa para gerenciamento de tarefas com autenticação de usuários, construída com FastAPI, SQLite e JavaScript vanilla.

## ✨ Funcionalidades

- **Autenticação de Usuários**
  - Registro de novos usuários
  - Login com JWT (JSON Web Tokens)
  - Sessões seguras

- **Gerenciamento de Tarefas (CRUD Completo)**
  - ✅ Criar novas tarefas
  - 📖 Visualizar todas as tarefas
  - ✏️ Editar tarefas existentes
  - 🗑️ Deletar tarefas
  - ☑️ Marcar tarefas como concluídas

- **Interface Responsiva**
  - Design moderno e intuitivo
  - Adaptável para desktop e mobile
  - Notificações toast para feedback do usuário

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **SQLite** - Banco de dados embutido
- **JWT** - Autenticação com tokens
- **Bcrypt** - Hash seguro de senhas
- **uv** - Gerenciador de pacotes ultrarrápido (10-100x mais rápido que pip)

### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Estilização moderna com variáveis CSS
- **JavaScript (Vanilla)** - Lógica e interação

### Por que uv?

Este projeto usa [uv](https://docs.astral.sh/uv/) em vez do pip tradicional:

- ⚡ **10-100x mais rápido** na instalação de pacotes
- 🔒 **Lock file automático** para builds reproduzíveis
- 🎯 **Gerenciamento de ambiente integrado** - não precisa criar venv manualmente
- 🦀 **Escrito em Rust** - extremamente performático
- 🔄 **Compatível com pip** - mesma sintaxe e ecossistema
- 📦 **Resoluções de dependência mais inteligentes**

Para mais detalhes sobre a migração, veja [MIGRATION_UV.md](MIGRATION_UV.md).

## 📋 Pré-requisitos

- Python 3.8 ou superior
- [uv](https://docs.astral.sh/uv/) - Gerenciador de pacotes Python ultrarrápido

### Instalando o uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 🚀 Instalação e Execução

### 1. Clone ou baixe o projeto

```bash
cd todoist34
```

### 2. Instale as dependências

O `uv` cria automaticamente o ambiente virtual e instala as dependências:

```bash
uv sync
```

### 3. Configure as variáveis de ambiente

O arquivo `.env` já está configurado com valores padrão para desenvolvimento. Para produção, altere a `SECRET_KEY`:

```env
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./todoist.db
```

### 4. Execute a aplicação

Com `uv`, você pode executar a aplicação diretamente sem ativar o ambiente virtual:

```bash
uv run python main.py
```

Ou usando uvicorn diretamente:

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Alternativa:** Se preferir ativar o ambiente virtual manualmente:

```bash
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate     # Windows

python main.py
```

### 5. Acesse a aplicação

Abra seu navegador e acesse:
```
http://localhost:8000
```

## 🛠️ Scripts e Comandos Úteis

### Usando Make (recomendado)

O projeto inclui um Makefile com comandos convenientes:

```bash
make install    # Instala dependências
make dev        # Inicia servidor de desenvolvimento
make start      # Inicia servidor em produção
make test       # Executa testes da API
make clean      # Limpa arquivos temporários
make lock       # Atualiza lock file
make add PKG=fastapi  # Adiciona nova dependência
```

### Usando Scripts Shell

Alternativamente, use os scripts diretamente:

```bash
./scripts/setup.sh    # Configurar ambiente completo
./scripts/dev.sh      # Iniciar servidor de desenvolvimento
./scripts/start.sh    # Iniciar servidor em produção
```

### Comandos uv Diretos

Ou use comandos `uv` diretamente:

```bash
uv sync                              # Sincronizar dependências
uv add <pacote>                      # Adicionar dependência
uv run python main.py                # Executar aplicação
uv run uvicorn main:app --reload    # Executar com hot-reload
```

## 📁 Estrutura do Projeto

```
todoist34/
├── backend/
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py       # Configuração do SQLAlchemy
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # Modelo de usuário
│   │   └── task.py             # Modelo de tarefa
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Schemas Pydantic de usuário
│   │   └── task.py             # Schemas Pydantic de tarefa
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py             # Rotas de autenticação
│   │   └── tasks.py            # Rotas de tarefas
│   ├── services/
│   │   ├── __init__.py
│   │   └── security.py         # Segurança e JWT
│   └── __init__.py
├── scripts/
│   ├── setup.sh                # Configuração do ambiente
│   ├── dev.sh                  # Iniciar em desenvolvimento
│   └── start.sh                # Iniciar em produção
├── static/
│   ├── css/
│   │   └── styles.css          # Estilos da aplicação
│   └── js/
│       └── app.js              # Lógica do frontend
├── templates/
│   └── index.html              # Página principal
├── main.py                     # Arquivo principal FastAPI
├── pyproject.toml              # Dependências e configuração (uv)
├── requirements.txt            # Dependências (legado, mantido para compatibilidade)
├── Makefile                    # Comandos make para desenvolvimento
├── .env                        # Variáveis de ambiente
├── .env.example                # Exemplo de variáveis
├── .gitignore                  # Arquivos ignorados pelo Git
├── CLAUDE.md                   # Padrões de código
├── MIGRATION_UV.md             # Guia de migração para uv
├── START.md                    # Início rápido
└── README.md                   # Este arquivo
```

## 🔑 API Endpoints

### Autenticação

- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Fazer login
- `GET /api/auth/me` - Obter dados do usuário atual

### Tarefas

- `GET /api/tasks` - Listar todas as tarefas do usuário
- `POST /api/tasks` - Criar nova tarefa
- `GET /api/tasks/{id}` - Obter tarefa específica
- `PUT /api/tasks/{id}` - Atualizar tarefa
- `DELETE /api/tasks/{id}` - Deletar tarefa

## 📖 Como Usar

### 1. Criar uma Conta
- Acesse a aplicação
- Clique em "Registre-se"
- Preencha usuário, email e senha (mínimo 6 caracteres)
- Clique em "Registrar"

### 2. Fazer Login
- Digite seu usuário e senha
- Clique em "Entrar"

### 3. Adicionar Tarefas
- Digite o título da tarefa no campo "O que você precisa fazer?"
- Opcionalmente, adicione uma descrição
- Clique em "+ Adicionar"

### 4. Gerenciar Tarefas
- **Marcar como concluída**: Clique no checkbox ao lado da tarefa
- **Editar**: Clique no botão "Editar"
- **Excluir**: Clique no botão "Excluir"

## 🔒 Segurança

- Senhas são criptografadas com bcrypt antes de serem armazenadas
- Autenticação baseada em JWT com tokens que expiram
- Proteção contra SQL Injection (SQLAlchemy ORM)
- Proteção contra XSS (escape de HTML no frontend)
- CORS configurado para permitir apenas origens autorizadas

## 🎨 Características da Interface

- Design moderno com gradientes e sombras
- Feedback visual para todas as ações
- Notificações toast elegantes
- Modal para edição de tarefas
- Estatísticas de tarefas em tempo real
- Ordenação inteligente (tarefas ativas primeiro)
- Responsivo para todos os tamanhos de tela

## 🧪 Testando a API

Você pode testar a API usando a documentação interativa do FastAPI:

```
http://localhost:8000/docs
```

Ou a alternativa ReDoc:

```
http://localhost:8000/redoc
```

## 📚 Documentação Adicional

Este projeto possui documentação completa para diferentes propósitos.

> 💡 **Procurando algo específico?** Veja o [INDEX.md](INDEX.md) - Índice completo de toda a documentação

### Início Rápido
- 🚀 [START.md](START.md) - Guia rápido para começar
- ⚡ [QUICKSTART_UV.md](QUICKSTART_UV.md) - Início rápido com uv

### Migração e UV
- 🔄 [MIGRATION_UV.md](MIGRATION_UV.md) - Guia completo de migração para uv
- 📊 [UV_VS_PIP.md](UV_VS_PIP.md) - Comparação detalhada uv vs pip
- ✅ [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - Resumo da migração
- ✓ [CHECKLIST_MIGRATION.md](CHECKLIST_MIGRATION.md) - Checklist de validação

### Desenvolvimento
- 📜 [scripts/README.md](scripts/README.md) - Documentação dos scripts
- 📝 [CLAUDE.md](CLAUDE.md) - Padrões de código do projeto
- 📖 [INDEX.md](INDEX.md) - Índice de toda a documentação

## 📝 Padrões de Código

Este projeto segue os padrões definidos em [CLAUDE.md](CLAUDE.md):

- Nomes descritivos e autoexplicativos em inglês
- Documentação em português do Brasil
- Funções pequenas com responsabilidade única
- Comentários apenas quando agregam valor
- Código legível e fácil de manter

## 🤝 Contribuindo

Sinta-se à vontade para contribuir com melhorias:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto e está disponível para uso livre.

## 🐛 Problemas Conhecidos

- Nenhum problema conhecido no momento

## 🚀 Melhorias Futuras

Possíveis melhorias para versões futuras:

- [ ] Categorias/tags para tarefas
- [ ] Data de vencimento para tarefas
- [ ] Prioridades (alta, média, baixa)
- [ ] Filtros e busca de tarefas
- [ ] Compartilhamento de tarefas entre usuários
- [ ] Notificações por email
- [ ] Temas claro/escuro
- [ ] PWA (Progressive Web App)

---

Desenvolvido com ❤️ usando FastAPI e JavaScript
