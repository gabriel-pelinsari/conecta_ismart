#!/usr/bin/env python3
"""Utility script to seed demo data in the Conecta Ismart API."""
import argparse
import os
from datetime import datetime, timedelta

import requests

DEFAULT_BASE_URL = "http://localhost:8000"
ADMIN_MASTER_PASSWORD = os.getenv("ADMIN_MASTER_PASSWORD", "123456")
DEFAULT_STUDENT_PASSWORD = os.getenv("STUDENT_PASSWORD", "Ismart@123")

USERS = [
    {
        "email": "admin@conecta.com",
        "password": ADMIN_MASTER_PASSWORD,
        "profile": {
            "full_name": "Admin Conecta",
            "nickname": "admin_conecta",
            "university": "Hub Ismart",
            "course": "Gestao de Comunidade",
            "semester": "Coordenacao",
            "bio": "Conta administrativa para moderar o ambiente.",
            "is_public": True,
        },
    },
    {
        "email": "julia.souza@universidade.com",
        "password": DEFAULT_STUDENT_PASSWORD,
        "profile": {
            "full_name": "Julia Souza",
            "nickname": "mentee_julia",
            "university": "USP",
            "course": "Engenharia de Producao",
            "semester": "5o semestre",
            "bio": "Explorando bolsas e oportunidades para estagios.",
            "is_public": True,
        },
    },
    {
        "email": "ana.carolina@universidade.com",
        "password": DEFAULT_STUDENT_PASSWORD,
        "profile": {
            "full_name": "Ana Carolina",
            "nickname": "ana_global",
            "university": "FGV",
            "course": "Relacoes Internacionais",
            "semester": "7o semestre",
            "bio": "Apaixonada por intercambio e experiencias globais.",
            "is_public": True,
        },
    },
    {
        "email": "pedro.henrique@universidade.com",
        "password": DEFAULT_STUDENT_PASSWORD,
        "profile": {
            "full_name": "Pedro Henrique",
            "nickname": "pedro_dev",
            "university": "UFPE",
            "course": "Ciencia da Computacao",
            "semester": "6o semestre",
            "bio": "Buscando networking para projetos de tecnologia.",
            "is_public": True,
        },
    },
    {
        "email": "clara.nogueira@universidade.com",
        "password": DEFAULT_STUDENT_PASSWORD,
        "profile": {
            "full_name": "Clara Nogueira",
            "nickname": "mentor_clara",
            "university": "PUC-Rio",
            "course": "Psicologia",
            "semester": "Mentora",
            "bio": "Mentora focada em desenvolvimento humano e carreira.",
            "is_public": True,
        },
    },
    {
        "email": "lucas.mendes@universidade.com",
        "password": DEFAULT_STUDENT_PASSWORD,
        "profile": {
            "full_name": "Lucas Mendes",
            "nickname": "coordenador_lucas",
            "university": "Insper",
            "course": "Administracao",
            "semester": "Coordenacao",
            "bio": "Coordena grupos de estudo e workshops tematicos.",
            "is_public": True,
        },
    },
]

THREADS = [
    {
        "author": "julia.souza@universidade.com",
        "title": "Duvida sobre bolsas em universidades particulares",
        "description": (
            "Alguem conseguiu conciliar bolsa parcial com estagio? "
            "Estou organizando a grade para o proximo semestre e preciso de dicas."
        ),
        "category": "geral",
        "tags": ["bolsas", "estagio"],
    },
    {
        "author": "ana.carolina@universidade.com",
        "title": "Processo seletivo internacional",
        "description": (
            "Para quem ja participou de intercambio, como foi o processo de validacao "
            "do historico escolar? Alguma dica sobre documentacoes?"
        ),
        "category": "faculdade",
        "tags": ["intercambio", "documentacao"],
    },
    {
        "author": "pedro.henrique@universidade.com",
        "title": "Como melhorar meu networking?",
        "description": (
            "Entrando no penultimo ano e procurando formas praticas de criar conexoes "
            "com profissionais de tecnologia. Ideias de eventos e abordagens?"
        ),
        "category": "geral",
        "tags": ["networking"],
    },
    {
        "author": "clara.nogueira@universidade.com",
        "title": "Grupo de acompanhamento emocional para bolsistas",
        "description": (
            "Estou estruturando encontros quinzenais para apoiar quem esta em processos "
            "seletivos intensos. Quem teria interesse?"
        ),
        "category": "geral",
        "tags": ["bem-estar", "grupos"],
    },
    {
        "author": "lucas.mendes@universidade.com",
        "title": "Calendario de workshops do semestre",
        "description": (
            "Compartilhando o rascunho de workshops de carreira e produtividade. "
            "Sugestoes sao bem-vindas!"
        ),
        "category": "geral",
        "tags": ["workshops", "planejamento"],
    },
]


