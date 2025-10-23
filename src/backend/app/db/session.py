# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Cria o engine do SQLAlchemy com o Postgres
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # verifica conexões antes de usar
)

# Cria a fábrica de sessões (SessionLocal)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependência para o FastAPI (abre e fecha a sessão)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
