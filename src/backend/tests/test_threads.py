# backend/tests/test_threads.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ——————————————————————————
# Usuários de teste existentes
USER_A = {"email": "gabriel.pelinsari.ismart@gmail.com", "password": "Inteli123"}
USER_B = {"email": "gabriel.pelinsari.spam@gmail.com", "password": "Inteli123"}

# backend/tests/test_threads.py

def get_token(user):
    resp = client.post(
        "/auth/token",
        data={"email": user["email"], "password": user["password"]},  # <- email aqui
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 200, f"Login failed for {user['email']}: {resp.text}"
    return resp.json()["access_token"]

@pytest.fixture
def token_a():
    return get_token(USER_A)

@pytest.fixture
def token_b():
    return get_token(USER_B)

# ——————————————————————————
def test_create_thread(token_a):
    headers = {"Authorization": f"Bearer {token_a}"}
    res = client.post("/threads/", json={
        "title": "Dúvida sobre intercâmbio",
        "description": "Alguém já fez intercâmbio pelo ISMART?",
        "category": "geral",
        "tags": ["intercâmbio", "dicas"]
    }, headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["title"] == "Dúvida sobre intercâmbio"
    assert data["category"] == "geral"
    assert isinstance(data["id"], int)

def test_comment_on_thread(token_a, token_b):
    # Cria a thread com USER_A
    headers_a = {"Authorization": f"Bearer {token_a}"}
    thread_res = client.post("/threads/", json={
        "title": "Evento na Poli?",
        "description": "Vai ter evento sábado?",
        "category": "faculdade",
        "tags": []
    }, headers=headers_a)
    assert thread_res.status_code == 200, thread_res.text
    thread_id = thread_res.json()["id"]

    # USER_B comenta
    headers_b = {"Authorization": f"Bearer {token_b}"}
    comment_res = client.post(f"/threads/{thread_id}/comments", json={
        "content": "Sim! Confirmado 14h na FEA."
    }, headers=headers_b)
    assert comment_res.status_code == 200, comment_res.text
    comment = comment_res.json()
    assert comment["thread_id"] == thread_id
    assert "Confirmado" in comment["content"]

def test_vote_on_thread(token_a, token_b):
    # USER_A cria thread
    headers_a = {"Authorization": f"Bearer {token_a}"}
    thread_res = client.post("/threads/", json={
        "title": "Qual app vocês usam para organizar estudos?",
        "description": "Tô tentando melhorar minha rotina...",
        "category": "geral",
        "tags": ["estudos", "produtividade"]
    }, headers=headers_a)
    assert thread_res.status_code == 200, thread_res.text
    thread_id = thread_res.json()["id"]

    # USER_B vota +1
    headers_b = {"Authorization": f"Bearer {token_b}"}
    vote_res = client.post(f"/threads/{thread_id}/vote", json={"value": 1}, headers=headers_b)
    assert vote_res.status_code == 200, vote_res.text
    assert vote_res.json()["message"] == "Voto registrado com sucesso."

def test_report_thread(token_b):
    # USER_B cria uma thread ofensiva para denunciar
    headers_b = {"Authorization": f"Bearer {token_b}"}
    thread_res = client.post("/threads/", json={
        "title": "Conteúdo inadequado",
        "description": "Exemplo ofensivo",
        "category": "geral",
        "tags": []
    }, headers=headers_b)
    assert thread_res.status_code == 200, thread_res.text
    thread_id = thread_res.json()["id"]

    # USER_A (ou outro) denuncia. Aqui uso USER_A.
    headers_a = {"Authorization": f"Bearer {get_token(USER_A)}"}
    report_res = client.post(f"/threads/{thread_id}/report", headers=headers_a)
    assert report_res.status_code == 200, report_res.text
    assert report_res.json()["message"] == "Thread denunciada com sucesso."

def test_thread_pagination(token_a):
    headers_a = {"Authorization": f"Bearer {token_a}"}
    # Cria 25 threads
    for i in range(25):
        client.post("/threads/", json={
            "title": f"Thread #{i}",
            "description": "Lorem ipsum dolor sit amet.",
            "category": "geral",
            "tags": []
        }, headers=headers_a)

    res = client.get("/threads?skip=0&limit=20", headers=headers_a)
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data) == 20

    res2 = client.get("/threads?skip=20&limit=20", headers=headers_a)
    assert res2.status_code == 200, res2.text
    data2 = res2.json()
    assert len(data2) >= 5
