from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.user import UserStats
from app.schemas.user import UserCreate, UserOut, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.core.email_utils import send_verification_email
import random, string, csv, io, logging
from fastapi import Form

# === LOGGING ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Função auxiliar ---
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# Criar form customizado
class OAuth2EmailPasswordRequestForm:
    def __init__(
        self,
        email: str = Form(...),
        password: str = Form(...)
    ):
        self.username = email
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
    logger.info(f"📤 Upload CSV iniciado: {file.filename}")
    
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
            logger.warning(f"⏭️  Email já existe: {email}")
            skipped.append(email)
            continue

        # Cria novo usuário
        user = User(email=email, is_active=False)
        db.add(user)
        created.append({"email": email})
        logger.info(f"✅ Usuário criado (pendente): {email}")

    db.commit()
    logger.info(f"📦 CSV processado: {len(created)} criados, {len(skipped)} ignorados")

    return {
        "created_count": len(created),
        "skipped_count": len(skipped),
        "created_users": created,
        "skipped_users": skipped
    }

# --- Cadastro ---
@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registro de novo usuário.
    Cria automaticamente Profile e UserStats após o registro.
    """
    logger.info(f"🔐 Registro iniciado para: {user_in.email}")

    user = db.query(User).filter(User.email == user_in.email).first()
    logger.debug(f"   Usuário existe no banco? {user is not None}")

    # Se o email já existe, erro
    if user:
        logger.warning(f"❌ Email já cadastrado: {user_in.email}")
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Criar novo usuário
    logger.info(f"👤 Criando novo usuário: {user_in.email}")
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.flush()
    logger.info(f"   Usuário criado com user_id={user.id}")

    # Cria Profile automaticamente
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(
            user_id=user.id,
            full_name=user.email.split("@")[0],
            is_public=True
        )
        db.add(profile)
        logger.info(f"✅ Profile criado para user_id={user.id}")
    else:
        logger.debug(f"ℹ️  Profile já existe para user_id={user.id}")

    # Cria UserStats automaticamente
    stats = db.query(UserStats).filter(UserStats.user_id == user.id).first()
    if not stats:
        stats = UserStats(
            user_id=user.id,
            total_posts=0,
            total_comments=0,
            total_votes_received=0,
            total_friendships=0,
            badges_count=0
        )
        db.add(stats)
        logger.info(f"✅ UserStats criado para user_id={user.id}")
    else:
        logger.debug(f"ℹ️  UserStats já existe para user_id={user.id}")

    db.commit()
    db.refresh(user)

    logger.info(f"✅ Registro completo: {user_in.email}")
    logger.info(f"   ID: {user.id}, Is Admin: {user.is_admin}, Is Verified: {user.is_verified}")

    return user

# --- Login ---
@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2EmailPasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login com email e senha.
    Retorna um token JWT com 60 minutos de validade.
    """
    logger.info(f"🔑 Login tentativa: {form_data.username}")
    
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user:
        logger.warning(f"❌ Usuário não encontrado: {form_data.username}")
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou sem senha definida")
    
    if not user.hashed_password:
        logger.warning(f"❌ Usuário sem senha: {form_data.username}")
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou sem senha definida")
    
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"❌ Senha incorreta: {form_data.username}")
        raise HTTPException(status_code=400, detail="Senha incorreta")
    
    if not user.is_verified:
        logger.warning(f"❌ Conta não verificada: {form_data.username}")
        raise HTTPException(status_code=403, detail="Conta não verificada")
    
    logger.info(f"✅ Login bem-sucedido: {form_data.username} (is_admin={user.is_admin})")

    # Incluir user_id no token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id,
            "is_admin": user.is_admin
        },
        expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}