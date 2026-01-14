"""
Schemas Pydantic para validação e serialização de dados de usuários.
Define os modelos de entrada e saída da API relacionados a usuários.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Schema base com campos comuns de usuário.

    Attributes:
        username: Nome de usuário
        email: Email do usuário
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """
    Schema para criação de novo usuário.

    Attributes:
        password: Senha do usuário (mínimo 6 caracteres)
    """
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """
    Schema para login de usuário.

    Attributes:
        username: Nome de usuário
        password: Senha do usuário
    """
    username: str
    password: str


class UserResponse(UserBase):
    """
    Schema de resposta com dados do usuário.

    Attributes:
        id: ID do usuário
        created_at: Data de criação do usuário
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """
    Schema para token de autenticação.

    Attributes:
        access_token: Token JWT de acesso
        token_type: Tipo do token (bearer)
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema para dados contidos no token.

    Attributes:
        username: Nome de usuário extraído do token
    """
    username: Optional[str] = None
