# Tutorial: Construindo um Gerenciador de Tarefas com FastAPI

Este tutorial guia você passo a passo na criação de uma aplicação completa de gerenciamento de tarefas usando FastAPI, SQLAlchemy, autenticação JWT e um frontend moderno.

**Público-alvo:** Desenvolvedores Python que querem aprender desenvolvimento web e nunca usaram FastAPI antes.

## 📋 Pré-requisitos

- Python 3.8+
- UV instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Conhecimento básico de Python

## 🎯 O que vamos construir

Uma aplicação web full-stack com:
- Backend FastAPI com autenticação JWT
- Banco de dados SQLite com SQLAlchemy ORM
- Sistema de usuários com senhas criptografadas (bcrypt)
- CRUD completo de tarefas
- Frontend responsivo com HTML/CSS/JS vanilla

---

## 🌐 Introdução: Como funciona uma aplicação web?

Antes de começar, é importante entender o básico de como aplicações web funcionam:

### Cliente-Servidor

```
┌─────────────┐         HTTP Request          ┌─────────────┐
│   Browser   │ ──────────────────────────────▶│   Server    │
│  (Cliente)  │                                 │  (FastAPI)  │
│             │◀────────────────────────────── │             │
└─────────────┘         HTTP Response          └─────────────┘
                                                       │
                                                       ▼
                                                ┌─────────────┐
                                                │  Database   │
                                                │  (SQLite)   │
                                                └─────────────┘
```

1. **Cliente (Browser)**: Envia requisições HTTP (GET, POST, PUT, DELETE)
2. **Servidor (FastAPI)**: Recebe requisições, processa lógica de negócio, acessa banco de dados
3. **Banco de Dados (SQLite)**: Armazena dados persistentes (usuários, tarefas)

### O que é uma API REST?

REST (Representational State Transfer) é um padrão para criar APIs. Uma API REST usa:

- **URLs** para identificar recursos: `/api/tasks/`, `/api/auth/login`
- **Métodos HTTP** para ações:
  - `GET`: buscar dados (ler)
  - `POST`: criar novos dados
  - `PUT`: atualizar dados existentes
  - `DELETE`: remover dados
- **JSON** para trocar dados entre cliente e servidor

Exemplo de requisição REST:
```
POST /api/tasks/
Content-Type: application/json

{
  "title": "Estudar FastAPI",
  "priority": "high"
}
```

### O que é FastAPI?

FastAPI é um framework web moderno para Python que:
- Cria APIs REST de forma simples e rápida
- Valida dados automaticamente usando type hints do Python
- Gera documentação automática (Swagger UI)
- É muito rápido (baseado em Starlette e Pydantic)

**Analogia**: Se Python fosse uma caixa de ferramentas, FastAPI seria uma furadeira elétrica - uma ferramenta especializada que facilita muito um trabalho específico (criar APIs).

---

## Parte 1: Estrutura Inicial do Projeto

### 1.1 Criar a estrutura de pastas

```bash
mkdir todoist34
cd todoist34

# Criar estrutura de diretórios
mkdir -p backend/{database,models,schemas,routes,services}
mkdir -p static/{css,js}
mkdir -p templates
mkdir -p scripts
```

**Por que essa estrutura?**

Esta é uma arquitetura em camadas, comum em aplicações web:

```
todoist34/
├── backend/              # Código Python do servidor
│   ├── database/         # Configuração do banco de dados
│   ├── models/           # Estrutura das tabelas (ORM)
│   ├── schemas/          # Validação de dados (entrada/saída)
│   ├── routes/           # Endpoints da API (URLs)
│   └── services/         # Lógica de negócio (segurança, etc)
├── static/               # Arquivos estáticos (CSS, JS)
├── templates/            # Arquivos HTML
└── main.py              # Ponto de entrada da aplicação
```

**Por que separar em camadas?**
- **Organização**: cada pasta tem uma responsabilidade específica
- **Manutenção**: fácil encontrar e modificar código
- **Escalabilidade**: fácil adicionar novas funcionalidades
- **Testabilidade**: fácil testar cada camada isoladamente

### 1.2 Inicializar o projeto com UV

```bash
# Inicializar projeto UV
uv init --no-workspace

# Adicionar dependências
uv add fastapi uvicorn sqlalchemy passlib python-jose python-multipart bcrypt

# IMPORTANTE: Fixar a versão do bcrypt para evitar problemas
uv add "bcrypt>=4.0.0,<5.0.0"
```

**O que cada dependência faz?**

- **fastapi**: o framework para criar a API
- **uvicorn**: servidor ASGI que executa o FastAPI (como o motor de um carro)
- **sqlalchemy**: ORM (Object-Relational Mapping) - transforma tabelas em classes Python
- **passlib**: biblioteca para fazer hash de senhas (criptografia)
- **python-jose**: biblioteca para criar e validar tokens JWT (autenticação)
- **python-multipart**: necessário para processar formulários HTTP
- **bcrypt**: algoritmo de hash usado pelo passlib

**O que é ORM?**

ORM (Object-Relational Mapping) permite trabalhar com banco de dados usando classes Python em vez de SQL puro.

Sem ORM (SQL):
```sql
INSERT INTO users (username, email) VALUES ('joao', 'joao@email.com');
SELECT * FROM users WHERE username = 'joao';
```

Com ORM (Python):
```python
user = User(username="joao", email="joao@email.com")
db.add(user)
user = db.query(User).filter(User.username == "joao").first()
```

**Por que fixar o bcrypt?**
A versão 5.x do bcrypt tem incompatibilidades com o `passlib`. Usar a versão 4.x garante estabilidade.

### 1.3 Criar arquivos `__init__.py`

```bash
touch backend/__init__.py
touch backend/database/__init__.py
touch backend/models/__init__.py
touch backend/schemas/__init__.py
touch backend/routes/__init__.py
touch backend/services/__init__.py
```

**O que são os `__init__.py`?**

Em Python, um diretório só é considerado um "pacote" (módulo importável) se tiver um arquivo `__init__.py`.

Sem `__init__.py`:
```python
from backend.models.user import User  # ❌ Erro: backend não é um pacote
```

Com `__init__.py`:
```python
from backend.models.user import User  # ✅ Funciona!
```

Esses arquivos podem ficar vazios - sua simples presença já é suficiente.

---

## Parte 2: Configuração do Banco de Dados

### 2.1 Por que precisamos de um banco de dados?

Quando você executa um programa Python normal, os dados ficam na memória RAM e são perdidos quando o programa termina.

```python
# Dados na memória (perdidos ao reiniciar)
users = []
users.append({"username": "joao"})  # Perdido ao fechar o programa
```

Um banco de dados armazena dados no disco - eles persistem mesmo após reiniciar o servidor.

**Por que SQLite?**
- É um arquivo único (`todoist.db`) - muito simples para desenvolvimento
- Não precisa instalar nenhum servidor de banco de dados
- Perfeito para aprender e prototipar

(Em produção, normalmente usa-se PostgreSQL ou MySQL)

### 2.2 O que é SQLAlchemy?

SQLAlchemy é a ferramenta que faz a ponte entre Python e o banco de dados.

```
Python Objects  ←→  SQLAlchemy ORM  ←→  SQL Database
   (Classes)         (Tradutor)         (Tabelas)
```

### 2.3 Criar `backend/database/connection.py`

