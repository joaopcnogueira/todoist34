# Tutorial: Construindo um Gerenciador de Tarefas com FastAPI

Este tutorial guia você passo a passo na criação de uma aplicação completa de gerenciamento de tarefas usando FastAPI, SQLAlchemy, autenticação JWT e um frontend moderno.

## 📋 Pré-requisitos

- Python 3.8+
- UV instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Conhecimento básico de Python e APIs REST

## 🎯 O que vamos construir

Uma aplicação web full-stack com:
- Backend FastAPI com autenticação JWT
- Banco de dados SQLite com SQLAlchemy ORM
- Sistema de usuários com senhas criptografadas (bcrypt)
- CRUD completo de tarefas
- Frontend responsivo com HTML/CSS/JS vanilla

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

### 1.2 Inicializar o projeto com UV

```bash
# Inicializar projeto UV
uv init --no-workspace

# Adicionar dependências
uv add fastapi uvicorn sqlalchemy passlib python-jose python-multipart bcrypt

# IMPORTANTE: Fixar a versão do bcrypt para evitar problemas
uv add "bcrypt>=4.0.0,<5.0.0"
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
Eles transformam diretórios em pacotes Python, permitindo importações entre módulos.

---

## Parte 2: Configuração do Banco de Dados

### 2.1 Criar `backend/database/connection.py`

```python
"""
Configuração da conexão com o banco de dados SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./todoist.db"

# create_engine: cria o motor de conexão com o banco
# check_same_thread=False: permite uso em múltiplas threads (necessário para FastAPI)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# sessionmaker: fábrica para criar sessões do banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: classe base para todos os models ORM
Base = declarative_base()

def get_db():
    """
    Dependency injection: fornece uma sessão do banco para cada request.
    O finally garante que a sessão seja fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Conceitos importantes:**
- **Engine**: gerencia a conexão com o banco
- **Session**: contexto de transação para operações no banco
- **Base**: classe mãe para definir models ORM
- **Dependency Injection**: padrão do FastAPI para fornecer recursos (como sessão do banco) automaticamente

---

## Parte 3: Definindo os Models

### 3.1 Criar `backend/models/user.py`

```python
"""
Model de usuário para autenticação e controle de acesso.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.database.connection import Base

class User(Base):
    """
    Representa um usuário no sistema.

    Campos:
    - id: identificador único (chave primária, auto-incremento)
    - username: nome de usuário (único, não nulo)
    - email: endereço de email (único, não nulo)
    - hashed_password: senha criptografada com bcrypt
    - created_at: timestamp de criação (gerado automaticamente)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Por que usar `index=True`?**
Índices aceleram buscas por username e email, melhorando a performance de login e verificações de duplicidade.

**Por que `server_default=func.now()`?**
O timestamp é gerado automaticamente pelo banco de dados no momento da inserção, garantindo precisão.

### 3.2 Criar `backend/models/task.py`

```python
"""
Model de tarefa para o sistema de gerenciamento.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database.connection import Base

class Task(Base):
    """
    Representa uma tarefa no sistema.

    Campos:
    - id: identificador único
    - title: título da tarefa
    - description: descrição detalhada (opcional)
    - completed: status de conclusão (padrão: False)
    - priority: nível de prioridade (low, medium, high)
    - user_id: referência ao usuário proprietário
    - created_at: timestamp de criação
    - updated_at: timestamp de última atualização (atualizado automaticamente)
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default="medium")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Relacionamento com User:**
`ForeignKey("users.id")` cria uma relação entre Task e User, garantindo que toda tarefa pertence a um usuário.

**Diferença entre `server_default` e `onupdate`:**
- `server_default`: valor inicial ao criar o registro
- `onupdate`: atualizado automaticamente em toda modificação

---

## Parte 4: Schemas (Validação de Dados)

### 4.1 Criar `backend/schemas/user.py`

