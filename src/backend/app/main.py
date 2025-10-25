from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from app.models import user

# === CONFIGURAR LOGGING ===
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# === Imports ===
from app.db.session import engine
from app.api import auth, profiles, interests, threads

# === Inicialização do app ===
app = FastAPI(title="ISMART Conecta API", version="1.0.0")

# === Inclusão de routers ===
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(interests.router)  
app.include_router(threads.router)

user.Base.metadata.create_all(bind=engine)

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