def parsed_args():
    parser = argparse.ArgumentParser(description="Seed de dados para o Conecta Ismart.")
    parser.add_argument(
        "--base-url",
        default=os.getenv("API_BASE_URL", DEFAULT_BASE_URL),
        help="URL base da API FastAPI (default: %(default)s)",
    )
    return parser.parse_args()


def register_user(
    session: requests.Session,
    base_url: str,
    email: str,
    password: str,
    verification_code: str | None = None,
):
    payload = {"email": email, "password": password}
    if verification_code:
        payload["verification_code"] = verification_code
    resp = session.post(f"{base_url}/auth/register", json=payload, timeout=15)
    if resp.status_code == 200:
        print(f"[ok] Usuario criado: {email}")
        return
    if resp.status_code == 400 and "Email ja cadastrado" in resp.text:
        print(f"[skip] Usuario existente: {email}")
        return
    resp.raise_for_status()


def upload_pending_users(session: requests.Session, base_url: str, token: str, emails):
    if not emails:
        return {}
    csv_content = "email\n" + "\n".join(emails)
    files = {"file": ("students.csv", csv_content.encode("utf-8"), "text/csv")}
    headers = {"Authorization": f"Bearer {token}"}
    resp = session.post(
        f"{base_url}/auth/upload-csv",
        files=files,
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    created = data.get("created_users", [])
    codes = {item["email"]: item.get("verification_code") for item in created}
    for email in emails:
        if email not in codes:
            print(f"[warn] Sem codigo retornado para {email}.")
    return codes


def login(session: requests.Session, base_url: str, email: str, password: str) -> str:
    resp = session.post(
        f"{base_url}/auth/token",
        data={"email": email, "password": password},
        timeout=15,
    )
    resp.raise_for_status()
    token = resp.json().get("access_token")
    if not token:
        raise RuntimeError(f"Nao foi possivel obter token para {email}")
    return token


def update_profile(session: requests.Session, base_url: str, token: str, profile: dict):
    headers = {"Authorization": f"Bearer {token}"}
    resp = session.put(
        f"{base_url}/profiles/me",
        json=profile,
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()


def create_thread(session: requests.Session, base_url: str, token: str, payload: dict):
    headers = {"Authorization": f"Bearer {token}"}
    resp = session.post(
        f"{base_url}/api/threads/",
        json=payload,
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    print(f"[ok] Thread criada: {payload['title']}")


def create_event(session: requests.Session, base_url: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    start = datetime.utcnow() + timedelta(days=5)
    end = start + timedelta(hours=2)
    payload = {
        "title": "Encontro de mentores e mentorados",
        "description": "Roda de conversa para estruturar duplas e grupos de estudo.",
        "event_type": "meetup",
        "start_datetime": start.isoformat(),
        "end_datetime": end.isoformat(),
        "location": "Auditorio do Campus Central",
        "is_online": False,
        "university": None,
        "max_participants": 60,
    }
    resp = session.post(
        f"{base_url}/api/events/",
        json=payload,
        headers=headers,
        timeout=15,
    )
    if resp.status_code == 201:
        print("[ok] Evento criado.")
    elif resp.status_code == 400 and "Data de termino" in resp.text:
        print("[warn] Evento ja existe ou dados invalidos.")
    else:
        resp.raise_for_status()


def create_poll(session: requests.Session, base_url: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "title": "Qual trilha de workshops devemos priorizar?",
        "description": "Vote na trilha que voce mais gostaria de participar no proximo ciclo.",
        "audience": "geral",
        "options": [
            "Carreiras em tecnologia",
            "Preparacao para entrevistas",
            "Produtividade e organizacao",
        ],
    }
    resp = session.post(
        f"{base_url}/api/polls/",
        json=payload,
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    print("[ok] Enquete criada.")


def main():
    args = parsed_args()
    session = requests.Session()

    tokens: dict[str, str] = {}

    admin = USERS[0]
    register_user(session, args.base_url, admin["email"], admin["password"])
    admin_token = login(session, args.base_url, admin["email"], admin["password"])
    tokens[admin["email"]] = admin_token
    update_profile(session, args.base_url, admin_token, admin["profile"])

    students = USERS[1:]
    codes = upload_pending_users(
        session,
        args.base_url,
        admin_token,
        [user["email"] for user in students],
    )

    for user in students:
        code = codes.get(user["email"])
        if not code:
            print(f"[skip] Sem codigo para {user['email']} (pode ja existir).")
            continue
        register_user(
            session,
            args.base_url,
            user["email"],
            user["password"],
            verification_code=code,
        )
        token = login(session, args.base_url, user["email"], user["password"])
        tokens[user["email"]] = token
        update_profile(session, args.base_url, token, user["profile"])

    for thread in THREADS:
        author_token = tokens.get(thread["author"])
        if not author_token:
            print(f"[skip] Usuario sem token para thread: {thread['author']}")
            continue
        create_thread(session, args.base_url, author_token, thread)

    create_event(session, args.base_url, admin_token)
    create_poll(session, args.base_url, admin_token)

    print("\nSeed concluida com sucesso.")


if __name__ == "__main__":
    main()
