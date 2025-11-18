# 🚀 ISMART Conecta - Setup and Testing Guide

Guia completo para setup do backend com banco de dados local e testes de API.

## 📑 Índice

1. [Setup Rápido](#setup-rápido)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Testes da API](#testes-da-api)
4. [Conexão DBeaver](#conexão-dbeaver)
5. [Troubleshooting](#troubleshooting)

---

## ⚡ Setup Rápido

### 1. Iniciar Backend e Banco

```bash
cd /home/omatheu/Desktop/projects/conecta_ismart
docker compose up -d
```

Aguarde 15-20 segundos até o banco ficar pronto.

### 2. Verificar Status

```bash
docker compose ps
```

Você deve ver:
- ✅ `conecta-db` (postgres:16-alpine) - Healthy
- ✅ `conecta-backend` (FastAPI) - Running

### 3. Testar API

```bash
# Opção 1: Script automático
bash test_api.sh

# Opção 2: Teste manual
curl http://localhost:8000/
```

---

## 📊 Estrutura do Projeto

```
conecta_ismart/
├── docker-compose.yml          # Configuração Docker
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── models/         # Modelos SQLAlchemy
│   │   │   │   ├── user.py     # Users, UserStats
│   │   │   │   ├── profile.py  # Profiles
│   │   │   │   ├── social.py   # Friendships, Interests
│   │   │   │   ├── thread.py   # Threads, Comments
│   │   │   │   └── gamification.py # Badges
│   │   │   ├── api/            # Rotas FastAPI
│   │   │   │   ├── auth.py     # Autenticação
│   │   │   │   ├── profiles.py # Perfis
│   │   │   │   ├── interests.py # Interesses
│   │   │   │   ├── threads.py  # Discussões
│   │   │   │   └── student_directory.py # Student Directory
│   │   │   ├── schemas/        # Schemas Pydantic
│   │   │   ├── services/       # Lógica de negócio
│   │   │   ├── core/           # Configurações (security, config)
│   │   │   └── db/             # Banco de dados
│   │   ├── alembic/
│   │   │   └── versions/
│   │   │       └── 001_initial_schema.py # Migrations
│   │   ├── .env                # Variáveis de ambiente
│   │   └── main.py             # Aplicação FastAPI
│   └── frontend/               # Frontend React (separado)
├── test_api.sh                 # Script de testes
├── reset_db.sh                 # Script de reset
├── API_TEST_GUIDE.md           # Guia detalhado de testes
└── SETUP_AND_TESTING.md        # Este arquivo
```

---

## 🧪 Testes da API

### Script Automático (Recomendado)

```bash
bash test_api.sh
```

Isto vai:
1. ✅ Criar 3 usuários de teste
2. ✅ Fazer login com cada um
3. ✅ Criar perfis com dados variados
4. ✅ Adicionar interesses
5. ✅ Testar exploração de alunos
6. ✅ Testar filtros e sugestões

**Saída esperada:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                  ISMART CONECTA - API TEST SCRIPT                          ║
║                                                                            ║
║  Testando todos os endpoints implementados                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

✓ API está disponível

========================================
1. TESTANDO AUTENTICAÇÃO
========================================

✓ Usuário 1 registrado com ID: 3
✓ Usuário 2 registrado com ID: 4
✓ Usuário 3 registrado com ID: 5
✓ Login bem-sucedido - Token recebido
...
```

### Testes Manuais com Curl

Veja [API_TEST_GUIDE.md](API_TEST_GUIDE.md) para exemplos completos.

**Teste rápido:**
```bash
# 1. Registrar
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@example.com","password":"Senha123"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "email=teste@example.com&password=Senha123" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Explorar alunos
curl -X GET "http://localhost:8000/api/students/explore?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 Endpoints Implementados

### Autenticação ✅

```
POST   /auth/register              Registrar usuário
POST   /auth/token                 Login (retorna JWT)
```

### Perfis ⚠️

```
POST   /api/profiles/              Criar/atualizar perfil
GET    /api/profiles/me            Buscar perfil do usuário
```

### Interesses ⚠️

```
GET    /api/interests/             Listar interesses
POST   /api/interests/             Criar interesse
POST   /api/interests/my-interests Adicionar interesses ao usuário
```

### Student Directory ✅✅

```
GET    /api/students/explore           Listar alunos com filtros
GET    /api/students/explore/facets    Contadores de filtros
GET    /api/students/suggestions       Sugestões personalizadas
GET    /api/students/university/{name} Alunos por universidade
```

### Threads ⚠️

```
POST   /api/threads/                Criar thread
GET    /api/threads/                Listar threads
POST   /api/threads/{id}/comments   Adicionar comentário
```

**Legenda:** ✅ = Funcionando bem | ⚠️ = Parcialmente implementado | ❌ = Não implementado

---

## 💾 Banco de Dados

### Conexão Local

```
Host:     localhost
Port:     5432
Database: ismart_db
User:     postgres
Password: postgres
```

### Tabelas

```
users                      → Usuários
├── profiles               → Perfis
├── user_stats             → Estatísticas
├── friendships            → Amizades
├── user_interests         → Interesses (M:N)
├── user_badges            → Badges
├── threads                → Discussões
│   ├── comments           → Comentários
│   ├── thread_votes       → Votos em threads
│   └── comment_votes      → Votos em comentários
├── university_groups      → Grupos por universidade
└── university_group_members → Membros de grupos
```

### Estatísticas

- **Total de tabelas:** 15
- **Total de relações:** 25+
- **Restrições de integridade:** CASCADE delete habilitado
- **Indices:** Criados em colunas críticas

---

## 🔐 Autenticação

### Fluxo

1. **Registrar** → POST `/auth/register` → Retorna User
2. **Login** → POST `/auth/token` → Retorna JWT Token
3. **Usar Token** → Header `Authorization: Bearer {TOKEN}` em requisições

### Token JWT

```json
{
  "sub": "usuario@example.com",
  "user_id": 1,
  "is_admin": false,
  "exp": 1763434009
}
```

**Validade:** 30 minutos (configurável em `.env`)

---

## 🖥️ Conexão DBeaver

### Passos

1. **DBeaver** → `Database` → `New Database Connection`
2. Selecione **PostgreSQL** → `Next`
3. Preencha:
   - Host: `localhost`
   - Port: `5432`
   - Database: `ismart_db`
   - Username: `postgres`
   - Password: `postgres`
4. Clique `Test Connection...`
5. Clique `Finish`

### Verificar Dados

```bash
psql -h localhost -U postgres -d ismart_db -c "\dt"
```

---

## 🧹 Limpeza e Reset

### Opção 1: Limpar dados (mantém estrutura)

```bash
bash reset_db.sh
# Escolha opção 1
```

Deleta todos os dados mas mantém as tabelas.

### Opção 2: Reset de banco (recreia estrutura)

```bash
bash reset_db.sh
# Escolha opção 2
```

Deleta banco e recreia do zero com migrations.

### Opção 3: Reset total (deleta volume Docker)

```bash
bash reset_db.sh
# Escolha opção 3
```

Deleta tudo: containers, volumes, dados.

---

## 🐛 Troubleshooting

### Problema: "API não está disponível"

**Solução:**
```bash
# Reinicie tudo
docker compose down
docker compose up -d
sleep 20
bash test_api.sh
```

### Problema: "Credenciais inválidas"

**Causa:** Token expirou ou não foi criado corretamente

**Solução:**
```bash
# Faça login novamente
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "email=usuario@example.com&password=SenhaForte123"
```

### Problema: Port 5432 já em uso

**Solução:**
```bash
# Encontre o processo
lsof -i :5432

# Mate o processo
kill -9 <PID>

# Ou mude a porta em docker-compose.yml
```

### Problema: Migrations falhando

**Solução:**
```bash
docker compose down -v
docker compose up -d
sleep 20
# Migrations rodam automaticamente
```

### Problema: Backend não inicia

**Verificar logs:**
```bash
docker compose logs backend -f
```

**Causas comuns:**
- Porta 8000 ocupada
- Variáveis de ambiente não carregadas
- Banco não está pronto

---

## 📈 Próximos Passos

### Melhorias Sugeridas

- [ ] Implementar rotas de threads completamente
- [ ] Adicionar validações mais robustas
- [ ] Criar índices de performance
- [ ] Adicionar cache Redis
- [ ] Implementar rate limiting
- [ ] Adicionar testes unitários

### Integração Frontend

```bash
cd src/frontend
npm install
npm start  # Roda em http://localhost:3000
```

### Deploy

```bash
# Build production
docker compose -f docker-compose.prod.yml up -d

# Configurar variáveis de produção em .env.prod
```

---

## 📚 Documentação Adicional

- [API_TEST_GUIDE.md](API_TEST_GUIDE.md) - Guia detalhado de todos os endpoints
- [README_STUDENT_DIRECTORY.md](src/backend/README_STUDENT_DIRECTORY.md) - Documentação do Student Directory
- [FastAPI Docs](http://localhost:8000/docs) - Documentação automática (Swagger UI)
- [ReDoc Docs](http://localhost:8000/redoc) - Documentação alternativa

---

## 🤝 Contribuindo

Para contribuir com melhorias:

1. Crie uma branch: `git checkout -b feature/sua-feature`
2. Commit: `git commit -m "feat: sua feature"`
3. Push: `git push origin feature/sua-feature`
4. Abra um Pull Request

---

## 📝 Changelog

### v1.0 (2025-11-18)
- ✅ Setup inicial com Docker Compose
- ✅ Schema de banco de dados com 15 tabelas
- ✅ Autenticação com JWT
- ✅ Student Directory com filtros avançados
- ✅ Script de testes automático
- ✅ Documentação completa

---

**Criado em:** 2025-11-18
**Última atualização:** 2025-11-18
**Status:** ✅ Funcional