```python
"""
Configuração da conexão com o banco de dados SQLite.

Este arquivo configura 3 coisas principais:
1. Engine: o "motor" que se conecta ao banco de dados
2. SessionLocal: fábrica para criar "sessões" (conexões temporárias)
3. Base: classe mãe para definir nossas tabelas
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL do banco de dados: sqlite:/// significa "arquivo local"
# ./todoist.db = arquivo na pasta atual
DATABASE_URL = "sqlite:///./todoist.db"

# ===== 1. ENGINE: Motor de conexão =====
# O engine gerencia a conexão física com o banco de dados
# Pense nele como o "motorista" que sabe como falar com o SQLite
engine = create_engine(
    DATABASE_URL,
    # check_same_thread=False: permite usar o banco em múltiplas threads
    # (necessário porque o FastAPI é assíncrono e usa múltiplas threads)
    connect_args={"check_same_thread": False}
)

# ===== 2. SESSIONLOCAL: Fábrica de sessões =====
# Uma "sessão" é como uma "conversa" temporária com o banco de dados
# Você abre uma sessão, faz operações, e fecha a sessão
# sessionmaker cria um "molde" para essas conversas

# autocommit=False: mudanças não são salvas automaticamente (você controla)
# autoflush=False: não envia comandos para o banco automaticamente
# bind=engine: vincula as sessões ao nosso engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===== 3. BASE: Classe mãe para models =====
# Todos os nossos models (User, Task) vão herdar desta classe
# Ela dá "superpoderes" ORM para nossas classes Python
Base = declarative_base()

# ===== DEPENDENCY INJECTION: Fornece sessão para cada requisição =====
def get_db():
    """
    Esta função é usada pelo FastAPI para fornecer uma sessão do banco
    para cada requisição HTTP.

    Como funciona:
    1. Cliente faz requisição → FastAPI chama get_db()
    2. get_db() cria uma nova sessão → yield db (fornece para a rota)
    3. Rota usa a sessão para acessar o banco
    4. Quando a rota termina → finally fecha a sessão

    Isso garante que:
    - Cada requisição tem sua própria sessão isolada
    - A sessão é SEMPRE fechada, mesmo se houver erro
    """
    db = SessionLocal()  # Cria uma nova sessão
    try:
        yield db  # "Empresta" a sessão para quem pediu
    finally:
        db.close()  # Garante que a sessão será fechada
```

**Conceitos importantes explicados:**

**Engine vs Session - Qual a diferença?**

Imagine uma biblioteca:
- **Engine** = a biblioteca inteira (o prédio, as estantes, os livros)
- **Session** = você pegando livros emprestados temporariamente

Você não carrega a biblioteca inteira para casa - você abre uma "sessão" de empréstimo, pega os livros, usa, e devolve.

**Por que `yield` em vez de `return`?**

`yield` é usado em geradores Python. Aqui, ele cria um padrão chamado "context manager":

```python
# Sem yield (ruim):
def get_db():
    db = SessionLocal()
    return db
    # ❌ Problema: quem vai fechar a sessão?

# Com yield (bom):
def get_db():
    db = SessionLocal()
    try:
        yield db  # Pausa aqui, executa a rota, volta aqui depois
    finally:
        db.close()  # ✅ Sempre fecha, mesmo com erro
```

**Por que `autocommit=False`?**

Transações no banco de dados seguem o princípio ACID. Com `autocommit=False`, você controla quando salvar mudanças:

```python
# Imagine transferir dinheiro entre contas
db.query(Account).filter(id=1).update({"balance": balance - 100})  # Debita
db.query(Account).filter(id=2).update({"balance": balance + 100})  # Credita
db.commit()  # Só agora ambas as operações são salvas juntas

# Se der erro entre as duas operações, nenhuma é salva (ACID)
```

---

## Parte 3: Definindo os Models

### 3.1 O que são Models?

Models são classes Python que representam tabelas no banco de dados.

```
Python Class              SQL Table
─────────────────────    ─────────────────────
class User:              CREATE TABLE users (
    id = Integer             id INTEGER PRIMARY KEY,
    username = String        username VARCHAR,
    email = String           email VARCHAR
                         )
```

Cada instância da classe = uma linha na tabela:

```python
# Criar um objeto Python
user = User(username="joao", email="joao@email.com")

# SQLAlchemy traduz para SQL:
# INSERT INTO users (username, email) VALUES ('joao', 'joao@email.com');
```

### 3.2 Criar `backend/models/user.py`

```python
"""
Model de usuário para autenticação e controle de acesso.

Um "model" é uma classe Python que representa uma tabela no banco de dados.
O SQLAlchemy automaticamente traduz esta classe para SQL.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.database.connection import Base

class User(Base):
    """
    Representa um usuário no sistema.

    Cada atributo de classe (id, username, email) vira uma coluna na tabela.
    Cada instância de User vira uma linha na tabela.

    Exemplo:
        user = User(username="joao", email="joao@email.com")
        # Isso cria uma linha na tabela 'users'
    """

    # __tablename__: nome da tabela no banco de dados
    # Sem isso, SQLAlchemy usaria "user" (singular) automaticamente
    __tablename__ = "users"

    # ===== COLUNAS DA TABELA =====

    # ID: Chave primária (identificador único)
    # Integer: tipo do dado (número inteiro)
    # primary_key=True: esta coluna identifica unicamente cada linha
    # index=True: cria um índice para buscas rápidas
    id = Column(Integer, primary_key=True, index=True)

    # USERNAME: Nome de usuário
    # String: tipo texto
    # unique=True: não pode haver dois usuários com mesmo username
    # index=True: acelera buscas por username (usado no login)
    # nullable=False: campo obrigatório (não pode ser NULL)
    username = Column(String, unique=True, index=True, nullable=False)

    # EMAIL: Endereço de email
    # Mesmas propriedades do username
    email = Column(String, unique=True, index=True, nullable=False)

    # HASHED_PASSWORD: Senha criptografada
    # NUNCA armazenamos senhas em texto plano!
    # Armazenamos apenas o "hash" (resultado de uma função criptográfica)
    hashed_password = Column(String, nullable=False)

    # CREATED_AT: Timestamp de criação
    # DateTime(timezone=True): data/hora com timezone
    # server_default=func.now(): valor gerado automaticamente pelo banco
    # (o banco insere a data/hora atual quando o registro é criado)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Conceitos importantes explicados:**

**Por que `primary_key=True`?**

Toda tabela precisa de uma forma de identificar unicamente cada linha. O `id` é essa identificação.

```python
# Dois usuários podem ter o mesmo nome:
user1 = User(id=1, username="João Silva")
user2 = User(id=2, username="João Silva")  # OK! IDs diferentes

# Mas não podem ter o mesmo ID:
user3 = User(id=1, username="Maria")  # ❌ Erro! ID 1 já existe
```

**Por que `index=True`?**

Índices são como o índice de um livro - aceleram a busca.

Sem índice:
```
Procurar "joao" em 1 milhão de usuários:
❌ Banco verifica linha por linha = lento (O(n))
```

Com índice:
```
Procurar "joao" com índice:
✅ Banco usa busca binária = rápido (O(log n))
```

Criamos índices em colunas usadas frequentemente em buscas:
- `username`: usado no login
- `email`: usado para verificar duplicidade

**Por que `unique=True`?**

Garante que não haverá duplicidade:

```python
# Primeiro usuário
user1 = User(username="joao", email="joao@email.com")
db.add(user1)
db.commit()  # ✅ OK

# Tentar criar outro com mesmo username
user2 = User(username="joao", email="outro@email.com")
db.add(user2)
db.commit()  # ❌ Erro! Username já existe
```

**Por que armazenar `hashed_password` em vez de `password`?**

Se alguém hackear seu banco de dados e você armazenar senhas em texto plano, todas as contas são comprometidas.

```
Senha em texto plano (RUIM):
password = "senha123"
# Hacker rouba o banco → vê todas as senhas

Senha com hash (BOM):
hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/..."
# Hacker rouba o banco → não consegue descobrir as senhas originais
```

Hash é uma função de "mão única" - você pode transformar senha em hash, mas não pode voltar de hash para senha.

**Por que `server_default=func.now()`?**

Queremos que o banco de dados insira automaticamente a data/hora de criação:

```python
# Sem server_default:
user = User(username="joao", created_at=datetime.now())  # ❌ Chato!

