"""
Schemas Pydantic para validação e serialização de dados de tarefas.
Define os modelos de entrada e saída da API relacionados a tarefas.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    """
    Schema base com campos comuns de tarefa.

    Attributes:
        title: Título da tarefa
        description: Descrição da tarefa (opcional)
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class TaskCreate(TaskBase):
    """
    Schema para criação de nova tarefa.
    Herda todos os campos de TaskBase.
    """
    pass


class TaskUpdate(BaseModel):
    """
    Schema para atualização de tarefa.
    Todos os campos são opcionais para permitir atualização parcial.

    Attributes:
        title: Novo título da tarefa
        description: Nova descrição da tarefa
        is_completed: Novo status de conclusão
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_completed: Optional[bool] = None


class TaskResponse(TaskBase):
    """
    Schema de resposta com dados completos da tarefa.

    Attributes:
        id: ID da tarefa
        is_completed: Status de conclusão
        created_at: Data de criação
        updated_at: Data da última atualização
        user_id: ID do usuário proprietário
    """
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True
