import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User
from app.core.security import hash_password

# Banco de dados de teste em memória
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Cria um banco de dados limpo para cada teste"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Cliente de teste do FastAPI"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db):
    """Cria um usuário admin para testes"""
    user = User(
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        is_admin=True,
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def student_user(db):
    """Cria um usuário estudante para testes"""
    user = User(
        email="student@test.com",
        hashed_password=hash_password("student123"),
        is_admin=False,
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def admin_token(client, admin_user):
    """Obtém token de autenticação do admin"""
    response = client.post(
        "/auth/token",
        data={
            "email": "admin@test.com",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def student_token(client, student_user):
    """Obtém token de autenticação do estudante"""
    response = client.post(
        "/auth/token",
        data={
            "email": "student@test.com",
            "password": "student123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(admin_token):
    """Headers com token de autenticação"""
    return {"Authorization": f"Bearer {admin_token}"}