# Com server_default:
user = User(username="joao")  # ✅ created_at é preenchido automaticamente!
```

### 3.3 Criar `backend/models/task.py`

```python
"""
Model de tarefa para o sistema de gerenciamento.

Uma tarefa pertence a um usuário (relacionamento User → Task).
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database.connection import Base

class Task(Base):
    """
    Representa uma tarefa no sistema.

    Cada tarefa pertence a um usuário específico (user_id).
    """
    __tablename__ = "tasks"

    # ===== IDENTIFICAÇÃO =====
    id = Column(Integer, primary_key=True, index=True)

    # ===== DADOS DA TAREFA =====

    # TITLE: Título da tarefa
    # nullable=False: campo obrigatório
    title = Column(String, nullable=False)

    # DESCRIPTION: Descrição detalhada
    # nullable=True: campo opcional (padrão, não precisa especificar)
    description = Column(String, nullable=True)

    # COMPLETED: Status de conclusão
    # Boolean: True ou False
    # default=False: valor padrão se não especificado
    completed = Column(Boolean, default=False)

    # PRIORITY: Nível de prioridade
    # Pode ser: "low", "medium", "high"
    # default="medium": prioridade padrão
    priority = Column(String, default="medium")

    # ===== RELACIONAMENTO =====

    # USER_ID: Referência ao usuário dono da tarefa
    # ForeignKey("users.id"): esta coluna referencia a coluna 'id' da tabela 'users'
    # Isso cria um relacionamento: cada tarefa pertence a um usuário
    # nullable=False: toda tarefa DEVE ter um dono
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ===== TIMESTAMPS =====

    # CREATED_AT: Quando a tarefa foi criada
    # server_default=func.now(): valor automático na criação
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # UPDATED_AT: Quando a tarefa foi modificada pela última vez
    # onupdate=func.now(): atualizado automaticamente em toda modificação
    # Diferença: server_default = ao criar, onupdate = ao atualizar
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Conceitos importantes explicados:**

**O que é `ForeignKey`?**

Foreign Key (chave estrangeira) cria um relacionamento entre tabelas:

```
Tabela users:              Tabela tasks:
┌────┬──────────┐         ┌────┬───────────┬─────────┐
│ id │ username │         │ id │   title   │ user_id │ ← referencia users.id
├────┼──────────┤         ├────┼───────────┼─────────┤
│ 1  │ joao     │    ┌───→│ 1  │ Estudar   │    1    │
│ 2  │ maria    │    │    │ 2  │ Trabalhar │    1    │
└────┴──────────┘    │    │ 3  │ Exercitar │    2    │
                     │    └────┴───────────┴─────────┘
                     └────────┘
                     Relacionamento
```

Isso garante integridade referencial:

```python
# ✅ OK: criar tarefa para usuário existente
task = Task(title="Estudar", user_id=1)  # user_id 1 existe

# ❌ ERRO: criar tarefa para usuário inexistente
task = Task(title="Estudar", user_id=999)  # user_id 999 não existe
# Banco de dados rejeitará isso!
```

**Por que ter `user_id`?**

Cada tarefa precisa "pertencer" a alguém. Isso permite:

1. **Isolamento**: João só vê as tarefas dele, Maria só vê as dela
2. **Segurança**: João não pode editar tarefas de Maria
3. **Organização**: podemos buscar "todas as tarefas do usuário X"

```python
# Buscar apenas tarefas do João (user_id=1)
tasks = db.query(Task).filter(Task.user_id == 1).all()
```

**Diferença entre `default` e `server_default`?**

- **`default`**: valor padrão aplicado pelo Python (antes de enviar ao banco)
- **`server_default`**: valor padrão aplicado pelo banco de dados

```python
# default (Python):
completed = Column(Boolean, default=False)
# Quando você faz: task = Task(title="X")
# Python já coloca: task.completed = False

# server_default (Banco):
created_at = Column(DateTime, server_default=func.now())
# O banco de dados gera o valor automaticamente
```

**Por que `onupdate=func.now()`?**

Queremos rastrear quando a tarefa foi modificada pela última vez:

```python
# Criar tarefa
task = Task(title="Estudar")
db.add(task)
db.commit()
# created_at = 2024-01-01 10:00
# updated_at = None

# Atualizar tarefa
task.completed = True
db.commit()
# created_at = 2024-01-01 10:00 (não muda)
# updated_at = 2024-01-01 15:30 (atualizado automaticamente!)
```

---

## Parte 4: Schemas (Validação de Dados)

### 4.1 O que são Schemas e por que precisamos deles?

**Problema**: FastAPI recebe dados de fora (do cliente) e precisa validá-los.

Imagine que o cliente envia:
```json
{
  "username": "joao",
  "email": "isso-nao-e-um-email",
  "password": ""
}
```

Sem validação, isso causaria problemas:
- Email inválido seria salvo no banco
- Senha vazia seria aceita
- Faltam campos obrigatórios? Aplicação quebra!

**Solução**: Schemas Pydantic

Schemas são "moldes" que descrevem como os dados devem ser:

```python
class UserCreate(BaseModel):
    username: str  # Deve ser string
    email: EmailStr  # Deve ser email válido
    password: str  # Deve ser string
```

Quando o FastAPI recebe dados, ele:
1. ✅ Valida automaticamente usando o schema
2. ❌ Rejeita dados inválidos antes de chegar no seu código
3. 📄 Gera documentação automática mostrando o formato esperado

**Models vs Schemas - Qual a diferença?**

```
Models (SQLAlchemy):              Schemas (Pydantic):
─────────────────────            ──────────────────────
→ Representam o banco            → Representam dados na API
→ Como dados são ARMAZENADOS     → Como dados são TRANSMITIDOS
→ Incluem colunas, índices       → Incluem validações, tipos
→ Usados dentro do servidor      → Usados na comunicação HTTP

Exemplo:
Model User tem 'hashed_password' → Schema UserResponse NÃO tem senha
```

### 4.2 Criar `backend/schemas/user.py`

```python
"""
Schemas Pydantic para validação de dados de usuário.

Schemas definem a "forma" dos dados que entram e saem da API.
Pydantic valida automaticamente os dados e converte tipos.
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ===== SCHEMA BASE =====
class UserBase(BaseModel):
    """
    Schema base com campos comuns de usuário.

    Este schema é herdado por outros para evitar duplicação.
    Contém campos que aparecem tanto na criação quanto na resposta.
    """
    username: str  # Type hint: deve ser string
    email: EmailStr  # Type especial que valida formato de email

# ===== SCHEMA DE ENTRADA =====
class UserCreate(UserBase):
    """
    Schema para criação de usuário (entrada da API).

    Este schema é usado quando o cliente quer CRIAR um usuário.
    Inclui a senha em texto plano (será hasheada depois).

    Exemplo de uso:
        POST /api/auth/register
        Body: {"username": "joao", "email": "joao@email.com", "password": "123"}
    """
    password: str  # Senha em texto plano (só na entrada!)

# ===== SCHEMA DE SAÍDA =====
class UserResponse(UserBase):
    """
    Schema para resposta de usuário (saída da API).

    Este schema é usado quando o servidor RETORNA dados de um usuário.
    NÃO inclui a senha (segurança!).
    Inclui campos adicionais gerados pelo banco (id, created_at).

    Exemplo de uso:
        Response: {"id": 1, "username": "joao", "email": "...", "created_at": "..."}
    """
    id: int  # ID gerado pelo banco
    created_at: datetime  # Timestamp gerado pelo banco

    class Config:
        """
        Configuração do Pydantic.

        from_attributes=True: permite criar o schema a partir de um objeto
        SQLAlchemy (model) em vez de apenas dicionário.

        Sem isso:
            user_dict = {"id": 1, "username": "joao"}
            UserResponse(**user_dict)  # ✅ OK
            UserResponse(**user_model)  # ❌ Erro

        Com isso:
            user_model = db.query(User).first()
            UserResponse.from_orm(user_model)  # ✅ OK
        """
        from_attributes = True

# ===== SCHEMAS DE AUTENTICAÇÃO =====
class Token(BaseModel):
    """
    Schema para resposta de autenticação JWT.

    Quando o usuário faz login com sucesso, retornamos um token.

    Exemplo:
        POST /api/auth/login
        Response: {"access_token": "eyJ...", "token_type": "bearer"}
    """
    access_token: str  # O token JWT
    token_type: str  # Tipo do token (sempre "bearer")

class TokenData(BaseModel):
    """
    Schema para dados extraídos do token JWT.

    Quando validamos um token, extraímos informações dele.
    Este schema representa esses dados internos.

    Não é usado diretamente na API - apenas internamente.
    """
    username: Optional[str] = None  # Username pode ser None se token inválido
```

**Conceitos importantes explicados:**

**Por que separar UserCreate e UserResponse?**

Segurança e clareza:

```python
# UserCreate (ENTRADA):
# Cliente envia: {"username": "joao", "password": "senha123"}
# ✅ Precisa da senha para criar a conta

# UserResponse (SAÍDA):
# Servidor retorna: {"id": 1, "username": "joao", "created_at": "..."}
# ❌ NÃO retorna a senha (hashed_password)
# ✅ Inclui campos gerados pelo banco (id, created_at)
```

Se usássemos o mesmo schema para entrada e saída:
- Teríamos que aceitar `id` na criação (não faz sentido - o banco gera o ID)
- Teríamos que retornar `password` na resposta (PÉSSIMA ideia de segurança!)

**O que é `EmailStr`?**

`EmailStr` é um tipo especial do Pydantic que valida formato de email:

```python
# Sem EmailStr:
email: str = "isso-nao-e-email"  # ✅ Aceito (é uma string)

