"""
Arquivo principal da aplicação FastAPI.
Configura e inicializa o servidor web, rotas e banco de dados.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.database import Base, engine
from backend.routes import auth_router, tasks_router
from backend.models import User, Task

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todoist - Task Manager",
    description="API para gerenciamento de tarefas com autenticação de usuários",
    version="1.0.0"
)

# Configuração de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra as rotas da API
app.include_router(auth_router)
app.include_router(tasks_router)

# Serve arquivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_home():
    """
    Serve a página principal da aplicação.

    Returns:
        FileResponse: Arquivo HTML da página inicial
    """
    return FileResponse("templates/index.html")


@app.get("/health")
def health_check():
    """
    Endpoint para verificar o status da API.

    Returns:
        dict: Status da aplicação
    """
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
