# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Importa todos os modelos usados
from app.models import user, profile, social, gamification, poll
from app.models.thread import Thread, Comment, ThreadVote, CommentVote

# Define metadata
from app.db.base import Base
target_metadata = Base.metadata

# Alembic Config object
config = context.config

# Atualiza URL de conexão a partir do .env
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

# Interpreta o arquivo de logging (alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define metadata base
target_metadata = Base.metadata

# ----------- Funções padrão do Alembic -----------
def run_migrations_offline():
    """Executa migrations no modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Executa migrations com conexão real."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
