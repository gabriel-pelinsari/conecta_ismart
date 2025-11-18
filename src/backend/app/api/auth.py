from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from sqlalchemy.orm import Session

from datetime import timedelta

from app.api.deps import get_db

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



# --- Funo auxiliar ---

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

    Recebe um arquivo CSV com uma coluna 'email' e cria usurios pendentes.

    Ignora e-mails j cadastrados. Envia o cdigo de verificao por e-mail.

    """

    logger.info(f" Upload CSV iniciado: {file.filename}")

    

    if not file.filename.endswith(".csv"):

        raise HTTPException(status_code=400, detail="O arquivo deve ser um CSV vlido.")



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

        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            logger.warning(f"  Email j existe: {email}")
            skipped.append(email)
            continue

        verification_code = generate_verification_code()
        user = User(
            email=email,
            is_active=False,
            is_verified=False,
            verification_code=verification_code,
        )
        db.add(user)
        created.append({"email": email, "verification_code": verification_code})
        logger.info(f" Usurio criado (pendente): {email} - code={verification_code}")

        try:
            send_verification_email(email, verification_code)
        except Exception as e:
            logger.error(f" Falha ao enviar e-mail para {email}: {e}")



    db.commit()

    logger.info(f" CSV processado: {len(created)} criados, {len(skipped)} ignorados")



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
    logger.info(f" Registro iniciado para: {user_in.email}")

    user = db.query(User).filter(User.email == user_in.email).first()
    logger.debug(f"   Usuário existe no banco? {user is not None}")

    admin_exists = db.query(User).filter(User.is_admin == True).count() > 0
    is_master_password = user_in.password == settings.ADMIN_MASTER_PASSWORD

    if not user:
        if admin_exists and not is_master_password:
            raise HTTPException(
                status_code=400,
                detail="Email não encontrado. Solicite pré-cadastro ao administrador.",
            )
        logger.info(f" Criando novo usuário: {user_in.email}")
        user = User(
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            is_active=True,
            is_verified=True,
            is_admin=is_master_password,
        )
        db.add(user)
        db.flush()
        logger.info(f"   Usuário criado com user_id={user.id}")
    else:
        if user.hashed_password:
            logger.warning(f" Email já cadastrado: {user_in.email}")
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        if not user_in.verification_code:
            raise HTTPException(
                status_code=400,
                detail="Informe o código de verificação enviado pelo administrador.",
            )
        if user.verification_code != user_in.verification_code:
            logger.warning(" Código de verificação inválido")
            raise HTTPException(
                status_code=400,
                detail="Código de verificação inválido.",
            )
        user.hashed_password = hash_password(user_in.password)
        user.is_active = True
        user.is_verified = True
        user.is_admin = user.is_admin or is_master_password
        user.verification_code = None
        logger.info(f" Usuário pendente ativado: {user.email}")

    if not admin_exists and not user.is_admin:
        user.is_admin = True
        logger.info("   Nenhum admin encontrado, promovendo este usuário a administrador.")
    elif user.is_admin:
        logger.info("   Senha mestre detectada - privilégios de administrador concedidos.")

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(
            user_id=user.id,
            full_name=user.email.split("@")[0],
            is_public=True
        )
        db.add(profile)
        logger.info(f" Profile criado para user_id={user.id}")

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
        logger.info(f" UserStats criado para user_id={user.id}")

    db.commit()
    db.refresh(user)

    logger.info(f" Registro completo: {user_in.email}")
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

    logger.info(f" Login tentativa: {form_data.username}")

    

    user = db.query(User).filter(User.email == form_data.username).first()

    

    if not user:

        logger.warning(f" Usurio no encontrado: {form_data.username}")

        raise HTTPException(status_code=400, detail="Usurio no encontrado ou sem senha definida")

    

    if not user.hashed_password:

        logger.warning(f" Usurio sem senha: {form_data.username}")

        raise HTTPException(status_code=400, detail="Usurio no encontrado ou sem senha definida")

    

    if not verify_password(form_data.password, user.hashed_password):

        logger.warning(f" Senha incorreta: {form_data.username}")

        raise HTTPException(status_code=400, detail="Senha incorreta")

    

    if not user.is_verified:

        logger.warning(f" Conta no verificada: {form_data.username}")

        raise HTTPException(status_code=403, detail="Conta no verificada")

    

    logger.info(f" Login bem-sucedido: {form_data.username} (is_admin={user.is_admin})")


    # Incluir user_id no token

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id,
            "is_admin": user.is_admin,
            "role": "admin" if user.is_admin else "student",
        },
        expires_delta=access_token_expires,
    )
    return {"access_token": token, "token_type": "bearer"}
