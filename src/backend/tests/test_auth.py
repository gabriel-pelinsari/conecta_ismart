import pytest
from io import BytesIO

def test_login_success(client, admin_user):
    """Teste: Login com credenciais válidas"""
    response = client.post(
        "/auth/token",
        data={
            "email": "admin@test.com",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, admin_user):
    """Teste: Login com senha incorreta"""
    response = client.post(
        "/auth/token",
        data={
            "email": "admin@test.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 400
    assert "Senha incorreta" in response.json()["detail"]

def test_login_user_not_found(client):
    """Teste: Login com usuário inexistente"""
    response = client.post(
        "/auth/token",
        data={
            "email": "notfound@test.com",
            "password": "any"
        }
    )
    assert response.status_code == 400

def test_upload_csv_valid(client, admin_user, auth_headers):
    """Teste: Upload de CSV válido"""
    csv_content = b"email\ntest1@example.com\ntest2@example.com"
    
    response = client.post(
        "/auth/upload-csv",
        files={"file": ("emails.csv", BytesIO(csv_content), "text/csv")},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created_count"] == 2
    assert len(data["created_users"]) == 2
    assert all("verification_code" in item for item in data["created_users"])

def test_upload_csv_invalid_format(client, auth_headers):
    """Teste: Upload de arquivo não-CSV"""
    txt_content = b"not a csv file"
    
    response = client.post(
        "/auth/upload-csv",
        files={"file": ("test.txt", BytesIO(txt_content), "text/plain")},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "CSV válido" in response.json()["detail"]

def test_upload_csv_missing_email_column(client, auth_headers):
    """Teste: CSV sem coluna 'email'"""
    csv_content = b"nome\nJoao\nMaria"
    
    response = client.post(
        "/auth/upload-csv",
        files={"file": ("test.csv", BytesIO(csv_content), "text/csv")},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "coluna chamada 'email'" in response.json()["detail"]

def test_register_with_valid_code(client, db):
    """Teste: Registro com código válido"""
    from app.models.user import User
    
    # Criar usuário pré-cadastrado
    user = User(
        email="newuser@test.com",
        verification_code="123456"
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "ValidPass123!",
            "verification_code": "123456"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["is_verified"] is True

def test_register_with_invalid_code(client, db):
    """Teste: Registro com código inválido"""
    from app.models.user import User
    
    user = User(
        email="newuser@test.com",
        verification_code="123456"
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "ValidPass123!",
            "verification_code": "WRONG"
        }
    )
    
    assert response.status_code == 400
    assert "inválido" in response.json()["detail"]

def test_register_weak_password(client, db):
    """Teste: Registro com senha fraca"""
    from app.models.user import User
    
    user = User(
        email="newuser@test.com",
        verification_code="123456"
    )
    db.add(user)
    db.commit()
    
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "weak",
            "verification_code": "123456"
        }
    )
    
    assert response.status_code == 422  # Validation error