# Com EmailStr:
email: EmailStr = "isso-nao-e-email"  # ❌ Erro! Formato inválido
email: EmailStr = "joao@email.com"  # ✅ OK
```

FastAPI rejeita automaticamente emails inválidos antes de chegar ao seu código.

**O que é `Optional[str]`?**

`Optional[str]` significa "pode ser string ou None":

```python
# Sem Optional:
username: str = None  # ❌ Erro de tipo

# Com Optional:
username: Optional[str] = None  # ✅ OK
username: Optional[str] = "joao"  # ✅ OK também
```

**O que faz `from_attributes = True`?**

Permite converter um model SQLAlchemy diretamente em schema Pydantic:

```python
# Buscar usuário do banco (retorna model SQLAlchemy)
user_model = db.query(User).first()
# user_model é um objeto da classe User

# Converter para schema (para retornar na API)
user_response = UserResponse.from_orm(user_model)  # ✅ Funciona!
```

Sem `from_attributes = True`, você teria que converter manualmente:

```python
# Manualmente (chato):
user_response = UserResponse(
    id=user_model.id,
    username=user_model.username,
    email=user_model.email,
    created_at=user_model.created_at
)
```

### 4.3 Criar `backend/schemas/task.py`

```python
"""
Schemas Pydantic para validação de dados de tarefa.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ===== SCHEMA BASE =====
class TaskBase(BaseModel):
    """
    Schema base com campos comuns de tarefa.
    """
    title: str
    description: Optional[str] = None  # Opcional: pode ser None
    completed: bool = False  # Valor padrão: False
    priority: str = "medium"  # Valor padrão: "medium"

# ===== SCHEMA DE CRIAÇÃO =====
class TaskCreate(TaskBase):
    """
    Schema para criação de tarefa.

    Herda todos os campos de TaskBase.
    Não precisa adicionar nada - apenas cria um nome diferente para clareza.

    Uso:
        POST /api/tasks/
        Body: {"title": "Estudar", "priority": "high"}
    """
    pass  # Não adiciona nada, apenas herda

# ===== SCHEMA DE ATUALIZAÇÃO =====
class TaskUpdate(BaseModel):
    """
    Schema para atualização de tarefa.

    Todos os campos são opcionais para permitir atualização PARCIAL.
    Você pode atualizar apenas o título, ou apenas o status, etc.

    Uso:
        PUT /api/tasks/1
        Body: {"completed": true}  # Atualiza só o status
    """
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None

# ===== SCHEMA DE RESPOSTA =====
class TaskResponse(TaskBase):
    """
    Schema para resposta de tarefa.

    Inclui campos adicionais gerados pelo servidor/banco.
    """
    id: int  # Gerado pelo banco
    user_id: int  # Adicionado pelo servidor (usuário autenticado)
    created_at: datetime  # Gerado pelo banco
    updated_at: Optional[datetime] = None  # Gerado pelo banco (pode ser None)

    class Config:
        from_attributes = True  # Permite converter de model SQLAlchemy
```

**Conceitos importantes explicados:**

**Por que `TaskUpdate` tem tudo opcional?**

Permite atualização parcial (PATCH):

```python
# Atualizar apenas o status:
PUT /api/tasks/1
Body: {"completed": true}

# Atualizar apenas o título:
PUT /api/tasks/1
Body: {"title": "Novo título"}

# Se os campos não fossem opcionais, você teria que enviar TUDO:
Body: {
    "title": "...",
    "description": "...",
    "completed": true,
    "priority": "..."
}  # Muito trabalho!
```

**Por que `pass` no `TaskCreate`?**

`pass` significa "não fazer nada". Usamos aqui porque:
- `TaskCreate` não precisa adicionar campos novos
- Mas queremos um nome de classe separado para deixar o código mais claro
- `TaskCreate` vs `TaskUpdate` têm propósitos diferentes, mesmo tendo campos similares

---

## Parte 5: Serviços de Segurança

### 5.1 Por que precisamos de segurança?

Imagine que você armazena senhas assim:

```python
# NUNCA FAÇA ISSO!
user = User(username="joao", password="senha123")
```

Se alguém hackear seu banco de dados:
- ❌ Vê todas as senhas em texto plano
- ❌ Pode fazer login como qualquer usuário
- ❌ Pode testar essas senhas em outros sites (muita gente reutiliza senhas)

**Solução 1: Hash de senhas**

Hash é uma função matemática de "mão única":
- Transforma "senha123" em algo como "$2b$12$LQv3c1yqBWVHxkd0LHAkCO..."
- É impossível voltar do hash para a senha original
- Mesmo senha = mesmo hash (para validar login)

```
senha123  →  [HASH]  →  $2b$12$LQv3c1...  ✅
$2b$12$LQv3c1...  →  [???]  →  ❌ Impossível voltar
```

**Solução 2: JWT para autenticação**

Problema: Como o servidor sabe quem você é em cada requisição?

Opção ruim (senhas em toda requisição):
```
POST /api/tasks/
Body: {"title": "...", "username": "joao", "password": "senha123"}
❌ Inseguro! Senha trafegando constantemente
```

Opção boa (JWT):
```
1. Login uma vez:
   POST /api/auth/login
   Body: {"username": "joao", "password": "senha123"}
   Response: {"access_token": "eyJ..."}

2. Usar token nas próximas requisições:
   POST /api/tasks/
   Header: Authorization: Bearer eyJ...
   ✅ Token prova quem você é, sem enviar senha novamente
```

### 5.2 O que é JWT?

JWT (JSON Web Token) é um token autocontido que carrega informações:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2FvIiwiZXhwIjoxNjQwOTk1MjAwfQ.signature
│                                    ││                                    ││
│                                    ││                                    │└─ Assinatura (valida se token é legítimo)
│                                    │└─ Payload (dados: username, expiração)
│                                    └─ Header (tipo, algoritmo)
```

Vantagens:
- ✅ Servidor não precisa consultar banco em toda requisição
- ✅ Token tem expiração automática
- ✅ Assinatura garante que ninguém modificou o token

### 5.3 Criar `backend/services/security.py`

```python
"""
Serviços de segurança: hash de senhas e autenticação JWT.

Este arquivo concentra toda a lógica de segurança:
- Hash e verificação de senhas (bcrypt)
- Criação e validação de tokens JWT
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# ===== CONFIGURAÇÃO DO BCRYPT =====
# CryptContext gerencia algoritmos de hash de senha
# schemes=["bcrypt"]: usamos o algoritmo bcrypt (lento por design)
# deprecated="auto": se houver versões antigas de hash, atualiza automaticamente
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===== CONFIGURAÇÕES DO JWT =====
# ⚠️ IMPORTANTE: Em produção, use uma chave secreta forte e armazene em variável de ambiente!
SECRET_KEY = "your-secret-key-here-change-in-production"

# ALGORITHM: algoritmo usado para assinar o token (HS256 é padrão)
ALGORITHM = "HS256"

# ACCESS_TOKEN_EXPIRE_MINUTES: tempo de vida do token (30 minutos)
# Depois disso, o usuário precisa fazer login novamente
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ===== FUNÇÕES DE HASH DE SENHA =====

