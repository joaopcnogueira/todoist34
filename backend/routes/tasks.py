"""
Rotas de gerenciamento de tarefas da API.
Fornece operações CRUD para tarefas dos usuários.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_database_session
from backend.models import User, Task
from backend.schemas import TaskCreate, TaskUpdate, TaskResponse
from backend.services import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_database_session)
):
    """
    Cria uma nova tarefa para o usuário autenticado.

    Args:
        task: Dados da tarefa a ser criada
        current_user: Usuário autenticado
        database: Sessão do banco de dados

    Returns:
        TaskResponse: Dados da tarefa criada
    """
    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=current_user.id
    )

    database.add(new_task)
    database.commit()
    database.refresh(new_task)

    return new_task


@router.get("", response_model=List[TaskResponse])
def get_all_tasks(
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_database_session)
):
    """
    Retorna todas as tarefas do usuário autenticado.

    Args:
        current_user: Usuário autenticado
        database: Sessão do banco de dados

    Returns:
        List[TaskResponse]: Lista de todas as tarefas do usuário
    """
    tasks = database.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id(
    task_id: int,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_database_session)
):
    """
    Retorna uma tarefa específica pelo ID.

    Args:
        task_id: ID da tarefa a ser buscada
        current_user: Usuário autenticado
        database: Sessão do banco de dados

    Returns:
        TaskResponse: Dados da tarefa encontrada

    Raises:
        HTTPException: Se a tarefa não existir ou não pertencer ao usuário
    """
    task = database.query(Task).filter(
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
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_database_session)
):
    """
    Atualiza uma tarefa existente.
    Permite atualização parcial dos campos.

    Args:
        task_id: ID da tarefa a ser atualizada
        task_update: Dados a serem atualizados
        current_user: Usuário autenticado
        database: Sessão do banco de dados

    Returns:
        TaskResponse: Dados da tarefa atualizada

    Raises:
        HTTPException: Se a tarefa não existir ou não pertencer ao usuário
    """
    task = database.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    database.commit()
    database.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_database_session)
):
    """
    Deleta uma tarefa existente.

    Args:
        task_id: ID da tarefa a ser deletada
        current_user: Usuário autenticado
        database: Sessão do banco de dados

    Returns:
        None: Retorna status 204 No Content em caso de sucesso

    Raises:
        HTTPException: Se a tarefa não existir ou não pertencer ao usuário
    """
    task = database.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    database.delete(task)
    database.commit()

    return None
