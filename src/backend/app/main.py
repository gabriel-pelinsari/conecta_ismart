from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, profiles, interests  
from app.db.session import engine
from app.db.base import Base
# IMPORTAR TODOS OS MODELOS AQUI
from app.models.user import User, UserStats
from app.models.profile import Profile
from app.models.social import Friendship, Interest, UserInterest
from app.models.gamification import Badge, UserBadge

# === Criação das tabelas no banco ===
Base.metadata.create_all(bind=engine)

# === Inicialização do app ===
app = FastAPI(title="ISMART Conecta API", version="1.0.0")

# === Inclusão de routers ===
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(interests.router)  

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