def hash_password(password: str) -> str:
    """
    Gera hash bcrypt de uma senha.

    Como funciona bcrypt:
    1. Adiciona "salt" aleatório à senha (previne rainbow tables)
    2. Aplica hash múltiplas vezes (lento por design = dificulta força bruta)
    3. Retorna hash que inclui salt + configurações

    Args:
        password: senha em texto plano (ex: "senha123")

    Returns:
        Hash da senha (ex: "$2b$12$LQv3c1yqBWVHxkd0LHAkCO...")

    Exemplo:
        hash_password("senha123")
        → "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lw..."

        hash_password("senha123")  # Mesmo input
        → "$2b$12$ABC123xyz..."  # Hash diferente! (salt aleatório)
    """
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash armazenado.

    Como funciona:
    1. Extrai o salt do hash armazenado
    2. Aplica o mesmo processo de hash na senha fornecida
    3. Compara os hashes usando comparação de tempo constante
       (previne timing attacks)

    Args:
        plain_password: senha fornecida pelo usuário (texto plano)
        hashed_password: hash armazenado no banco de dados

    Returns:
        True se a senha está correta, False caso contrário

    Exemplo:
        hash_armazenado = "$2b$12$LQv3c1..."
        verify_password("senha123", hash_armazenado)  → True
        verify_password("senha_errada", hash_armazenado)  → False
    """
    return password_context.verify(plain_password, hashed_password)

# ===== FUNÇÕES DE JWT =====

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT com os dados fornecidos.

    JWT é composto de 3 partes: header.payload.signature
    - Header: tipo do token e algoritmo
    - Payload: dados que queremos transmitir (username, expiração)
    - Signature: garante que o token não foi modificado

    Args:
        data: dicionário com dados a codificar no token
              Geralmente: {"sub": username}
              "sub" = subject (sujeito do token)
        expires_delta: tempo até expiração (opcional)

    Returns:
        Token JWT assinado (string)

    Exemplo:
        token = create_access_token({"sub": "joao"})
        → "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWI..."

    Como o token funciona:
        1. Servidor cria token com SECRET_KEY
        2. Cliente guarda token (localStorage, cookie)
        3. Cliente envia token em requisições futuras
        4. Servidor valida assinatura com SECRET_KEY
        5. Se válido, confia nos dados do token
    """
    # Copiar dados para não modificar o original
    to_encode = data.copy()

    # Calcular tempo de expiração
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Adicionar expiração ao payload
    # "exp" é um campo padrão JWT que bibliotecas entendem automaticamente
    to_encode.update({"exp": expire})

    # Codificar e assinar o token
    # jwt.encode retorna uma string no formato: header.payload.signature
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """
    Verifica e decodifica um token JWT.

    Esta função:
    1. Verifica a assinatura (garante que token não foi modificado)
    2. Verifica expiração (rejeita tokens expirados)
    3. Extrai o username do payload

    Args:
        token: token JWT recebido do cliente

    Returns:
        Username extraído do token, ou None se token inválido/expirado

    Exemplo:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        verify_token(token)  → "joao"

        token_invalido = "token-modificado-por-hacker"
        verify_token(token_invalido)  → None

        token_expirado = "eyJ..."  # (30 minutos já passaram)
        verify_token(token_expirado)  → None
    """
    try:
        # Decodificar e validar o token
        # jwt.decode automaticamente:
        # - Verifica assinatura usando SECRET_KEY
        # - Verifica expiração usando campo "exp"
        # - Lança exceção se algo estiver errado
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extrair username do payload
        # "sub" = subject (convenção padrão para identificar o usuário)
        username: str = payload.get("sub")

        return username

    except JWTError:
        # Token inválido, modificado, ou expirado
        return None
```

**Conceitos importantes explicados:**

**Por que bcrypt é "lento por design"?**

Isso é PROPOSITAL para segurança:

```
Atacante tenta adivinhar senha por força bruta:

Algoritmo rápido (MD5):
- 1 milhão de tentativas/segundo
- Descobre senha em minutos

Algoritmo lento (bcrypt):
- 100 tentativas/segundo
- Descobre senha em ANOS
```

Bcrypt ajusta a "lentidão" com um parâmetro chamado "rounds". Quanto maior, mais lento e seguro.

**O que é "salt" e por que é importante?**

Salt é um valor aleatório adicionado à senha antes do hash:

```
Sem salt (RUIM):
hash("senha123")  →  $abc123...
hash("senha123")  →  $abc123...  (mesmo hash!)
❌ Hacker cria "rainbow table" (tabela pré-calculada de hashes)

Com salt (BOM):
hash("senha123" + "salt_aleatorio_1")  →  $xyz789...
hash("senha123" + "salt_aleatorio_2")  →  $def456...  (hash diferente!)
✅ Mesmo senha = hashes diferentes = rainbow tables inúteis
```

**Por que usar "comparação de tempo constante"?**

Previne timing attacks:

```
Comparação normal (RUIM):
if hash1 == hash2:  # Para no primeiro caractere diferente
    # Hacker mede tempo de resposta e deduz quantos caracteres acertou

Comparação de tempo constante (BOM):
# Sempre compara TODOS os caracteres, mesmo se já sabe que é diferente
# Tempo de resposta não vaza informação
```

**O que é SECRET_KEY e por que é importante?**

SECRET_KEY é usada para assinar o token JWT:

```
Criar token:
header.payload → hash com SECRET_KEY → signature

Validar token:
header.payload → hash com SECRET_KEY → comparar com signature
✅ Se bate: token legítimo
❌ Se não bate: token foi modificado
```

Se um hacker descobrir sua SECRET_KEY:
- ❌ Pode criar tokens falsos para qualquer usuário
- ❌ Pode se passar por qualquer pessoa

**Em produção, SEMPRE:**
```python
import os
SECRET_KEY = os.getenv("SECRET_KEY")  # Variável de ambiente
# NUNCA commitar a chave no código!
```

**O que significa "sub" no payload do JWT?**

"sub" = subject (sujeito). É uma convenção padrão JWT que significa "sobre quem é este token".

```python
# Criar token
create_access_token({"sub": "joao"})
# Token carrega informação: "este token é sobre o usuário 'joao'"

# Validar token
username = verify_token(token)
# Extrai: "joao"
```

Outros campos padrão JWT:
- `exp`: expiration (expiração)
- `iat`: issued at (emitido em)
- `iss`: issuer (emissor)

---

## Parte 6: Rotas de Autenticação

### 6.1 O que são rotas?

Rotas são os "pontos de entrada" da sua API - URLs que os clientes podem acessar:

```
GET  /api/tasks/      → Listar tarefas
POST /api/tasks/      → Criar tarefa
GET  /api/tasks/123   → Buscar tarefa específica
```

Cada rota é uma função Python decorada com `@router.get`, `@router.post`, etc.

### 6.2 Como funciona o fluxo de autenticação?

```
1. Registro (uma vez):
   Cliente → POST /api/auth/register {"username": "joao", "password": "123"}
   Servidor → Salva no banco com senha hasheada

2. Login (quando quiser usar a aplicação):
   Cliente → POST /api/auth/login {"username": "joao", "password": "123"}
   Servidor → Valida credenciais, retorna token JWT

3. Usar API autenticado:
   Cliente → POST /api/tasks/ + Header: Authorization: Bearer <token>
   Servidor → Valida token, executa ação
```

### 6.3 Criar `backend/routes/auth.py`

```python
"""
Rotas de autenticação: registro e login de usuários.

Este arquivo define os endpoints (URLs) para:
- Registrar novos usuários
- Fazer login (receber token JWT)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserResponse, Token
from backend.services.security import hash_password, verify_password, create_access_token

# ===== CRIAÇÃO DO ROUTER =====
# APIRouter agrupa rotas relacionadas
# prefix="/api/auth": todas as rotas começam com /api/auth
# tags=["auth"]: agrupa na documentação automática
router = APIRouter(prefix="/api/auth", tags=["auth"])

# ===== ROTA: REGISTRO DE USUÁRIO =====
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.

    Fluxo:
    1. Cliente envia: {"username": "joao", "email": "joao@email.com", "password": "123"}
    2. Validamos se username/email já existem
    3. Hasheamos a senha
    4. Salvamos no banco
    5. Retornamos dados do usuário (SEM a senha)

    Args:
        user: dados do usuário (UserCreate schema valida automaticamente)
        db: sessão do banco (injetada automaticamente pelo Depends)

    Returns:
        Dados do usuário criado (UserResponse)

    Raises:
        HTTPException 400: se username ou email já existem

    Decoradores explicados:
        @router.post("/register"):
            - Esta função atende requisições POST para /api/auth/register

        response_model=UserResponse:
            - FastAPI valida e serializa a resposta usando UserResponse
            - Garante que senha não será retornada (UserResponse não tem password)

        status_code=201:
            - Código HTTP para "Created" (recurso criado com sucesso)
            - 200 = OK, 201 = Created, 400 = Bad Request, 401 = Unauthorized, etc.
    """

    # ───── VALIDAÇÃO 1: Username único ─────
    # Buscar no banco se já existe um usuário com esse username
    existing_user = db.query(User).filter(User.username == user.username).first()

    if existing_user:
        # HTTPException: FastAPI converte isso em resposta HTTP com erro
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # Código 400
            detail="Username already registered"  # Mensagem de erro
        )

    # ───── VALIDAÇÃO 2: Email único ─────
    existing_email = db.query(User).filter(User.email == user.email).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ───── CRIAR USUÁRIO ─────
    # 1. Hashear a senha (NUNCA armazenar senha em texto plano!)
    hashed_pwd = hash_password(user.password)

    # 2. Criar objeto User (model SQLAlchemy)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd  # Senha hasheada, não a original!
    )

    # 3. Adicionar à sessão (ainda não salvou no banco)
    db.add(db_user)

    # 4. Commit: salva de fato no banco de dados
    db.commit()

    # 5. Refresh: atualiza o objeto com dados do banco (id, created_at)
    db.refresh(db_user)

    # ───── RETORNAR RESPOSTA ─────
    # FastAPI automaticamente:
    # 1. Converte db_user (model) para UserResponse (schema)
    # 2. Serializa para JSON
    # 3. Remove campos não presentes em UserResponse (como hashed_password)
    return db_user

