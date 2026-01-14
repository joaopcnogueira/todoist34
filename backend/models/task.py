"""
Modelo de dados para tarefas do sistema.
Representa a tabela 'tasks' no banco de dados.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Task(Base):
    """
    Modelo que representa uma tarefa no sistema.

    Attributes:
        id: Identificador único da tarefa
        title: Título da tarefa
        description: Descrição detalhada da tarefa (opcional)
        is_completed: Indica se a tarefa foi concluída
        created_at: Data e hora de criação da tarefa
        updated_at: Data e hora da última atualização
        user_id: ID do usuário proprietário da tarefa
        owner: Relacionamento com o usuário proprietário
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="tasks")
