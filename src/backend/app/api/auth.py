from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.core.email_utils import send_verification_email
import random, string, csv, io
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form  # <-- adicionar

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Função auxiliar ---
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# Criar form customizado
class OAuth2EmailPasswordRequestForm:
    def __init__(
        self,
        email: str = Form(...),  # <-- "email" em vez de "username"
        password: str = Form(...)
    ):
        self.username = email  # compatibilidade interna
        self.password = password

# --- Upload CSV (admin) ---
@router.post("/upload-csv")
async def upload_emails_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recebe um arquivo CSV com uma coluna 'email' e cria usuários pendentes.
    Ignora e-mails já cadastrados. Envia o código de verificação por e-mail.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um CSV válido.")

    content = await file.read()
    text = content.decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(text))

    if "email" not in csv_reader.fieldnames:
        raise HTTPException(status_code=400, detail="O CSV deve conter uma coluna chamada 'email'.")

    created = []
    skipped = []

    for row in csv_reader:
        email = row["email"].strip().lower()
        if not email:
            continue

        # Verifica se já existe no banco
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            skipped.append(email)
            continue  # ignora duplicados já existentes

        # Cria novo usuário com código
        code = generate_verification_code()
        user = User(email=email, verification_code=code)
        db.add(user)
        created.append({"email": email, "code": code})

        # Envia o e-mail com o código
        try:
            send_verification_email(email, code)
        except Exception as e:
            print(f"⚠️ Falha ao enviar e-mail para {email}: {e}")

    db.commit()

    return {
        "created_count": len(created),
        "skipped_count": len(skipped),
        "created_users": created,
        "skipped_users": skipped
    }

# --- Cadastro com código ---
@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email não pré-cadastrado")
    if user.verification_code != user_in.verification_code:
        raise HTTPException(status_code=400, detail="Código de verificação inválido")
    user.hashed_password = hash_password(user_in.password)
    user.is_verified = True
    user.verification_code = None
    db.commit()
    db.refresh(user)
    return user

# Atualizar endpoint
@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2EmailPasswordRequestForm = Depends(),  # <-- usar o customizado
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou sem senha definida")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha incorreta")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Conta não verificada")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}