from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.social import Friendship


def get_friend_status(db: Session, viewer_id: int, owner_id: int) -> str:
    if viewer_id == owner_id:
        return "self"

    outgoing = (
        db.query(Friendship)
        .filter(
            Friendship.user_id == viewer_id,
            Friendship.friend_id == owner_id,
        )
        .first()
    )
    if outgoing:
        if outgoing.status == "accepted":
            return "friends"
        if outgoing.status == "pending":
            return "pending"

    incoming = (
        db.query(Friendship)
        .filter(
            Friendship.user_id == owner_id,
            Friendship.friend_id == viewer_id,
        )
        .first()
    )
    if incoming:
        if incoming.status == "accepted":
            return "friends"
        if incoming.status == "pending":
            return "incoming"

    return "none"


def create_friendship(db: Session, requester_id: int, target_id: int) -> str:
    existing = (
        db.query(Friendship)
        .filter(
            Friendship.user_id == requester_id,
            Friendship.friend_id == target_id,
        )
        .first()
    )
    if existing:
        return existing.status

    reverse = (
        db.query(Friendship)
        .filter(
            Friendship.user_id == target_id,
            Friendship.friend_id == requester_id,
        )
        .first()
    )
    if reverse and reverse.status == "pending":
        reverse.status = "accepted"
        db.add(reverse)
        db.add(
            Friendship(
                user_id=requester_id,
                friend_id=target_id,
                status="accepted",
            )
        )
        db.commit()
        return "friends"

    db.add(
        Friendship(
            user_id=requester_id,
            friend_id=target_id,
            status="pending",
        )
    )
    db.commit()
    return "pending"


def respond_friendship(db: Session, requester_id: int, target_id: int, accept: bool) -> str:
    outgoing = (
        db.query(Friendship)
        .filter(
            Friendship.user_id == requester_id,
            Friendship.friend_id == target_id,
        )
        .first()
    )
    if not outgoing:
        raise ValueError("Pedido de amizade não encontrado.")

    if accept:
        outgoing.status = "accepted"
        reverse = (
            db.query(Friendship)
            .filter(
                Friendship.user_id == target_id,
                Friendship.friend_id == requester_id,
            )
            .first()
        )
        if reverse:
            reverse.status = "accepted"
        else:
            db.add(
                Friendship(
                    user_id=target_id,
                    friend_id=requester_id,
                    status="accepted",
                )
            )
        db.commit()
        return "friends"
    else:
        db.delete(outgoing)
        db.query(Friendship).filter(
            Friendship.user_id == target_id,
            Friendship.friend_id == requester_id,
        ).delete(synchronize_session=False)
        db.commit()
        return "none"
