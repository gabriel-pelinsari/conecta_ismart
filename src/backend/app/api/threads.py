# backend/app/api/threads.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.thread import Thread, Comment, ThreadVote, CommentVote
from app.schemas.thread import ThreadCreate, ThreadOut, CommentCreate, CommentOut, VoteIn
from app.api.deps import get_current_user

router = APIRouter(prefix="/threads", tags=["Threads"])

# === Criar Thread ===
@router.post("/", response_model=ThreadOut)
def create_thread(data: ThreadCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Perfil não encontrado.")

    thread = Thread(
        title=data.title,
        description=data.description,
        category=data.category,
        tags=",".join(data.tags or []),
        user_id=user.id,
        university=profile.university
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return enrich_thread(thread, db)

# === Buscar Threads com Filtros e Paginação ===
@router.get("/", response_model=List[ThreadOut])
def list_threads(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    university: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Thread)

    if search:
        query = query.filter(Thread.title.ilike(f"%{search}%"))

    if category:
        query = query.filter(Thread.category == category)

    if university:
        query = query.filter(Thread.university == university)

    query = query.order_by(desc(Thread.created_at)).offset(skip).limit(limit)
    threads = query.all()
    return [enrich_thread(t, db) for t in threads]

# === Ver Thread por ID ===
@router.get("/{thread_id}", response_model=ThreadOut)
def get_thread(thread_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread não encontrada.")
    return enrich_thread(thread, db)

# === Comentar em Thread ===
@router.post("/{thread_id}/comments", response_model=CommentOut)
def create_comment(thread_id: int, data: CommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread não encontrada.")

    comment = Comment(
        thread_id=thread_id,
        content=data.content,
        user_id=user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return enrich_comment(comment, db)

# === Listar comentários de uma thread ===
@router.get("/{thread_id}/comments", response_model=List[CommentOut])
def list_comments(thread_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread não encontrada.")

    comments = (
        db.query(Comment)
        .filter(Comment.thread_id == thread_id)
        .order_by(Comment.created_at.desc())
        .all()
    )

    return [enrich_comment(c, db) for c in comments]


# === Votar em Thread ===
@router.post("/{thread_id}/vote")
def vote_thread(thread_id: int, vote: VoteIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(ThreadVote).filter_by(thread_id=thread_id, user_id=user.id).first()

    if existing:
        if existing.value == vote.value:
            # mesmo voto → remove (toggle)
            db.delete(existing)
            message = "Voto removido."
        else:
            # voto diferente → substitui
            existing.value = vote.value
            message = "Voto atualizado."
    else:
        db.add(ThreadVote(thread_id=thread_id, user_id=user.id, value=vote.value))
        message = "Voto registrado."

    db.commit()
    return {"message": message}


# === Votar em Comentário ===
@router.post("/comments/{comment_id}/vote")
def vote_comment(comment_id: int, vote: VoteIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(CommentVote).filter_by(comment_id=comment_id, user_id=user.id).first()

    if existing:
        if existing.value == vote.value:
            db.delete(existing)
            message = "Voto removido."
        else:
            existing.value = vote.value
            message = "Voto atualizado."
    else:
        db.add(CommentVote(comment_id=comment_id, user_id=user.id, value=vote.value))
        message = "Voto registrado."

    db.commit()
    return {"message": message}

# === Denunciar Thread ===
@router.post("/{thread_id}/report")
def report_thread(thread_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread não encontrada.")
    thread.is_reported = True
    db.commit()
    return {"message": "Thread denunciada com sucesso."}

# === Admin: listar denunciadas ===
@router.get("/denuncias", response_model=List[ThreadOut])
def list_reported(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas admins podem acessar.")
    threads = db.query(Thread).filter(Thread.is_reported == True).all()
    return [enrich_thread(t, db) for t in threads]

# === Admin: deletar thread ===
@router.delete("/{thread_id}")
def delete_thread(thread_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread não encontrada.")
    if thread.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Sem permissão.")
    db.delete(thread)
    db.commit()
    return {"message": "Thread deletada."}

# === Helpers ===
def enrich_thread(thread: Thread, db: Session) -> ThreadOut:
    from app.schemas.user import UserOut
    author = db.query(User).filter(User.id == thread.user_id).first()
    upvotes = db.query(func.count()).select_from(ThreadVote).filter(ThreadVote.thread_id == thread.id, ThreadVote.value == 1).scalar()
    downvotes = db.query(func.count()).select_from(ThreadVote).filter(ThreadVote.thread_id == thread.id, ThreadVote.value == -1).scalar()
    top_comments = (
        db.query(Comment)
        .filter(Comment.thread_id == thread.id)
        .outerjoin(CommentVote)
        .group_by(Comment.id)
        .order_by(func.coalesce(func.sum(CommentVote.value), 0).desc())
        .limit(3)
        .all()
    )
    return ThreadOut(
        id=thread.id,
        title=thread.title,
        description=thread.description,
        category=thread.category,
        tags=thread.tags.split(",") if thread.tags else [],
        user_id=thread.user_id,
        university=thread.university,
        created_at=thread.created_at,
        author=UserOut.from_orm(author),
        upvotes=upvotes,
        downvotes=downvotes,
        is_reported=thread.is_reported,
        top_comments=[enrich_comment(c, db) for c in top_comments]
    )

def enrich_comment(comment: Comment, db: Session) -> CommentOut:
    from app.schemas.user import UserOut
    author = db.query(User).filter(User.id == comment.user_id).first()
    upvotes = db.query(func.count()).select_from(CommentVote).filter(CommentVote.comment_id == comment.id, CommentVote.value == 1).scalar()
    downvotes = db.query(func.count()).select_from(CommentVote).filter(CommentVote.comment_id == comment.id, CommentVote.value == -1).scalar()
    return CommentOut(
        id=comment.id,
        content=comment.content,
        thread_id=comment.thread_id,
        user_id=comment.user_id,
        created_at=comment.created_at,
        author=UserOut.from_orm(author),
        upvotes=upvotes,
        downvotes=downvotes
    )