# ===== ROTA: LOGIN =====
@router.post("/login", response_model=Token)
def login(username: str, password: str, db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token JWT.

    Fluxo:
    1. Cliente envia: username e password
    2. Buscamos usuário no banco
    3. Verificamos se a senha está correta
    4. Geramos token JWT
    5. Retornamos token

    Args:
        username: nome de usuário
        password: senha em texto plano
        db: sessão do banco (injetada automaticamente)

    Returns:
        Token JWT e tipo (bearer)

    Raises:
        HTTPException 401: se credenciais incorretas

    Segurança:
        - Mesma mensagem de erro para username e senha incorretos
          (previne enumerar usuários válidos)
        - Senha é verificada com bcrypt (comparação segura)
        - Token tem expiração (30 minutos)
    """

    # ───── BUSCAR USUÁRIO ─────
    user = db.query(User).filter(User.username == username).first()

    if not user:
        # ⚠️ SEGURANÇA: Mesma mensagem para username E senha incorretos
        # Se disséssemos "Username não existe", hacker saberia quais usernames são válidos
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # 401 = não autorizado
            detail="Incorrect username or password"
        )

    # ───── VERIFICAR SENHA ─────
    # verify_password usa bcrypt para comparação segura
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"  # Mesma mensagem!
        )

    # ───── CRIAR TOKEN JWT ─────
    # Token carrega o username no campo "sub" (subject)
    access_token = create_access_token(data={"sub": user.username})

    # ───── RETORNAR TOKEN ─────
    # FastAPI serializa automaticamente para JSON:
    # {"access_token": "eyJ...", "token_type": "bearer"}
    return {"access_token": access_token, "token_type": "bearer"}
```

**Conceitos importantes explicados:**

**O que é `Depends(get_db)`?**

`Depends` é um recurso do FastAPI chamado "Dependency Injection":

```python
def login(username: str, password: str, db: Session = Depends(get_db)):
    # FastAPI automaticamente:
    # 1. Chama get_db() para obter uma sessão
    # 2. Passa a sessão para o parâmetro 'db'
    # 3. Fecha a sessão quando a função termina (finally block do get_db)
```

Benefícios:
- ✅ Você não precisa lembrar de fechar a sessão
- ✅ Código mais limpo (sem try/finally)
- ✅ Fácil testar (pode mockar a dependência)

**O que é `response_model=UserResponse`?**

Isso diz ao FastAPI:
1. Validar a resposta contra o schema `UserResponse`
2. Remover campos não presentes no schema
3. Serializar para JSON

```python
# Função retorna um model User:
db_user = User(username="joao", email="...", hashed_password="...")
return db_user

# FastAPI automaticamente:
# 1. Pega só os campos de UserResponse (id, username, email, created_at)
# 2. Remove hashed_password (não está em UserResponse)
# 3. Converte para JSON
```

**Por que `db.commit()` e `db.refresh()`?**

```python
db.add(db_user)  # Marca para adicionar (ainda não salvou)
db.commit()  # Salva de fato no banco
db.refresh(db_user)  # Atualiza o objeto com dados do banco

# Após commit, o banco pode ter gerado:
# - id (auto-incremento)
# - created_at (server_default)
# refresh() busca esses valores atualizados
```

**Por que usar status codes (200, 201, 400, 401)?**

Status codes comunicam o resultado da requisição:

- `200 OK`: tudo certo
- `201 Created`: recurso criado com sucesso
- `400 Bad Request`: erro nos dados enviados
- `401 Unauthorized`: não autenticado
- `404 Not Found`: recurso não existe
- `500 Internal Server Error`: erro no servidor

Clientes (browsers, apps) entendem esses códigos e reagem apropriadamente.

**Por que usar a mesma mensagem de erro para username e senha?**

Segurança contra enumeração de usuários:

```
❌ RUIM:
POST /login {"username": "joao_inexistente", "password": "..."}
Response: "Username não existe"
→ Hacker descobre que "joao_inexistente" não é um usuário válido

✅ BOM:
POST /login {"username": "joao_inexistente", "password": "..."}
Response: "Incorrect username or password"
→ Hacker não sabe se errou username ou senha
```

---

## Parte 7: Rotas de Tarefas

### 7.1 Como funciona autenticação nas rotas?

Rotas protegidas requerem um token JWT válido:

```
Cliente faz requisição:
POST /api/tasks/
Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Body: {"title": "Estudar"}

Servidor:
1. Extrai token do header Authorization
2. Valida token (signature, expiração)
3. Extrai username do token
4. Busca usuário no banco
5. Executa a ação (criar tarefa)
```

### 7.2 Criar `backend/routes/tasks.py`

```python
"""
Rotas CRUD para gerenciamento de tarefas.

CRUD = Create, Read, Update, Delete

Todas as rotas aqui requerem autenticação (token JWT válido).
Usuários só podem acessar suas próprias tarefas.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
from backend.database.connection import get_db
from backend.models.task import Task
from backend.models.user import User
from backend.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from backend.services.security import verify_token

# ===== CRIAÇÃO DO ROUTER =====
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# ===== DEPENDENCY: AUTENTICAÇÃO =====
def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    """
    Dependency para extrair e validar o usuário autenticado do token JWT.

    Esta função é usada como dependência em todas as rotas de tarefas.
    Ela garante que apenas usuários autenticados possam acessar as rotas.

    Como funciona:
    1. Extrai token do header HTTP "Authorization"
    2. Valida o token JWT
    3. Extrai username do token
    4. Busca usuário no banco
    5. Retorna o objeto User

    Args:
        authorization: valor do header Authorization (injetado automaticamente)
                       Formato esperado: "Bearer <token>"
        db: sessão do banco (injetada automaticamente)

    Returns:
        Objeto User autenticado

    Raises:
        HTTPException 401: se token inválido, expirado, ou usuário não encontrado

    Uso:
        @router.get("/")
        def get_tasks(current_user: User = Depends(get_current_user)):
            # current_user é automaticamente o usuário autenticado
            tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    """

    # ───── VALIDAÇÃO 1: Header presente e no formato correto ─────
    # Header deve ser: "Authorization: Bearer eyJhbGciOiJIUzI..."
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # ───── EXTRAIR TOKEN ─────
    # Remove "Bearer " para ficar só com o token
    token = authorization.replace("Bearer ", "")

    # ───── VALIDAR TOKEN ─────
    # verify_token valida assinatura e expiração
    username = verify_token(token)

    if not username:
        # Token inválido, modificado, ou expirado
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # ───── BUSCAR USUÁRIO ─────
    user = db.query(User).filter(User.username == username).first()

    if not user:
        # Token válido, mas usuário não existe mais (deletado?)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # ───── RETORNAR USUÁRIO ─────
    return user

# ===== CREATE: Criar tarefa =====
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova tarefa para o usuário autenticado.

    Fluxo:
    1. FastAPI valida token (via Depends(get_current_user))
    2. Recebe dados da tarefa (validados via TaskCreate schema)
    3. Cria tarefa no banco associada ao current_user
    4. Retorna tarefa criada

    Args:
        task: dados da tarefa (TaskCreate)
        db: sessão do banco (injetada)
        current_user: usuário autenticado (injetado via Depends)

    Returns:
        Tarefa criada (TaskResponse)

    Exemplo:
        POST /api/tasks/
        Headers: Authorization: Bearer eyJ...
        Body: {"title": "Estudar FastAPI", "priority": "high"}

        Response 201:
        {
            "id": 1,
            "title": "Estudar FastAPI",
            "priority": "high",
            "completed": false,
            "user_id": 1,
            "created_at": "2024-01-01T10:00:00"
        }
    """

    # ───── CRIAR TAREFA ─────
    # task.dict(): converte schema Pydantic para dicionário
    # **task.dict(): desempacota dicionário como argumentos
    # user_id=current_user.id: associa tarefa ao usuário autenticado
    db_task = Task(**task.dict(), user_id=current_user.id)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

# ===== READ: Listar tarefas =====
@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todas as tarefas do usuário autenticado.

    Segurança:
        - Usuário só vê SUAS tarefas (filtro por user_id)
        - João não pode ver tarefas de Maria

    Returns:
        Lista de tarefas (pode ser vazia [])

    Exemplo:
        GET /api/tasks/
        Headers: Authorization: Bearer eyJ...

        Response 200:
        [
            {"id": 1, "title": "Estudar", ...},
            {"id": 2, "title": "Trabalhar", ...}
        ]
    """

    # ───── BUSCAR TAREFAS DO USUÁRIO ─────
    # Filtra apenas tarefas onde user_id == current_user.id
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()

    return tasks

# ===== READ: Buscar tarefa específica =====
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca uma tarefa específica do usuário autenticado.

    Args:
        task_id: ID da tarefa (extraído da URL)

    Returns:
        Tarefa encontrada

    Raises:
        HTTPException 404: se tarefa não existe ou não pertence ao usuário

    Exemplo:
        GET /api/tasks/123
        Headers: Authorization: Bearer eyJ...

        Response 200:
        {"id": 123, "title": "Estudar", ...}

    Segurança:
        - Verifica que tarefa pertence ao usuário autenticado
        - João não pode acessar tarefa ID 123 se ela for de Maria
    """

    # ───── BUSCAR TAREFA ─────
    # Filtra por ID E por user_id (segurança!)
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id  # Garante que é do usuário autenticado
    ).first()

    if not task:
        # Tarefa não existe OU não pertence ao usuário
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task

# ===== UPDATE: Atualizar tarefa =====
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza uma tarefa existente do usuário autenticado.

    Suporta atualização parcial - apenas campos fornecidos são atualizados.

    Args:
        task_id: ID da tarefa
        task_update: campos a atualizar (TaskUpdate - todos opcionais)

    Returns:
        Tarefa atualizada

    Raises:
        HTTPException 404: se tarefa não existe ou não pertence ao usuário

    Exemplo:
        PUT /api/tasks/123
        Headers: Authorization: Bearer eyJ...
        Body: {"completed": true}  # Atualiza só o status

        Response 200:
        {"id": 123, "completed": true, ...}  # Outros campos inalterados
    """

    # ───── BUSCAR TAREFA ─────
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # ───── ATUALIZAR CAMPOS ─────
    # exclude_unset=True: ignora campos não fornecidos
    # Exemplo: se só enviar {"completed": true}, title não é incluído
    update_data = task_update.dict(exclude_unset=True)

    # Para cada campo fornecido, atualizar no objeto
    for field, value in update_data.items():
        setattr(task, field, value)  # task.completed = True, etc.

    db.commit()
    db.refresh(task)  # Busca updated_at atualizado pelo banco

    return task

# ===== DELETE: Deletar tarefa =====
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta uma tarefa do usuário autenticado.

    Returns:
        Nada (status 204 No Content)

    Raises:
        HTTPException 404: se tarefa não existe ou não pertence ao usuário

    Exemplo:
        DELETE /api/tasks/123
        Headers: Authorization: Bearer eyJ...

        Response 204: (sem body)
    """

    # ───── BUSCAR TAREFA ─────
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # ───── DELETAR ─────
    db.delete(task)
    db.commit()

    # 204 No Content: operação bem-sucedida, sem corpo de resposta
    return None
```

**Conceitos importantes explicados:**

**Por que criar `get_current_user` como dependency?**

Evita repetição de código:

```python
# Sem dependency (RUIM - repete em toda rota):
@router.get("/")
def get_tasks(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    username = verify_token(token)
    user = db.query(User).filter...
    # ... (10 linhas de validação repetidas em toda rota)

# Com dependency (BOM - define uma vez, usa em todas):
@router.get("/")
def get_tasks(current_user: User = Depends(get_current_user)):
    # current_user já é o usuário validado!
```

**O que é `Header(...)`?**

`Header(...)` diz ao FastAPI para extrair um valor do header HTTP:

```python
def get_current_user(authorization: str = Header(...)):
    # FastAPI automaticamente:
    # 1. Busca header "Authorization" na requisição
    # 2. Passa o valor para o parâmetro 'authorization'
    # ... = obrigatório (sem valor padrão)
```

Cliente envia:
```
GET /api/tasks/
Authorization: Bearer eyJ...
```

FastAPI extrai automaticamente e passa para a função.

**Por que filtrar por `user_id` em todas as queries?**

Segurança - isolamento de dados entre usuários:

```python
# SEM filtro por user_id (INSEGURO!):
task = db.query(Task).filter(Task.id == 123).first()
# João pode acessar tarefa 123 mesmo se for de Maria!

# COM filtro por user_id (SEGURO):
task = db.query(Task).filter(
    Task.id == 123,
    Task.user_id == current_user.id  # Só tarefas do usuário autenticado
).first()
# João só acessa suas próprias tarefas
```

**O que faz `exclude_unset=True`?**

Permite atualização parcial:

```python
# Cliente envia apenas:
{"completed": true}

# Sem exclude_unset (RUIM):
task_update.dict()
→ {"title": None, "description": None, "completed": True, "priority": None}
# Apagaria todos os outros campos!

# Com exclude_unset=True (BOM):
task_update.dict(exclude_unset=True)
→ {"completed": True}
# Só inclui campos que foram definidos
```

**Por que status 204 no DELETE?**

`204 No Content` significa "operação bem-sucedida, nada para retornar":

```
DELETE /api/tasks/123
Response: 204 (sem body)

✅ Tarefa foi deletada
✅ Não há dados para retornar (tarefa não existe mais)
✅ Cliente sabe que foi sucesso pelo código 204
```

---

## Parte 8: Arquivo Principal da Aplicação

### 8.1 O que faz o `main.py`?

O `main.py` é o ponto de entrada da aplicação - onde tudo começa:

1. Cria as tabelas no banco de dados
2. Inicializa a aplicação FastAPI
3. Registra as rotas
4. Configura arquivos estáticos
5. Inicia o servidor

### 8.2 Criar `main.py`

```python
"""
Arquivo principal da aplicação FastAPI.

Este é o "coração" da aplicação - o ponto de entrada onde tudo é configurado.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from backend.database.connection import engine, Base
from backend.routes import auth, tasks

# ===== CRIAR TABELAS NO BANCO =====
# Base.metadata contém informações sobre todos os models (User, Task)
# create_all: cria as tabelas se elas não existirem
# bind=engine: usa nosso engine (conexão com SQLite)
Base.metadata.create_all(bind=engine)

# Por que isso funciona automaticamente?
# 1. User e Task herdam de Base
# 2. Base.metadata registra automaticamente todos os descendentes
# 3. create_all lê os metadados e cria as tabelas

# ===== INICIALIZAR APLICAÇÃO FASTAPI =====
app = FastAPI(
    title="Todoist Task Manager",  # Aparece na documentação
    description="API para gerenciamento de tarefas com autenticação JWT",
    version="1.0.0"
)

# O que é 'app'?
# app é a instância central do FastAPI - o "aplicativo web"
# Tudo que configuramos aqui afeta toda a aplicação

# ===== INCLUIR ROTAS =====
# Registra os routers criados em auth.py e tasks.py
# Isso conecta as rotas à aplicação principal
app.include_router(auth.router)
app.include_router(tasks.router)

# O que include_router faz?
# - Pega todas as rotas definidas em auth.router (@router.post, etc.)
# - Adiciona à aplicação com o prefix configurado (/api/auth, /api/tasks)
# - Resultado: /api/auth/register, /api/auth/login, /api/tasks/, etc.

# ===== SERVIR ARQUIVOS ESTÁTICOS =====
# StaticFiles serve arquivos CSS, JS, imagens
# Quando cliente acessa /static/css/styles.css, FastAPI retorna o arquivo
app.mount("/static", StaticFiles(directory="static"), name="static")

# Por que isso é necessário?
# HTML precisa carregar CSS e JS:
# <link rel="stylesheet" href="/static/css/styles.css">
# Sem isso, o navegador receberia 404 (Not Found)

# ===== ROTA RAIZ =====
@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve a página inicial HTML.

    Quando usuário acessa http://localhost:8000/, retorna o HTML.

    response_class=HTMLResponse: indica que resposta é HTML, não JSON
    """
    html_path = Path("templates/index.html")
    return html_path.read_text()

# ===== HEALTH CHECK =====
@app.get("/health")
async def health_check():
    """
    Endpoint de health check para monitoramento.

    Útil para:
    - Verificar se servidor está funcionando
    - Monitoramento automático (Kubernetes, Docker, etc.)
    - Load balancers checarem se instância está saudável

    Response:
        {"status": "healthy"}
    """
    return {"status": "healthy"}

# ===== EXECUTAR SERVIDOR =====
if __name__ == "__main__":
    # Este bloco só executa se você rodar: python main.py
    # (não executa se você importar main.py em outro arquivo)

    import uvicorn

    # uvicorn.run inicia o servidor ASGI
    # app: a aplicação FastAPI
    # host="0.0.0.0": aceita conexões de qualquer IP (não só localhost)
    # port=8000: porta onde o servidor escuta
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Conceitos importantes explicados:**

**O que é ASGI e por que usar Uvicorn?**

```
WSGI (antigo):                 ASGI (moderno):
─────────────                  ───────────────
→ Síncrono                     → Assíncrono
→ Uma requisição por vez       → Múltiplas requisições simultâneas
→ Usado por Flask, Django      → Usado por FastAPI, Starlette

Uvicorn é um servidor ASGI - ele executa aplicações FastAPI
```

Analogia: WSGI é como atender um cliente por vez no caixa; ASGI é como ter vários caixas atendendo simultaneamente.

**Por que `Base.metadata.create_all()`?**

```python
# Você define models:
class User(Base):
    ...

class Task(Base):
    ...

# Base.metadata registra automaticamente:
# "Ah, User é uma tabela com colunas id, username, email..."
# "Ah, Task é uma tabela com colunas id, title, user_id..."

# create_all() usa essas informações para:
# CREATE TABLE users (...);
# CREATE TABLE tasks (...);
```

Isso acontece automaticamente na inicialização - muito conveniente para desenvolvimento!

**Por que `if __name__ == "__main__"`?**

```python
# Se você executar: python main.py
# → __name__ == "__main__" (True)
# → Executa uvicorn.run()

# Se você importar: from main import app
# → __name__ == "main" (não é "__main__")
# → NÃO executa uvicorn.run()
```

Isso permite importar `app` sem iniciar o servidor (útil para testes).

**O que é `host="0.0.0.0"`?**

```
host="127.0.0.1" ou "localhost":
→ Aceita conexões apenas do próprio computador
→ Outros dispositivos na rede não conseguem acessar

host="0.0.0.0":
→ Aceita conexões de qualquer IP
→ Seu celular na mesma rede pode acessar
→ Necessário para produção (servidor recebe requisições da internet)
```

---

## Parte 9, 10 e 11: Frontend (HTML, CSS, JavaScript)

O frontend já está documentado de forma suficiente no tutorial original. Como você pediu foco no backend, manteremos essas seções como estão.

---

## Parte 12: Executando a Aplicação

### 12.1 Iniciar o servidor

```bash
# Opção 1: Executar main.py diretamente
uv run python main.py

# Opção 2: Usar Uvicorn diretamente (mais recursos)
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**O que significa cada parâmetro?**

```
uvicorn main:app
         │    └─ nome da variável FastAPI no arquivo
         └─ nome do arquivo Python (sem .py)

--reload
    → Reinicia servidor automaticamente ao modificar código
    → Útil para desenvolvimento (NÃO use em produção!)

--host 0.0.0.0
    → Aceita conexões de qualquer IP

--port 8000
    → Porta onde o servidor escuta
```

### 12.2 Acessar a aplicação

Abra seu navegador em: **http://localhost:8000**

### 12.3 Acessar documentação automática

FastAPI gera documentação interativa automaticamente:

- **Swagger UI**: http://localhost:8000/docs
  - Interface visual para testar API
  - Mostra todos os endpoints, parâmetros, schemas
  - Permite fazer requisições diretamente do navegador

- **ReDoc**: http://localhost:8000/redoc
  - Documentação alternativa (mais "limpa")
  - Mesmo conteúdo, apresentação diferente

---

## Parte 13: Adicionando ao Git e GitHub

### 13.1 Criar `.gitignore`

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv/
.python-version

# uv
uv.lock

# Database
*.db
*.sqlite
*.sqlite3

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
```

### 13.2 Inicializar repositório Git

```bash
git init
git add .
git commit -m "Initial commit: Todoist Task Manager

FastAPI-based task management application with user authentication.

Features:
- User registration and JWT authentication
- Task CRUD operations with priority levels
- SQLite database with SQLAlchemy ORM
- Modern HTML/CSS/JS frontend
- UV package manager integration
- Bcrypt password hashing (fixed to v4.x)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### 13.3 Criar repositório no GitHub

```bash
# Se você tiver o GitHub CLI instalado
gh repo create todoist34 --public --source=. --remote=origin --push

# OU manualmente:
# 1. Crie o repositório em https://github.com/new
# 2. Execute:
git remote add origin https://github.com/SEU_USERNAME/todoist34.git
git branch -M main
git push -u origin main
```

---

## 🎓 Conceitos Aprendidos

### Backend
- **FastAPI**: framework moderno para APIs REST
- **SQLAlchemy ORM**: mapeamento objeto-relacional
- **JWT**: autenticação stateless com tokens
- **Bcrypt**: hash seguro de senhas
- **Dependency Injection**: padrão do FastAPI para gerenciar dependências
- **Pydantic**: validação de dados com type hints
- **ASGI**: protocolo assíncrono para aplicações web
- **RESTful API**: padrão de design de APIs
- **HTTP Status Codes**: comunicação de resultados
- **Foreign Keys**: relacionamentos entre tabelas
- **Schemas vs Models**: separação de concerns

### Segurança
- ✅ Senhas hasheadas (nunca em texto plano)
- ✅ JWT com expiração
- ✅ Isolamento de dados por usuário
- ✅ Validação de entrada (Pydantic)
- ✅ Proteção contra enumeração de usuários
- ✅ Comparação de tempo constante
- ✅ Salt aleatório em hashes

### Arquitetura
- **Separação em camadas**: database, models, schemas, routes, services
- **Single Responsibility**: cada arquivo/função tem um propósito
- **DRY (Don't Repeat Yourself)**: dependencies evitam repetição
- **Dependency Injection**: inversão de controle

---

## 🚀 Próximos Passos (Exercícios)

1. **Adicionar filtros de tarefas**: por status (completas/pendentes) e prioridade
2. **Implementar edição de tarefas**: formulário para editar título/descrição
3. **Adicionar datas**: `due_date` para prazo de conclusão
4. **Melhorar autenticação**: adicionar refresh tokens
5. **Adicionar testes**: pytest para testar endpoints
6. **Deploy**: Heroku, Railway, ou Render
7. **Migrar para PostgreSQL**: para produção
8. **Adicionar CORS middleware**: para aceitar requisições de outros domínios
9. **Adicionar paginação**: listar tarefas com limite/offset
10. **Adicionar busca**: filtrar tarefas por texto

---

## 📚 Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/)
- [JWT.io](https://jwt.io/) - Debugger de tokens JWT
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [HTTP Status Codes](https://httpstatuses.com/)
- [REST API Best Practices](https://restfulapi.net/)

---

## ❓ Troubleshooting

### Erro: "Address already in use"
```bash
# Encontrar e matar processo na porta 8000
lsof -ti:8000 | xargs kill -9
```

### Erro: "bcrypt ValueError"
Certifique-se de que está usando bcrypt 4.x:
```bash
uv add "bcrypt>=4.0.0,<5.0.0"
uv sync
```

### Banco de dados corrompido
```bash
# Deletar e recriar
rm todoist.db
uv run python main.py
```

### Token JWT não funciona
- Verifique se está enviando header: `Authorization: Bearer <token>`
- Verifique se token não expirou (30 minutos)
- Verifique console do navegador para erros

---

**Parabéns!** 🎉 Você construiu uma aplicação full-stack completa com autenticação, CRUD e frontend responsivo, e entendeu profundamente como cada parte funciona!
