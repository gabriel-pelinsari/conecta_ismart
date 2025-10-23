from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # colunas já existentes
    is_active = Column(Boolean, nullable=False, server_default="true")
    is_admin = Column(Boolean, nullable=False, server_default="false")  # legado/opcional

    # novas colunas que seu código usa
    is_verified = Column(Boolean, nullable=False, server_default="false")
    verification_code = Column(String(6), nullable=True)
    role = Column(String(20), nullable=False, server_default="student")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
