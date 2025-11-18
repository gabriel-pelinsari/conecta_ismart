from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db, get_current_user
from app.models.poll import Poll, PollOption, PollVote
from app.models.profile import Profile
from app.models.user import User
from app.schemas.poll import (
    PollCreate,
    PollOut,
    PollVoteRequest,
    PollCreatorOut,
    PollOptionOut,
)

router = APIRouter(prefix="/api/polls", tags=["polls"])


def _serialize_poll(poll: Poll, current_user: Optional[User], db: Session) -> PollOut:
    profile = (
        db.query(Profile).filter(Profile.user_id == poll.created_by).first()
    )
    creator = PollCreatorOut(
        user_id=poll.created_by,
        nickname=profile.nickname if profile else None,
        full_name=profile.full_name if profile else None,
        university=profile.university if profile else None,
    )

    user_vote = None
    if current_user:
        vote = (
            db.query(PollVote)
            .filter(
                PollVote.poll_id == poll.id,
                PollVote.user_id == current_user.id,
            )
            .first()
        )
        if vote and vote.option:
            user_vote = vote.option.label

    options = [
        PollOptionOut(id=option.id, label=option.label, votes_count=option.votes_count)
        for option in poll.options
    ]

    return PollOut(
        id=poll.id,
        title=poll.title,
        description=poll.description,
        audience=poll.audience,
        created_at=poll.created_at,
        creator=creator,
        options=options,
        user_vote=user_vote,
    )


@router.get("/", response_model=List[PollOut])
def list_polls(
    audience: Optional[str] = Query(
        None, description="Filtra por p��blico alvo (geral ou faculdade)"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Poll)
        .options(selectinload(Poll.options))
        .order_by(Poll.created_at.desc())
    )
    if audience:
        query = query.filter(Poll.audience == audience)
    polls = query.offset(skip).limit(limit).all()
    return [_serialize_poll(poll, current_user, db) for poll in polls]


@router.post("/", response_model=PollOut, status_code=status.HTTP_201_CREATED)
def create_poll(
    payload: PollCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    unique_options = []
    seen = set()
    for option in payload.options:
        label = option.strip()
        if not label:
            continue
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_options.append(label)

    if len(unique_options) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forne��a pelo menos duas op��es distintas para a enquete.",
        )

    poll = Poll(
        title=payload.title,
        description=payload.description,
        audience=payload.audience,
        created_by=current_user.id,
    )
    db.add(poll)
    db.flush()

    for label in unique_options:
        option = PollOption(poll_id=poll.id, label=label, votes_count=0)
        db.add(option)

    db.commit()
    db.refresh(poll)

    poll = (
        db.query(Poll)
        .options(selectinload(Poll.options))
        .filter(Poll.id == poll.id)
        .first()
    )
    return _serialize_poll(poll, current_user, db)


@router.post("/{poll_id}/vote", response_model=PollOut)
def vote_poll(
    poll_id: int,
    payload: PollVoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    poll = (
        db.query(Poll)
        .options(selectinload(Poll.options))
        .filter(Poll.id == poll_id)
        .first()
    )
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquete n��o encontrada.")

    label = (payload.option_label or "").strip()
    existing_vote = (
        db.query(PollVote)
        .filter(
            PollVote.poll_id == poll_id,
            PollVote.user_id == current_user.id,
        )
        .first()
    )

    def decrement_option(option_obj: PollOption):
        if option_obj.votes_count > 0:
            option_obj.votes_count -= 1

    if not label:
        if existing_vote:
            decrement_option(existing_vote.option)
            db.delete(existing_vote)
            db.commit()
        return _serialize_poll(poll, current_user, db)

    target_option = None
    for option in poll.options:
        if option.label.lower() == label.lower():
            target_option = option
            break

    if not target_option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Op��o da enquete n��o encontrada.",
        )

    if existing_vote and existing_vote.option_id == target_option.id:
        decrement_option(existing_vote.option)
        db.delete(existing_vote)
    elif existing_vote:
        decrement_option(existing_vote.option)
        existing_vote.option_id = target_option.id
        target_option.votes_count += 1
    else:
        vote = PollVote(
            poll_id=poll_id,
            option_id=target_option.id,
            user_id=current_user.id,
        )
        target_option.votes_count += 1
        db.add(vote)

    db.commit()
    poll = (
        db.query(Poll)
        .options(selectinload(Poll.options))
        .filter(Poll.id == poll_id)
        .first()
    )
    return _serialize_poll(poll, current_user, db)
