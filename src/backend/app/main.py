from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.routes.email_routes import router as email_router

load_dotenv()

# Cria a app FastAPI
app = FastAPI(
    title="ISMART Conecta API",
    description="API para plataforma de conexão entre alunos",
    version="1.0.0"
)

# Configurar CORS
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(email_router)

# Rota de teste
@app.get("/")
def read_root():
    return {
        "message": "ISMART Conecta API",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}