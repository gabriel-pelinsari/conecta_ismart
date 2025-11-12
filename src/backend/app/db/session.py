# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Obtém a DATABASE_URL do settings (usa DATABASE_URL do .env se existir)
DATABASE_URL = settings.get_database_url()

# Cria a engine SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Sessão padrão (cada requisição cria uma sessão)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para todos os modelos ORM
Base = declarative_base()

# Dependency para FastAPI (injeção de DB em rotas)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
