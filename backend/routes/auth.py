"""
Rotas de autenticação da API.
Gerencia registro e login de usuários.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.database import get_database_session
from backend.models import User
from backend.schemas import UserCreate, UserLogin, UserResponse, Token
from backend.services import hash_password, verify_password, create_access_token, get_current_user
import os

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, database: Session = Depends(get_database_session)):
    """
    Registra um novo usuário no sistema.

    Args:
        user: Dados do usuário a ser criado
        database: Sessão do banco de dados

    Returns:
        UserResponse: Dados do usuário criado

    Raises:
        HTTPException: Se o username ou email já existirem
    """
    existing_user_by_username = database.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    existing_user_by_email = database.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    database.add(new_user)
    database.commit()
    database.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login_user(user: UserLogin, database: Session = Depends(get_database_session)):
    """
    Autentica um usuário e retorna um token de acesso.

    Args:
        user: Credenciais de login (username e password)
        database: Sessão do banco de dados

    Returns:
        Token: Token JWT de acesso

    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    db_user = database.query(User).filter(User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Retorna as informações do usuário autenticado.

    Args:
        current_user: Usuário autenticado (extraído do token)

    Returns:
        UserResponse: Dados do usuário autenticado
    """
    return current_user
