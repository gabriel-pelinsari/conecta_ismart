# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Monta a URL do banco
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

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