```python
"""
Schemas Pydantic para validação de dados de usuário.
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """
    Schema base com campos comuns de usuário.
    """
    username: str
    email: EmailStr  # Valida formato de email automaticamente

class UserCreate(UserBase):
    """
    Schema para criação de usuário (inclui senha).
    """
    password: str

class UserResponse(UserBase):
    """
    Schema para resposta de usuário (sem senha).
    Usado em responses da API.
    """
    id: int
    created_at: datetime

    class Config:
        # Permite criar o schema a partir de um model SQLAlchemy
        from_attributes = True

class Token(BaseModel):
    """
    Schema para resposta de autenticação JWT.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Schema para dados extraídos do token JWT.
    """
    username: Optional[str] = None
```

**Por que separar schemas?**
- **UserCreate**: aceita senha em texto plano (entrada)
- **UserResponse**: nunca retorna a senha (saída)
- Isso garante segurança e separação de responsabilidades

### 4.2 Criar `backend/schemas/task.py`

```python
"""
Schemas Pydantic para validação de dados de tarefa.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    """
    Schema base com campos comuns de tarefa.
    """
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = "medium"

class TaskCreate(TaskBase):
    """
    Schema para criação de tarefa.
    """
    pass

class TaskUpdate(BaseModel):
    """
    Schema para atualização de tarefa.
    Todos os campos são opcionais para permitir atualização parcial.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None

class TaskResponse(TaskBase):
    """
    Schema para resposta de tarefa.
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

**Por que `TaskUpdate` tem tudo opcional?**
Permite atualização parcial (PATCH) - você pode atualizar apenas o título, ou apenas o status, sem enviar todos os campos.

---

## Parte 5: Serviços de Segurança

### 5.1 Criar `backend/services/security.py`

```python
"""
Serviços de segurança: hash de senhas e autenticação JWT.
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# Configuração do contexto de hash com bcrypt
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações JWT
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """
    Gera hash bcrypt de uma senha.

    O bcrypt é um algoritmo de hash lento por design, tornando ataques
    de força bruta impraticáveis.
    """
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash armazenado.

    Usa comparação de tempo constante para prevenir ataques de timing.
    """
    return password_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT com os dados fornecidos.

    Args:
        data: dados a serem codificados no token (geralmente username)
        expires_delta: tempo até expiração (padrão: 30 minutos)

    Returns:
        Token JWT assinado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """
    Verifica e decodifica um token JWT.

    Returns:
        Username extraído do token, ou None se inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError:
        return None
```

**Conceitos de segurança:**
- **Bcrypt**: algoritmo lento que dificulta força bruta
- **JWT**: token autocontido que não requer consulta ao banco
- **SECRET_KEY**: NUNCA committar a chave real! Use variáveis de ambiente em produção

---

## Parte 6: Rotas de Autenticação

### 6.1 Criar `backend/routes/auth.py`

```python
"""
Rotas de autenticação: registro e login de usuários.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserResponse, Token
from backend.services.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.

    Validações:
    - Username único
    - Email único
    - Senha é hasheada antes de salvar

    Returns:
        Dados do usuário criado (sem senha)
    """
    # Verificar se username já existe
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Verificar se email já existe
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Criar novo usuário com senha hasheada
    hashed_pwd = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Atualiza o objeto com dados do banco (id, created_at)

    return db_user

@router.post("/login", response_model=Token)
def login(username: str, password: str, db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token JWT.

    Fluxo:
    1. Busca usuário pelo username
    2. Verifica a senha
    3. Gera token JWT

    Returns:
        Token JWT e tipo (bearer)
    """
    # Buscar usuário
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Verificar senha
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Criar token JWT
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}
```

**Padrões de segurança implementados:**
- Mesma mensagem de erro para username e senha incorretos (previne enumeração)
- Senha nunca é retornada na resposta
- Token tem expiração configurável

---

## Parte 7: Rotas de Tarefas

### 7.1 Criar `backend/routes/tasks.py`

```python
"""
Rotas CRUD para gerenciamento de tarefas.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
from backend.database.connection import get_db
from backend.models.task import Task
from backend.models.user import User
from backend.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from backend.services.security import verify_token

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    """
    Dependency para extrair e validar o usuário autenticado do token JWT.

    Fluxo:
    1. Extrai token do header Authorization
    2. Valida o token
    3. Busca o usuário no banco

    Returns:
        Objeto User autenticado

    Raises:
        HTTPException 401 se token inválido ou usuário não encontrado
    """
    # Extrair token (formato: "Bearer <token>")
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    token = authorization.replace("Bearer ", "")
    username = verify_token(token)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova tarefa para o usuário autenticado.
    """
    db_task = Task(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todas as tarefas do usuário autenticado.
    """
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca uma tarefa específica do usuário autenticado.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task

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
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Atualizar apenas campos fornecidos
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta uma tarefa do usuário autenticado.
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()
    return None
```

**Segurança implementada:**
- Todas as rotas requerem autenticação (`Depends(get_current_user)`)
- Usuários só podem acessar suas próprias tarefas (filtro por `user_id`)
- Validação automática de dados via Pydantic schemas

---

## Parte 8: Arquivo Principal da Aplicação

### 8.1 Criar `main.py`

```python
"""
Arquivo principal da aplicação FastAPI.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from backend.database.connection import engine, Base
from backend.routes import auth, tasks

# Criar todas as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicializar aplicação FastAPI
app = FastAPI(
    title="Todoist Task Manager",
    description="API para gerenciamento de tarefas com autenticação JWT",
    version="1.0.0"
)

# Incluir rotas
app.include_router(auth.router)
app.include_router(tasks.router)

# Servir arquivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve a página inicial HTML.
    """
    html_path = Path("templates/index.html")
    return html_path.read_text()

@app.get("/health")
async def health_check():
    """
    Endpoint de health check para monitoramento.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**O que acontece aqui:**
1. `Base.metadata.create_all(bind=engine)` cria as tabelas automaticamente
2. Rotas são registradas via `include_router`
3. Frontend é servido via `StaticFiles` e rota raiz
4. Health check para monitoramento de disponibilidade

---

## Parte 9: Frontend HTML

### 9.1 Criar `templates/index.html`

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todoist - Gerenciador de Tarefas</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="container">
        <!-- Seção de Autenticação -->
        <div id="auth-section">
            <div class="auth-forms">
                <!-- Formulário de Login -->
                <div class="auth-form" id="login-form">
                    <h2>Login</h2>
                    <form onsubmit="handleLogin(event)">
                        <input type="text" id="login-username" placeholder="Username" required>
                        <input type="password" id="login-password" placeholder="Password" required>
                        <button type="submit">Entrar</button>
                    </form>
                    <p>Não tem conta? <a href="#" onclick="showRegister()">Registre-se</a></p>
                </div>

                <!-- Formulário de Registro -->
                <div class="auth-form hidden" id="register-form">
                    <h2>Registro</h2>
                    <form onsubmit="handleRegister(event)">
                        <input type="text" id="register-username" placeholder="Username" required>
                        <input type="email" id="register-email" placeholder="Email" required>
                        <input type="password" id="register-password" placeholder="Password" required>
                        <button type="submit">Registrar</button>
                    </form>
                    <p>Já tem conta? <a href="#" onclick="showLogin()">Faça login</a></p>
                </div>
            </div>
        </div>

        <!-- Seção de Tarefas -->
        <div id="tasks-section" class="hidden">
            <div class="header">
                <h1>Minhas Tarefas</h1>
                <button onclick="handleLogout()">Sair</button>
            </div>

            <!-- Formulário de Nova Tarefa -->
            <div class="task-form">
                <h2>Nova Tarefa</h2>
                <form onsubmit="handleCreateTask(event)">
                    <input type="text" id="task-title" placeholder="Título da tarefa" required>
                    <textarea id="task-description" placeholder="Descrição (opcional)"></textarea>
                    <select id="task-priority">
                        <option value="low">Baixa</option>
                        <option value="medium" selected>Média</option>
                        <option value="high">Alta</option>
                    </select>
                    <button type="submit">Adicionar Tarefa</button>
                </form>
            </div>

            <!-- Lista de Tarefas -->
            <div class="tasks-list">
                <h2>Lista de Tarefas</h2>
                <div id="tasks-container"></div>
            </div>
        </div>
    </div>

    <script src="/static/js/app.js"></script>
</body>
</html>
```

---

## Parte 10: CSS Responsivo

### 10.1 Criar `static/css/styles.css`

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.container {
    width: 90%;
    max-width: 800px;
    margin: 20px;
}

/* Estilos de Autenticação */
.auth-forms {
    background: white;
    border-radius: 10px;
    padding: 40px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.auth-form h2 {
    color: #333;
    margin-bottom: 20px;
}

.auth-form input {
    width: 100%;
    padding: 12px;
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 14px;
}

.auth-form button {
    width: 100%;
    padding: 12px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.3s;
}

.auth-form button:hover {
    background: #5568d3;
}

.auth-form p {
    text-align: center;
    margin-top: 15px;
    color: #666;
}

.auth-form a {
    color: #667eea;
    text-decoration: none;
}

/* Estilos de Tarefas */
#tasks-section {
    background: white;
    border-radius: 10px;
    padding: 30px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.header h1 {
    color: #333;
}

.header button {
    padding: 10px 20px;
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.task-form {
    margin-bottom: 30px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.task-form h2 {
    color: #333;
    margin-bottom: 15px;
    font-size: 20px;
}

.task-form input,
.task-form textarea,
.task-form select {
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.task-form textarea {
    resize: vertical;
    min-height: 80px;
}

.task-form button {
    width: 100%;
    padding: 12px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

/* Card de Tarefa */
.task-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    transition: transform 0.2s;
}

.task-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.task-card.completed {
    opacity: 0.6;
    background: #f8f9fa;
}

.task-card h3 {
    color: #333;
    margin-bottom: 8px;
}

.task-card.completed h3 {
    text-decoration: line-through;
}

.task-card p {
    color: #666;
    margin-bottom: 10px;
}

.task-priority {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    margin-bottom: 10px;
}

.priority-low { background: #28a745; color: white; }
.priority-medium { background: #ffc107; color: #333; }
.priority-high { background: #dc3545; color: white; }

.task-actions {
    display: flex;
    gap: 10px;
}

.task-actions button {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.btn-complete {
    background: #28a745;
    color: white;
}

.btn-delete {
    background: #dc3545;
    color: white;
}

/* Utilitários */
.hidden {
    display: none !important;
}
```

---

## Parte 11: JavaScript Frontend

### 11.1 Criar `static/js/app.js`

```javascript
// Variável global para armazenar o token JWT
let authToken = localStorage.getItem('authToken');

// Configuração base da API
const API_BASE_URL = 'http://localhost:8000';

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        showTasksSection();
        loadTasks();
    } else {
        showAuthSection();
    }
});

// ===== AUTENTICAÇÃO =====

function showLogin() {
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('register-form').classList.add('hidden');
}

function showRegister() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
}

async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });

        if (response.ok) {
            alert('Registro realizado com sucesso! Faça login.');
            showLogin();
        } else {
            const error = await response.json();
            alert(`Erro: ${error.detail}`);
        }
    } catch (error) {
        alert('Erro ao registrar. Tente novamente.');
        console.error(error);
    }
}

async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        // FastAPI espera os dados em formato de formulário (URL encoded)
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/api/auth/login?${formData}`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showTasksSection();
            loadTasks();
        } else {
            alert('Credenciais inválidas!');
        }
    } catch (error) {
        alert('Erro ao fazer login. Tente novamente.');
        console.error(error);
    }
}

