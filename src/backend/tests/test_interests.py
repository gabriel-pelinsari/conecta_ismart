import pytest

def test_create_interest(client, auth_headers):
    """Teste: Criar novo interesse"""
    response = client.post(
        "/interests/",
        json={"name": "Programação"},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Programação"
    assert "id" in data

def test_create_duplicate_interest(client, auth_headers):
    """Teste: Não permitir interesse duplicado"""
    client.post(
        "/interests/",
        json={"name": "Música"},
        headers=auth_headers
    )
    
    response = client.post(
        "/interests/",
        json={"name": "Música"},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "já existe" in response.json()["detail"]

def test_list_all_interests(client, auth_headers):
    """Teste: Listar todos os interesses"""
    # Criar alguns interesses
    client.post("/interests/", json={"name": "Esportes"}, headers=auth_headers)
    client.post("/interests/", json={"name": "Leitura"}, headers=auth_headers)
    client.post("/interests/", json={"name": "Música"}, headers=auth_headers)
    
    response = client.get("/interests/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert any(i["name"] == "Esportes" for i in data)

def test_add_interest_to_profile(client, auth_headers, db):
    """Teste: Adicionar interesse ao perfil"""
    # Criar interesse
    from app.models.social import Interest
    interest = Interest(name="Programação")
    db.add(interest)
    db.commit()
    db.refresh(interest)
    
    response = client.post(
        f"/interests/me/{interest.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "sucesso" in data["message"]

def test_add_nonexistent_interest(client, auth_headers):
    """Teste: Tentar adicionar interesse que não existe"""
    response = client.post(
        "/interests/me/9999",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

def test_add_duplicate_interest_to_profile(client, auth_headers, db):
    """Teste: Não permitir adicionar interesse duplicado ao perfil"""
    from app.models.social import Interest
    interest = Interest(name="Música")
    db.add(interest)
    db.commit()
    db.refresh(interest)
    
    # Adicionar primeira vez
    client.post(f"/interests/me/{interest.id}", headers=auth_headers)
    
    # Tentar adicionar novamente
    response = client.post(
        f"/interests/me/{interest.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "já adicionado" in response.json()["detail"]

def test_get_my_interests(client, auth_headers, db):
    """Teste: Listar meus interesses"""
    from app.models.social import Interest
    from app.models.user import User
    from app.models.social import UserInterest
    
    # Criar interesses
    int1 = Interest(name="Esportes")
    int2 = Interest(name="Cinema")
    db.add_all([int1, int2])
    db.commit()
    
    # Adicionar ao perfil
    client.post(f"/interests/me/{int1.id}", headers=auth_headers)
    client.post(f"/interests/me/{int2.id}", headers=auth_headers)
    
    # Buscar
    response = client.get("/interests/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["interests"]) == 2

def test_remove_interest_from_profile(client, auth_headers, db):
    """Teste: Remover interesse do perfil"""
    from app.models.social import Interest
    
    interest = Interest(name="Dança")
    db.add(interest)
    db.commit()
    db.refresh(interest)
    
    # Adicionar
    client.post(f"/interests/me/{interest.id}", headers=auth_headers)
    
    # Remover
    response = client.delete(
        f"/interests/me/{interest.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204

def test_remove_nonexistent_interest_from_profile(client, auth_headers):
    """Teste: Tentar remover interesse que não está no perfil"""
    response = client.delete(
        "/interests/me/9999",
        headers=auth_headers
    )
    
    assert response.status_code == 404

def test_profile_shows_interests(client, auth_headers, db):
    """Teste: Perfil exibe interesses corretamente"""
    from app.models.social import Interest
    
    # Criar e adicionar interesses
    int1 = Interest(name="Tecnologia")
    int2 = Interest(name="Artes")
    db.add_all([int1, int2])
    db.commit()
    
    client.post(f"/interests/me/{int1.id}", headers=auth_headers)
    client.post(f"/interests/me/{int2.id}", headers=auth_headers)
    
    # Buscar perfil
    response = client.get("/profiles/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["interests"]) == 2
    assert any(i["name"] == "Tecnologia" for i in data["interests"])
    assert any(i["name"] == "Artes" for i in data["interests"])