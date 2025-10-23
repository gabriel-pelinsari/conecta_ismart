from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def create_default_admin():
    db: Session = SessionLocal()
    try:
        admin_email = "admin@ismart.com"
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            return

        admin = User(
            email=admin_email,
            hashed_password=hash_password("admin"),
            is_active=True,
            is_admin=True,          # opcional/legado
            is_verified=True,       # já marcado como verificado
            role="admin",           # ← importante
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()
