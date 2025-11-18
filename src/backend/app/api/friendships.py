import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.models.social import Friendship
from app.schemas.friendship import (
    FriendOut,
    FriendRequestOut,
    FriendshipResponse,
    FriendListResponse,
)
from app.services.social_graph import (
    create_friendship,
    respond_friendship,
    get_friend_status,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/friendships", tags=["friendships"])


@router.get("/", response_model=FriendListResponse)
def list_friends(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📋 Lista todos os amigos aceitos do usuário atual

    - Retorna perfis completos dos amigos
    - Suporta paginação
    - Ordenado por data de criação (mais recentes primeiro)
    """
    logger.info(f"📋 User {current_user.id} listing friends")

    # Buscar amizades aceitas (bidirecional)
    friendships = (
        db.query(Friendship)
        .filter(
            or_(
                Friendship.user_id == current_user.id,
                Friendship.friend_id == current_user.id,
            ),
            Friendship.status == "accepted",
        )
        .order_by(Friendship.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = (
        db.query(Friendship)
        .filter(
            or_(
                Friendship.user_id == current_user.id,
                Friendship.friend_id == current_user.id,
            ),
            Friendship.status == "accepted",
        )
        .count()
    )

    friends_list = []
    for friendship in friendships:
        # Determinar qual é o amigo (não o usuário atual)
        friend_id = (
            friendship.friend_id
            if friendship.user_id == current_user.id
            else friendship.user_id
        )

        # Buscar perfil do amigo
        profile = db.query(Profile).filter(Profile.user_id == friend_id).first()
        if profile:
            friends_list.append(
                FriendOut(
                    user_id=friend_id,
                    full_name=profile.full_name,
                    nickname=profile.nickname,
                    university=profile.university,
                    course=profile.course,
                    semester=profile.semester,
                    photo_url=profile.photo_url,
                    status="accepted",
                    created_at=friendship.created_at,
                )
            )

    return FriendListResponse(friends=friends_list, total=total)


@router.get("/pending/sent", response_model=List[FriendRequestOut])
def list_sent_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📤 Lista solicitações de amizade enviadas (pendentes)

    - Retorna perfis dos usuários para quem você enviou solicitação
    - Apenas solicitações com status 'pending'
    """
    logger.info(f"📤 User {current_user.id} listing sent friend requests")

    sent_requests = (
        db.query(Friendship)
        .filter(
            Friendship.user_id == current_user.id,
            Friendship.status == "pending",
        )
        .order_by(Friendship.created_at.desc())
        .all()
    )

    requests_list = []
    for request in sent_requests:
        profile = db.query(Profile).filter(Profile.user_id == request.friend_id).first()
        if profile:
            requests_list.append(
                FriendRequestOut(
                    user_id=request.friend_id,
                    full_name=profile.full_name,
                    nickname=profile.nickname,
                    university=profile.university,
                    photo_url=profile.photo_url,
                    created_at=request.created_at,
                )
            )

    return requests_list


@router.get("/pending/received", response_model=List[FriendRequestOut])
def list_received_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📥 Lista solicitações de amizade recebidas (pendentes)

    - Retorna perfis dos usuários que enviaram solicitação
    - Apenas solicitações com status 'pending'
    - Pode aceitar ou rejeitar através do endpoint de resposta
    """
    logger.info(f"📥 User {current_user.id} listing received friend requests")

    received_requests = (
        db.query(Friendship)
        .filter(
            Friendship.friend_id == current_user.id,
            Friendship.status == "pending",
        )
        .order_by(Friendship.created_at.desc())
        .all()
    )

    requests_list = []
    for request in received_requests:
        profile = db.query(Profile).filter(Profile.user_id == request.user_id).first()
        if profile:
            requests_list.append(
                FriendRequestOut(
                    user_id=request.user_id,
                    full_name=profile.full_name,
                    nickname=profile.nickname,
                    university=profile.university,
                    photo_url=profile.photo_url,
                    created_at=request.created_at,
                )
            )

    return requests_list


@router.delete("/{user_id}", response_model=FriendshipResponse)
def remove_friend(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ❌ Remove uma amizade existente

    - Deleta ambos os lados da amizade (bidirecional)
    - Funciona para amizades aceitas ou solicitações pendentes
    """
    logger.info(f"❌ User {current_user.id} removing friendship with user {user_id}")

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode remover amizade consigo mesmo",
        )

    # Verificar se o usuário existe
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    # Deletar ambos os lados da amizade
    deleted_count = (
        db.query(Friendship)
        .filter(
            or_(
                and_(
                    Friendship.user_id == current_user.id,
                    Friendship.friend_id == user_id,
                ),
                and_(
                    Friendship.user_id == user_id,
                    Friendship.friend_id == current_user.id,
                ),
            )
        )
        .delete(synchronize_session=False)
    )

    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Amizade não encontrada",
        )

    db.commit()

    return FriendshipResponse(
        status="success",
        message="Amizade removida com sucesso",
    )


@router.get("/search", response_model=List[FriendOut])
def search_friends(
    query: str = Query(..., min_length=1, max_length=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🔍 Busca amigos por nome ou nickname

    - Busca apenas entre amigos aceitos
    - Case-insensitive search
    - Busca em full_name e nickname
    """
    logger.info(f"🔍 User {current_user.id} searching friends with query: {query}")

    # Buscar IDs de amigos aceitos
    friendships = (
        db.query(Friendship)
        .filter(
            or_(
                Friendship.user_id == current_user.id,
                Friendship.friend_id == current_user.id,
            ),
            Friendship.status == "accepted",
        )
        .all()
    )

    friend_ids = []
    friendship_map = {}  # Para manter a data de criação
    for friendship in friendships:
        friend_id = (
            friendship.friend_id
            if friendship.user_id == current_user.id
            else friendship.user_id
        )
        friend_ids.append(friend_id)
        friendship_map[friend_id] = friendship.created_at

    if not friend_ids:
        return []

    # Buscar perfis que correspondam à query
    search_pattern = f"%{query}%"
    profiles = (
        db.query(Profile)
        .filter(
            Profile.user_id.in_(friend_ids),
            or_(
                Profile.full_name.ilike(search_pattern),
                Profile.nickname.ilike(search_pattern),
            ),
        )
        .all()
    )

    results = []
    for profile in profiles:
        results.append(
            FriendOut(
                user_id=profile.user_id,
                full_name=profile.full_name,
                nickname=profile.nickname,
                university=profile.university,
                course=profile.course,
                semester=profile.semester,
                photo_url=profile.photo_url,
                status="accepted",
                created_at=friendship_map[profile.user_id],
            )
        )

    return results


@router.get("/status/{user_id}", response_model=dict)
def check_friendship_status(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🔍 Verifica o status de amizade com um usuário específico

    Retorna:
    - "self": é o próprio usuário
    - "friends": são amigos
    - "pending": você enviou solicitação (aguardando)
    - "incoming": você recebeu solicitação
    - "none": sem relação
    """
    logger.info(f"🔍 User {current_user.id} checking friendship status with {user_id}")

    status_value = get_friend_status(db, current_user.id, user_id)

    return {"user_id": user_id, "status": status_value}
