import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.report import Report
from app.models.thread import Thread, Comment
from app.models.profile import Profile
from app.schemas.report import (
    ReportCreate,
    ReportOut,
    ReportUpdate,
    ReportResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/moderation", tags=["moderation"])


def is_admin(user: User) -> bool:
    """Verifica se o usuário é admin"""
    return user.is_admin


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🚨 Criar uma denúncia

    - Tipos suportados: thread, comment, user
    - Categorias: spam, offensive, harassment, inappropriate, fake, other
    - Previne denúncias duplicadas (mesmo reporter, target e categoria)
    """
    logger.info(
        f"🚨 User {current_user.id} reporting {report_data.target_type} "
        f"#{report_data.target_id} for {report_data.category}"
    )

    # Verificar se o alvo existe
    if report_data.target_type == "thread":
        target = db.query(Thread).filter(Thread.id == report_data.target_id).first()
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread não encontrada",
            )
    elif report_data.target_type == "comment":
        target = db.query(Comment).filter(Comment.id == report_data.target_id).first()
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comentário não encontrado",
            )
    elif report_data.target_type == "user":
        target = db.query(User).filter(User.id == report_data.target_id).first()
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado",
            )

    # Prevenir denúncia duplicada
    existing_report = (
        db.query(Report)
        .filter(
            Report.reporter_id == current_user.id,
            Report.target_type == report_data.target_type,
            Report.target_id == report_data.target_id,
            Report.category == report_data.category,
            Report.status == "pending",
        )
        .first()
    )

    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já denunciou este conteúdo com a mesma categoria",
        )

    # Criar denúncia
    new_report = Report(
        reporter_id=current_user.id,
        target_type=report_data.target_type,
        target_id=report_data.target_id,
        category=report_data.category,
        description=report_data.description,
        status="pending",
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return ReportResponse(
        status="success",
        message="Denúncia criada com sucesso",
        report_id=new_report.id,
    )


@router.get("/reports", response_model=List[ReportOut])
def list_reports(
    status_filter: Optional[str] = Query(None, pattern="^(pending|reviewed|approved|rejected)$"),
    target_type: Optional[str] = Query(None, pattern="^(thread|comment|user)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📋 Listar denúncias (Admin only)

    - Filtrar por status (pending, reviewed, approved, rejected)
    - Filtrar por tipo de alvo (thread, comment, user)
    - Ordenado por data de criação (mais recente primeiro)
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar denúncias",
        )

    logger.info(f"📋 Admin {current_user.id} listing reports")

    query = db.query(Report)

    if status_filter:
        query = query.filter(Report.status == status_filter)

    if target_type:
        query = query.filter(Report.target_type == target_type)

    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    return reports


@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🔍 Ver detalhes de uma denúncia (Admin only)
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem ver denúncias",
        )

    logger.info(f"🔍 Admin {current_user.id} viewing report {report_id}")

    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Denúncia não encontrada",
        )

    return report


@router.put("/reports/{report_id}", response_model=ReportResponse)
def update_report_status(
    report_id: int,
    update_data: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ✏️ Atualizar status de uma denúncia (Admin only)

    - Status: pending, reviewed, approved, rejected
    - Registra quem revisou e quando
    - Pode adicionar notas administrativas
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem atualizar denúncias",
        )

    logger.info(
        f"✏️ Admin {current_user.id} updating report {report_id} to {update_data.status}"
    )

    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Denúncia não encontrada",
        )

    # Atualizar status
    report.status = update_data.status
    if update_data.admin_notes:
        report.admin_notes = update_data.admin_notes

    # Registrar revisão
    if update_data.status in ["reviewed", "approved", "rejected"]:
        report.reviewed_by = current_user.id
        report.reviewed_at = datetime.utcnow()

    db.commit()

    return ReportResponse(
        status="success",
        message=f"Denúncia atualizada para {update_data.status}",
    )


@router.get("/my-reports", response_model=List[ReportOut])
def get_my_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📋 Listar minhas denúncias

    - Retorna denúncias criadas pelo usuário atual
    - Ordenado por data (mais recente primeiro)
    """
    logger.info(f"📋 User {current_user.id} listing their reports")

    reports = (
        db.query(Report)
        .filter(Report.reporter_id == current_user.id)
        .order_by(Report.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return reports


@router.get("/reports/target/{target_type}/{target_id}", response_model=List[ReportOut])
def get_reports_for_target(
    target_type: str,
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🎯 Listar denúncias de um alvo específico (Admin only)

    - Retorna todas as denúncias para um thread, comment ou user específico
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem ver denúncias",
        )

    logger.info(f"🎯 Admin {current_user.id} viewing reports for {target_type} {target_id}")

    if target_type not in ["thread", "comment", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de alvo inválido. Use: thread, comment, user",
        )

    reports = (
        db.query(Report)
        .filter(
            Report.target_type == target_type,
            Report.target_id == target_id,
        )
        .order_by(Report.created_at.desc())
        .all()
    )

    return reports


@router.get("/stats", response_model=dict)
def get_moderation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    📊 Estatísticas de moderação (Admin only)

    - Total de denúncias por status
    - Total de denúncias por tipo
    - Denúncias pendentes
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem ver estatísticas",
        )

    logger.info(f"📊 Admin {current_user.id} viewing moderation stats")

    # Denúncias por status
    status_counts = {}
    for status_value in ["pending", "reviewed", "approved", "rejected"]:
        count = db.query(Report).filter(Report.status == status_value).count()
        status_counts[status_value] = count

    # Denúncias por tipo
    type_counts = {}
    for type_value in ["thread", "comment", "user"]:
        count = db.query(Report).filter(Report.target_type == type_value).count()
        type_counts[type_value] = count

    # Denúncias por categoria
    category_counts = {}
    for category in ["spam", "offensive", "harassment", "inappropriate", "fake", "other"]:
        count = db.query(Report).filter(Report.category == category).count()
        category_counts[category] = count

    total_reports = db.query(Report).count()

    return {
        "total_reports": total_reports,
        "by_status": status_counts,
        "by_type": type_counts,
        "by_category": category_counts,
    }
