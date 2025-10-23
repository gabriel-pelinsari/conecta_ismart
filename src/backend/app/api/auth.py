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

        # Cria novo usuário com código
        code = generate_verification_code()
        user = User(email=email, verification_code=code)
        db.add(user)
        created.append({"email": email, "code": code})
        logger.info(f"✅ Usuário criado (pendente): {email} com código {code}")

        # Envia o e-mail com o código
        try:
            send_verification_email(email, code)
            logger.info(f"📧 Email enviado para: {email}")
        except Exception as e:
            logger.error(f"❌ Falha ao enviar e-mail para {email}: {e}")

    db.commit()
    logger.info(f"📦 CSV processado: {len(created)} criados, {len(skipped)} ignorados")

    return {
        "created_count": len(created),
        "skipped_count": len(skipped),
        "created_users": created,
        "skipped_users": skipped
    }

# --- Cadastro com código ---
@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registro de novo usuário. Suporta:
    - Usuários normais (código de 6 dígitos do CSV): Email precisa ser pré-cadastrado
    - Admin (código especial do .env: ADMIN_VERIFICATION_CODE): Email é criado automaticamente
    
    Cria automaticamente Profile e UserStats após o registro.
    """
    logger.info(f"🔐 Registro iniciado para: {user_in.email}")
    logger.debug(f"   Código recebido: {user_in.verification_code}")
    logger.debug(f"   Código admin esperado: {settings.ADMIN_VERIFICATION_CODE}")
    
    # Verifica se é código admin
    is_admin_code = user_in.verification_code == settings.ADMIN_VERIFICATION_CODE
    logger.info(f"   É código admin? {is_admin_code}")
    
    user = db.query(User).filter(User.email == user_in.email).first()
    logger.debug(f"   Usuário existe no banco? {user is not None}")
    
    # Se for código admin E o email não existe, criar o usuário
    if is_admin_code and not user:
        logger.info(f"🛡️  Criando novo admin: {user_in.email}")
        user = User(
            email=user_in.email,
            verification_code=None,
            is_admin=True,
            role="admin"
        )
        db.add(user)
        db.flush()
        logger.info(f"   Admin criado com user_id={user.id}, role={user.role}, is_admin={user.is_admin}")
    
    # Se não for admin e o email não existe, erro
    elif not is_admin_code and not user:
        logger.warning(f"❌ Email não pré-cadastrado: {user_in.email}")
        raise HTTPException(status_code=400, detail="Email não pré-cadastrado")
    
    # Se for admin, ignora validação do código
    # Se não for admin, valida o código
    if not is_admin_code and user.verification_code != user_in.verification_code:
        logger.warning(f"❌ Código inválido para {user_in.email}")
        raise HTTPException(status_code=400, detail="Código de verificação inválido")

    # Atualizar usuário
    user.hashed_password = hash_password(user_in.password)
    user.is_verified = True
    user.verification_code = None
    
    # Se for código normal, define como student
    if not is_admin_code:
        logger.info(f"👤 Criando aluno comum: {user_in.email}")
        user.role = "student"
    else:
        logger.info(f"🛡️  Confirmando admin: {user_in.email}")
    
    db.add(user)
    db.flush()
    logger.debug(f"   User após atualização: role={user.role}, is_admin={user.is_admin}, is_verified={user.is_verified}")

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
            threads_count=0,
            comments_count=0,
            events_count=0
        )
        db.add(stats)
        logger.info(f"✅ UserStats criado para user_id={user.id}")
    else:
        logger.debug(f"ℹ️  UserStats já existe para user_id={user.id}")

    db.commit()
    db.refresh(user)
    
    logger.info(f"✅ Registro completo: {user_in.email}")
    logger.info(f"   ID: {user.id}, Role: {user.role}, Is Admin: {user.is_admin}, Is Verified: {user.is_verified}")
    
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
    
    logger.info(f"✅ Login bem-sucedido: {form_data.username} (role={user.role})")
    
    # ✅ INCLUIR user_id E role NO TOKEN
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id,    # ← ADICIONADO
            "role": user.role      # ← JÁ ESTAVA
        },
        expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}