import pytest
from io import BytesIO

def test_get_my_profile_creates_if_not_exists(client, admin_user, auth_headers):
    """Teste: GET /profiles/me cria perfil se não existir"""
    response = client.get("/profiles/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == admin_user.id
    assert "full_name" in data
    assert "interests" in data
    assert "stats" in data
    assert "badges" in data

def test_update_my_profile(client, admin_user, auth_headers):
    """Teste: PUT /profiles/me atualiza perfil"""
    profile_data = {
        "full_name": "João Silva",
        "nickname": "Joãozinho",
        "university": "USP",
        "course": "Engenharia",
        "semester": "5º semestre",
        "bio": "Estudante apaixonado por tecnologia",
        "linkedin": "https://linkedin.com/in/joao",
        "instagram": "@joao",
        "whatsapp": "11999999999",
        "show_whatsapp": True,
        "is_public": True
    }
    
    response = client.put(
        "/profiles/me",
        json=profile_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "João Silva"
    assert data["nickname"] == "Joãozinho"
    assert data["bio"] == "Estudante apaixonado por tecnologia"
    assert data["university"] == "USP"
    assert data["whatsapp"] == "11999999999"
    assert data["show_whatsapp"] is True

def test_get_my_profile_after_update(client, admin_user, auth_headers):
    """Teste: Verificar se as mudanças persistiram"""
    # Atualizar
    client.put(
        "/profiles/me",
        json={
            "full_name": "Maria Costa",
            "bio": "Desenvolvedora Full Stack",
            "university": "UNICAMP",
            "course": "Ciência da Computação",
            "semester": "3º semestre",
            "linkedin": None,
            "instagram": None,
            "whatsapp": None,
            "show_whatsapp": False,
            "is_public": True
        },
        headers=auth_headers
    )
    
    # Buscar novamente
    response = client.get("/profiles/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Maria Costa"
    assert data["bio"] == "Desenvolvedora Full Stack"
    assert data["university"] == "UNICAMP"

def test_get_other_user_profile_public(client, admin_user, student_user, student_token):
    """Teste: Ver perfil público de outro usuário"""
    # Criar perfil do admin
    admin_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Admin cria seu perfil público
    from app.models.profile import Profile
    from app.db.session import TestingSessionLocal
    db = TestingSessionLocal()
    
    profile = Profile(
        user_id=admin_user.id,
        full_name="Admin User",
        university="USP",
        is_public=True,
        linkedin="https://linkedin.com/admin",
        whatsapp="11999999999"
    )
    db.add(profile)
    db.commit()
    db.close()
    
    # Student tenta ver perfil do admin
    response = client.get(
        f"/profiles/{admin_user.id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Admin User"
    # Redes sociais NÃO devem aparecer (não são amigos)
    assert "linkedin" not in data or data.get("linkedin") is None
    assert "whatsapp" not in data or data.get("whatsapp") is None

def test_upload_photo_valid(client, admin_user, auth_headers):
    """Teste: Upload de foto válida"""
    # Criar uma imagem fake (PNG de 1x1 pixel)
    fake_image = BytesIO(
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    
    response = client.post(
        "/profiles/me/photo",
        files={"file": ("test.png", fake_image, "image/png")},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "photo_url" in data
    assert data["photo_url"].startswith("/media/avatars/")

def test_upload_photo_invalid_type(client, auth_headers):
    """Teste: Upload de arquivo não-imagem"""
    fake_file = BytesIO(b"not an image")
    
    response = client.post(
        "/profiles/me/photo",
        files={"file": ("test.txt", fake_file, "text/plain")},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "inválido" in response.json()["detail"]

def test_profile_stats_integration(client, admin_user, auth_headers):
    """Teste: Stats aparecem no perfil"""
    response = client.get("/profiles/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "threads_count" in data["stats"]
    assert "comments_count" in data["stats"]
    assert "events_count" in data["stats"]
    assert data["stats"]["threads_count"] == 0  # Inicial

def test_profile_badges_integration(client, admin_user, auth_headers):
    """Teste: Badges aparecem no perfil"""
    response = client.get("/profiles/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "badges" in data
    assert isinstance(data["badges"], list)