function handleLogout() {
    authToken = null;
    localStorage.removeItem('authToken');
    showAuthSection();
}

// ===== NAVEGAÇÃO =====

function showAuthSection() {
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('tasks-section').classList.add('hidden');
}

function showTasksSection() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('tasks-section').classList.remove('hidden');
}

// ===== TAREFAS =====

async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const tasks = await response.json();
            renderTasks(tasks);
        } else if (response.status === 401) {
            handleLogout();
        }
    } catch (error) {
        console.error('Erro ao carregar tarefas:', error);
    }
}

function renderTasks(tasks) {
    const container = document.getElementById('tasks-container');

    if (tasks.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">Nenhuma tarefa ainda. Crie sua primeira!</p>';
        return;
    }

    container.innerHTML = tasks.map(task => `
        <div class="task-card ${task.completed ? 'completed' : ''}">
            <h3>${task.title}</h3>
            <p>${task.description || 'Sem descrição'}</p>
            <span class="task-priority priority-${task.priority}">
                ${task.priority.toUpperCase()}
            </span>
            <div class="task-actions">
                <button class="btn-complete" onclick="toggleTaskComplete(${task.id}, ${!task.completed})">
                    ${task.completed ? 'Reabrir' : 'Concluir'}
                </button>
                <button class="btn-delete" onclick="deleteTask(${task.id})">
                    Excluir
                </button>
            </div>
        </div>
    `).join('');
}

