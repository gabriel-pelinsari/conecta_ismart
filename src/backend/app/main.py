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
from app.api import (
    auth, profiles, interests, threads, student_directory,
    friendships, university_groups, gamification, moderation,
    notifications, events, mentorship, polls
)

# === Inicialização do app ===
app = FastAPI(title="ISMART Conecta API", version="1.0.0")

# === Inclusão de routers ===
app.include_router(auth.router)
app.include_router(profiles.router)  # legacy /profiles/*
app.include_router(profiles.router, prefix="/api")  # main /api/profiles/*
app.include_router(interests.router)  # legacy /interests/*
app.include_router(interests.router, prefix="/api")  # main /api/interests/*
app.include_router(threads.router)
app.include_router(student_directory.router)
app.include_router(friendships.router)
app.include_router(university_groups.router)
app.include_router(gamification.router)
app.include_router(moderation.router)
app.include_router(notifications.router)
app.include_router(events.router)
app.include_router(mentorship.router)
app.include_router(polls.router)

# Não criar tabelas automaticamente - banco gerenciado externamente
# user.Base.metadata.create_all(bind=engine)

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
