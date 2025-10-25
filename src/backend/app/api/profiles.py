import os
import uuid
import logging
from typing import Union, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.models.social import Interest, UserInterest
from app.schemas.profile import (
    ProfileUpdate, ProfilePublicOut, ProfilePrivateOut
)
from app.services.social_graph import are_friends
from app.services.stats_badges import get_user_stats, get_user_badges

# === LOGGING ===
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["profiles"])

MEDIA_DIR = os.path.join(os.getcwd(), "media", "avatars")
os.makedirs(MEDIA_DIR, exist_ok=True)

ALLOWED_MIMES = {"image/jpeg", "image/png"}
MAX_BYTES = 2 * 1024 * 1024  # 2MB

def _to_public(profile: Profile, db: Session) -> ProfilePublicOut:
    # Buscar interesses do usuário
    user_interests = (
        db.query(Interest)
        .join(UserInterest)
        .filter(UserInterest.user_id == profile.user_id)
        .all()
    )
    
    return ProfilePublicOut(
        user_id=profile.user_id,
        full_name=profile.full_name,
        nickname=profile.nickname,
        university=profile.university,
        course=profile.course,
        semester=profile.semester,
        bio=profile.bio,
        photo_url=profile.photo_url,
        interests=user_interests,
        stats=get_user_stats(profile.user_id, db),
        badges=get_user_badges(profile.user_id, db),
    )

def _to_private(profile: Profile, db: Session) -> ProfilePrivateOut:
    # Buscar interesses do usuário
    user_interests = (
        db.query(Interest)
        .join(UserInterest)
        .filter(UserInterest.user_id == profile.user_id)
        .all()
    )
    
    return ProfilePrivateOut(
        user_id=profile.user_id,
        full_name=profile.full_name,
        nickname=profile.nickname,
        university=profile.university,
        course=profile.course,
        semester=profile.semester,
        bio=profile.bio,
        photo_url=profile.photo_url,
        interests=user_interests,
        stats=get_user_stats(profile.user_id, db),
        badges=get_user_badges(profile.user_id, db),
        linkedin=profile.linkedin,
        instagram=profile.instagram,
        whatsapp=profile.whatsapp,
        show_whatsapp=profile.show_whatsapp,
    )

# ✅ ROTA /me PRIMEIRO (mais específica)
@router.get("/me", response_model=ProfilePrivateOut)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna o perfil do usuário logado (privado)"""
    logger.info(f"👤 Buscando perfil do usuário: {current_user.email}")
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(
            user_id=current_user.id,
            full_name=current_user.email.split("@")[0]
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return _to_private(profile, db)

# ✅ ROTA /users SEGUNDO (mais específica que /{user_id})
@router.get("/users", response_model=List[ProfilePublicOut])
def list_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários com perfis públicos.
    Retorna informações básicas para descobrir o ID de outros usuários.
    """
    logger.info(f"📋 Listando todos os perfis públicos...")
    
    profiles = db.query(Profile).filter(Profile.is_public == True).all()
    
    logger.info(f"📋 {len(profiles)} perfis públicos encontrados")
    
    return [_to_public(profile, db) for profile in profiles]

# ✅ ROTA /{user_id} POR ÚLTIMO (menos específica)
@router.get("/{user_id}", response_model=Union[ProfilePublicOut, ProfilePrivateOut])
def get_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna o perfil de um usuário específico.
    - Se for seu próprio perfil: retorna dados privados
    - Se for amigo: retorna dados privados
    - Caso contrário: retorna apenas dados públicos
    """
    logger.info(f"🔍 Buscando perfil do usuário: {user_id}")
    
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        logger.warning(f"❌ Perfil não encontrado: {user_id}")
        raise HTTPException(status_code=404, detail="Perfil não encontrado")

    if current_user.id == user_id:
        logger.info(f"✅ Retornando perfil privado (seu perfil)")
        return _to_private(profile, db)

    if not profile.is_public:
        logger.warning(f"❌ Perfil privado: {user_id}")
        raise HTTPException(status_code=403, detail="Perfil privado")

    if are_friends(current_user.id, user_id):
        logger.info(f"✅ Retornando perfil privado (amigos)")
        return _to_private(profile, db)

    logger.info(f"✅ Retornando perfil público")
    return _to_public(profile, db)

@router.put("/me", response_model=ProfilePrivateOut)
def update_my_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza o perfil do usuário logado"""
    logger.info(f"✏️ Atualizando perfil: {current_user.email}")
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(
            user_id=current_user.id,
            full_name=current_user.email.split("@")[0]
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    for field, value in payload.dict().items():
        setattr(profile, field, value)

    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    logger.info(f"✅ Perfil atualizado: {current_user.email}")
    
    return _to_private(profile, db)

@router.post("/me/photo")
async def upload_my_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Faz upload de foto de perfil do usuário logado"""
    logger.info(f"📸 Upload de foto iniciado: {current_user.email}")
    
    # validações
    if file.content_type not in ALLOWED_MIMES:
        logger.warning(f"❌ Tipo de arquivo inválido: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail="Tipo de arquivo inválido. Use JPG ou PNG."
        )
    
    content = await file.read()
    if len(content) > MAX_BYTES:
        logger.warning(f"❌ Arquivo muito grande: {len(content)} bytes")
        raise HTTPException(
            status_code=400,
            detail="Arquivo muito grande (máx 2MB)."
        )

    # filename seguro
    ext = ".jpg" if file.content_type == "image/jpeg" else ".png"
    fname = f"{current_user.id}_{uuid.uuid4().hex}{ext}"
    fpath = os.path.join(MEDIA_DIR, fname)

    with open(fpath, "wb") as f:
        f.write(content)

    # URL pública (via StaticFiles montado)
    public_url = f"/media/avatars/{fname}"

    # salva no perfil
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(
            user_id=current_user.id,
            full_name=current_user.email.split("@")[0]
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    profile.photo_url = public_url
    db.add(profile)
    db.commit()
    db.refresh(profile)

    logger.info(f"✅ Foto salva: {public_url}")
    
    return {"photo_url": public_url}