async function handleCreateTask(event) {
    event.preventDefault();

    const title = document.getElementById('task-title').value;
    const description = document.getElementById('task-description').value;
    const priority = document.getElementById('task-priority').value;

    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                title,
                description,
                priority,
                completed: false
            })
        });

        if (response.ok) {
            // Limpar formulário
            document.getElementById('task-title').value = '';
            document.getElementById('task-description').value = '';
            document.getElementById('task-priority').value = 'medium';

            // Recarregar lista
            loadTasks();
        }
    } catch (error) {
        console.error('Erro ao criar tarefa:', error);
    }
}

async function toggleTaskComplete(taskId, completed) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ completed })
        });

        if (response.ok) {
            loadTasks();
        }
    } catch (error) {
        console.error('Erro ao atualizar tarefa:', error);
    }
}

async function deleteTask(taskId) {
    if (!confirm('Tem certeza que deseja excluir esta tarefa?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok || response.status === 204) {
            loadTasks();
        }
    } catch (error) {
        console.error('Erro ao excluir tarefa:', error);
    }
}
```

---

## Parte 12: Executando a Aplicação

### 12.1 Iniciar o servidor

```bash
# Com UV
uv run python main.py

# Ou diretamente com Uvicorn
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 12.2 Acessar a aplicação

Abra seu navegador em: **http://localhost:8000**

### 12.3 Testar a API

Acesse a documentação interativa automática do FastAPI:
- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

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

### Frontend
- **SPA simples**: Single Page Application sem frameworks
- **LocalStorage**: armazenamento de token no navegador
- **Fetch API**: requisições HTTP assíncronas
- **CSS moderno**: gradientes, transitions, flexbox

### Segurança
- ✅ Senhas hasheadas (nunca em texto plano)
- ✅ JWT com expiração
- ✅ Isolamento de dados por usuário
- ✅ Validação de entrada (Pydantic)
- ✅ CORS (para produção, adicionar middleware)

### DevOps
- **UV**: gerenciador de pacotes moderno
- **SQLite**: banco de dados embutido (fácil para desenvolvimento)
- **Git**: controle de versão
- **GitHub**: hospedagem de código

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

---

## 📚 Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/)
- [JWT.io](https://jwt.io/) - Debugger de tokens JWT
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [UV Documentation](https://github.com/astral-sh/uv)

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

---

**Parabéns!** 🎉 Você construiu uma aplicação full-stack completa com autenticação, CRUD e frontend responsivo!
