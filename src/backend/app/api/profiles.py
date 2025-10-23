import os
import uuid
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.schemas.profile import (
    ProfileUpdate, ProfilePublicOut, ProfilePrivateOut
)
from app.services.social_graph import are_friends
from app.services.stats_badges import get_user_stats, get_user_badges
from starlette.datastructures import UploadFile as StarletteUploadFile

router = APIRouter(prefix="/profiles", tags=["profiles"])

MEDIA_DIR = os.path.join(os.getcwd(), "media", "avatars")
os.makedirs(MEDIA_DIR, exist_ok=True)

ALLOWED_MIMES = {"image/jpeg", "image/png"}
MAX_BYTES = 2 * 1024 * 1024  # 2MB

def _to_public(profile: Profile) -> ProfilePublicOut:
    return ProfilePublicOut(
        user_id=profile.user_id,
        full_name=profile.full_name,
        nickname=profile.nickname,
        university=profile.university,
        course=profile.course,
        semester=profile.semester,
        bio=profile.bio,
        photo_url=profile.photo_url,
        stats=get_user_stats(profile.user_id),
        badges=get_user_badges(profile.user_id),
    )

def _to_private(profile: Profile) -> ProfilePrivateOut:
    return ProfilePrivateOut(
        user_id=profile.user_id,
        full_name=profile.full_name,
        nickname=profile.nickname,
        university=profile.university,
        course=profile.course,
        semester=profile.semester,
        bio=profile.bio,
        photo_url=profile.photo_url,
        stats=get_user_stats(profile.user_id),
        badges=get_user_badges(profile.user_id),
        linkedin=profile.linkedin,
        instagram=profile.instagram,
        whatsapp=profile.whatsapp,
        show_whatsapp=profile.show_whatsapp,
    )

@router.get("/me", response_model=ProfilePrivateOut)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        # cria básico se não existir
        profile = Profile(user_id=current_user.id, full_name=current_user.email.split("@")[0])
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return _to_private(profile)

@router.get("/{user_id}", response_model=Union[ProfilePublicOut, ProfilePrivateOut])
def get_profile(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")

    # is owner?
    if current_user.id == user_id:
        return _to_private(profile)

    # se o perfil não é público, bloqueia tudo (MVP)
    if not profile.is_public:
        raise HTTPException(status_code=403, detail="Perfil privado")

    # amigos? (quando RF002 estiver pronto)
    if are_friends(current_user.id, user_id):
        return _to_private(profile)

    # não amigo → remover socials
    return _to_public(profile)

@router.put("/me", response_model=ProfilePrivateOut)
def update_my_profile(payload: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id, full_name=current_user.email.split("@")[0])
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # aplica alterações
    for field, value in payload.dict().items():
        setattr(profile, field, value)

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _to_private(profile)

@router.post("/me/photo")
async def upload_my_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # validações
    if file.content_type not in ALLOWED_MIMES:
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido. Use JPG ou PNG.")
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máx 2MB).")

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
        profile = Profile(user_id=current_user.id, full_name=current_user.email.split("@")[0])
        db.add(profile)
        db.commit()
        db.refresh(profile)

    profile.photo_url = public_url
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {"photo_url": public_url}
