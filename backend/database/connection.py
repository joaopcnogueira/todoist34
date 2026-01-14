"""
Módulo responsável pela configuração e conexão com o banco de dados SQLite.
Fornece a engine do SQLAlchemy e as sessões do banco.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todoist.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # necessário apenas para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_database_session():
    """
    Cria e fornece uma sessão do banco de dados.
    A sessão é automaticamente fechada após o uso.

    Yields:
        Session: Sessão do banco de dados SQLAlchemy
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
