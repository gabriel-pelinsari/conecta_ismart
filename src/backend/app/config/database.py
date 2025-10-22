from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Pega a URL do banco do arquivo .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Cria a engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool
)

# Cria a session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para os modelos
Base = declarative_base()

# Função para pegar a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()