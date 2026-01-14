"""
Modelo de dados para usuários do sistema.
Representa a tabela 'users' no banco de dados.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class User(Base):
    """
    Modelo que representa um usuário no sistema.

    Attributes:
        id: Identificador único do usuário
        username: Nome de usuário único
        email: Email único do usuário
        hashed_password: Senha criptografada do usuário
        created_at: Data e hora de criação do usuário
        tasks: Relacionamento com as tarefas do usuário
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
