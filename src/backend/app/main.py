from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, profiles  # 👈 inclui o módulo de perfis
from app.db.session import engine
from app.models import user, profile  # 👈 garante que ambos os modelos existam
from app.db.init_admin import create_default_admin

# === Criação das tabelas no banco ===
user.Base.metadata.create_all(bind=engine)

# === Inicialização do app ===
app = FastAPI(title="ISMART Conecta API", version="1.0.0")

# === Cria admin padrão ===
create_default_admin()

# === Inclusão de routers ===
app.include_router(auth.router)
app.include_router(profiles.router)

# === CORS ===
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Servir uploads locais ===
import os
os.makedirs("media/avatars", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

# === Rotas simples ===
@app.get("/")
def read_root():
    return {"message": "API ISMART Conecta - online 🚀"}
