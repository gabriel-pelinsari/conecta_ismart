from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.social import Interest, UserInterest
from app.schemas.interest import InterestOut, InterestCreate, UserInterestsOut

router = APIRouter(prefix="/interests", tags=["interests"])

@router.get("/", response_model=List[InterestOut])
def list_all_interests(db: Session = Depends(get_db)):
    """Lista todos os interesses disponíveis"""
    interests = db.query(Interest).order_by(Interest.name).all()
    return interests

@router.get("/me", response_model=UserInterestsOut)
def get_my_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista interesses do usuário logado"""
    user_interests = (
        db.query(Interest)
        .join(UserInterest)
        .filter(UserInterest.user_id == current_user.id)
        .order_by(Interest.name)
        .all()
    )
    return UserInterestsOut(interests=user_interests)

@router.post("/me/{interest_id}", status_code=status.HTTP_201_CREATED)
def add_interest_to_me(
    interest_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adiciona um interesse ao perfil do usuário"""
    # Verifica se o interesse existe
    interest = db.query(Interest).filter(Interest.id == interest_id).first()
    if not interest:
        raise HTTPException(status_code=404, detail="Interesse não encontrado")
    
    # Verifica se já não está adicionado
    existing = (
        db.query(UserInterest)
        .filter(
            UserInterest.user_id == current_user.id,
            UserInterest.interest_id == interest_id
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Interesse já adicionado")
    
    # Adiciona
    user_interest = UserInterest(user_id=current_user.id, interest_id=interest_id)
    db.add(user_interest)
    db.commit()
    
    return {"message": "Interesse adicionado com sucesso", "interest": interest.name}

@router.delete("/me/{interest_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_interest_from_me(
    interest_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um interesse do perfil do usuário"""
    user_interest = (
        db.query(UserInterest)
        .filter(
            UserInterest.user_id == current_user.id,
            UserInterest.interest_id == interest_id
        )
        .first()
    )
    
    if not user_interest:
        raise HTTPException(status_code=404, detail="Interesse não encontrado no seu perfil")
    
    db.delete(user_interest)
    db.commit()
    
    return None

@router.post("/", response_model=InterestOut, status_code=status.HTTP_201_CREATED)
def create_interest(
    payload: InterestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo interesse (apenas para testes/admin).
    Em produção, isso deveria ter aprovação por moderador.
    """
    # Verifica duplicata
    existing = db.query(Interest).filter(Interest.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Interesse já existe")
    
    interest = Interest(name=payload.name)
    db.add(interest)
    db.commit()
    db.refresh(interest)
    
    return interest