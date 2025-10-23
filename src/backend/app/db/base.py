# app/db/base.py
from sqlalchemy.orm import declarative_base

# Classe base para todos os models
Base = declarative_base()

# IMPORTA TODOS OS MODELS AQUI PARA REGISTRAR NO METADATA
from app.models import user  # modelo User já existente
from app.models import profile  # modelo Profile que criamos agora

__all__ = ["Base"]
