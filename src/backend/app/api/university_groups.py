import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.models.social import UniversityGroup, UniversityGroupMember
from app.models.thread import Thread
from app.schemas.university_group import (
    UniversityGroupOut,
    UniversityGroupMemberOut,
    UniversityGroupStatsOut,
    MyGroupOut,
)
from app.services.university_groups import UniversityGroupService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/university-groups", tags=["university-groups"])


@router.get("/", response_model=List[UniversityGroupOut])
def list_all_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    📋 Lista todos os grupos universitários

    - Retorna todos os grupos criados
    - Inclui contagem de membros
    - Ordenado por número de membros (maior primeiro)
    - Suporta paginação
    """
    logger.info("📋 Listing all university groups")

    groups_with_stats = UniversityGroupService.get_all_groups_with_stats(db)

    # Aplicar paginação
    total = len(groups_with_stats)
    groups_with_stats = groups_with_stats[skip : skip + limit]

    # Converter para schema
    result = []
    for group_data in groups_with_stats:
        result.append(
            UniversityGroupOut(
                id=group_data["id"],
                university_name=group_data["university_name"],
                name=group_data["name"],
                description=group_data["description"],
                member_count=group_data["member_count"],
                created_at=group_data["created_at"],
                updated_at=None,
            )
        )

    logger.info(f"Found {total} university groups, returning {len(result)}")
    return result


@router.get("/{group_id}/members", response_model=List[UniversityGroupMemberOut])
def list_group_members(
    group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    👥 Lista todos os membros de um grupo universitário

    - Retorna perfis dos membros
    - Ordenado por data de entrada (mais recentes primeiro)
    - Suporta paginação
    """
    logger.info(f"👥 Listing members of group {group_id}")

    # Verificar se o grupo existe
    group = db.query(UniversityGroup).filter(UniversityGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado",
        )

    # Buscar membros com seus perfis
    members_query = (
        db.query(UniversityGroupMember, Profile)
        .join(Profile, UniversityGroupMember.user_id == Profile.user_id)
        .filter(UniversityGroupMember.group_id == group_id)
        .order_by(UniversityGroupMember.joined_at.desc())
    )

    total = members_query.count()
    members = members_query.offset(skip).limit(limit).all()

    result = []
    for member, profile in members:
        result.append(
            UniversityGroupMemberOut(
                user_id=profile.user_id,
                full_name=profile.full_name,
                nickname=profile.nickname,
                course=profile.course,
                semester=profile.semester,
                photo_url=profile.photo_url,
                joined_at=member.joined_at,
            )
        )

    logger.info(f"Found {total} members in group {group_id}, returning {len(result)}")
    return result


@router.get("/my-group", response_model=MyGroupOut)
def get_my_group(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🎓 Retorna o grupo da universidade do usuário atual

    - Se o usuário tem universidade configurada, retorna o grupo
    - Indica se o usuário já é membro
    - Se não tem universidade, retorna null
    """
    logger.info(f"🎓 User {current_user.id} requesting their university group")

    # Buscar perfil do usuário
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    if not profile or not profile.university:
        logger.info(f"User {current_user.id} has no university configured")
        return MyGroupOut(group=None, is_member=False, joined_at=None)

    # Buscar ou criar o grupo
    group = UniversityGroupService.ensure_group_exists(db, profile.university)

    # Verificar se é membro
    membership = (
        db.query(UniversityGroupMember)
        .filter(
            UniversityGroupMember.group_id == group.id,
            UniversityGroupMember.user_id == current_user.id,
        )
        .first()
    )

    # Contar membros
    member_count = UniversityGroupService.get_group_members_count(db, group.id)

    group_out = UniversityGroupOut(
        id=group.id,
        university_name=group.university_name,
        name=group.name,
        description=group.description,
        member_count=member_count,
        created_at=group.created_at,
        updated_at=group.updated_at,
    )

    return MyGroupOut(
        group=group_out,
        is_member=membership is not None,
        joined_at=membership.joined_at if membership else None,
    )


@router.post("/join", response_model=dict)
def join_my_group(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✅ Adiciona o usuário ao grupo da sua universidade

    - Automaticamente adiciona ao grupo baseado na universidade do perfil
    - Cria o grupo se não existir
    - Retorna erro se o usuário não tem universidade configurada
    """
    logger.info(f"✅ User {current_user.id} joining their university group")

    # Buscar perfil
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    if not profile or not profile.university:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você precisa configurar sua universidade no perfil primeiro",
        )

    # Adicionar ao grupo
    added = UniversityGroupService.add_user_to_group(
        db, current_user.id, profile.university
    )

    if not added:
        return {
            "status": "already_member",
            "message": "Você já é membro deste grupo",
        }

    return {
        "status": "success",
        "message": f"Você entrou no grupo {profile.university}",
    }


@router.get("/{group_id}/stats", response_model=UniversityGroupStatsOut)
def get_group_stats(
    group_id: int,
    db: Session = Depends(get_db),
):
    """
    📊 Retorna estatísticas de um grupo universitário

    - Total de membros
    - Membros ativos (postaram nos últimos 30 dias)
    - Número de threads do grupo
    - Número de eventos do grupo (quando implementado)
    """
    logger.info(f"📊 Getting stats for group {group_id}")

    # Verificar se o grupo existe
    group = db.query(UniversityGroup).filter(UniversityGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado",
        )

    # Total de membros
    total_members = UniversityGroupService.get_group_members_count(db, group_id)

    # Membros ativos (postaram nos últimos 30 dias)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_members = (
        db.query(UniversityGroupMember.user_id)
        .filter(UniversityGroupMember.group_id == group_id)
        .join(Thread, Thread.user_id == UniversityGroupMember.user_id)
        .filter(Thread.created_at >= thirty_days_ago)
        .distinct()
        .count()
    )

    # Threads da universidade
    threads_count = (
        db.query(Thread)
        .filter(Thread.university == group.university_name)
        .count()
    )

    # Eventos (placeholder - será implementado depois)
    events_count = 0

    return UniversityGroupStatsOut(
        total_members=total_members,
        active_members=active_members,
        threads_count=threads_count,
        events_count=events_count,
    )


@router.get("/by-university/{university_name}", response_model=UniversityGroupOut)
def get_group_by_university(
    university_name: str,
    db: Session = Depends(get_db),
):
    """
    🔍 Busca grupo por nome da universidade

    - Retorna o grupo da universidade especificada
    - Cria o grupo se não existir
    """
    logger.info(f"🔍 Searching group for university: {university_name}")

    group = UniversityGroupService.ensure_group_exists(db, university_name)
    member_count = UniversityGroupService.get_group_members_count(db, group.id)

    return UniversityGroupOut(
        id=group.id,
        university_name=group.university_name,
        name=group.name,
        description=group.description,
        member_count=member_count,
        created_at=group.created_at,
        updated_at=group.updated_at,
    )
