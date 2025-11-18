# 🧪 ISMART Conecta - API Test Guide

Script de testes completo para testar todos os endpoints implementados usando `curl`.

## 📋 Conteúdo

- [Como Usar](#como-usar)
- [Estrutura do Script](#estrutura-do-script)
- [Endpoints Testados](#endpoints-testados)
- [Resolução de Problemas](#resolução-de-problemas)

---

## 🚀 Como Usar

### Pré-requisitos

1. **Backend rodando:**
```bash
cd /home/omatheu/Desktop/projects/conecta_ismart
docker compose up -d
```

2. **Aguarde o backend ficar pronto** (cerca de 20 segundos)

### Executar o Script

```bash
# From the root directory
bash test_api.sh
```

### Output Esperado

O script vai:
1. ✅ Verificar se a API está disponível
2. ✅ Registrar 3 usuários de teste
3. ✅ Fazer login com cada usuário
4. ✅ Criar perfis para cada usuário
5. ✅ Adicionar interesses
6. ✅ Testar student directory (explorar, filtrar, sugestões)
7. ✅ Testar threads (criar, comentar)

---

## 📁 Estrutura do Script

### Seções Principais

```
test_health()              → Verifica se API está online
test_auth()                → Testa registro e login
test_profiles()            → Testa criação de perfis
test_interests()           → Testa criação de interesses
test_student_directory()   → Testa exploração de alunos
test_threads()             → Testa discussões
```

### Dados de Teste

O script cria automaticamente:

**Usuários:**
- usuario1@example.com (ID: 3)
- usuario2@example.com (ID: 4)
- usuario3@example.com (ID: 5)

**Profiles:**
- João Silva (USP - Engenharia de Software)
- Maria Santos (UNICAMP - Ciência da Computação)
- Pedro Costa (USP - Engenharia de Software)

**Interesses:**
- Usuário 1: Python, JavaScript, Machine Learning
- Usuário 2: Machine Learning, AI, Deep Learning
- Usuário 3: React, JavaScript, Web Development

---

## 🔌 Endpoints Testados

### 1. Autenticação (`/auth`)

#### POST `/auth/register`
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "SenhaForte123"
  }'
```

**Response:**
```json
{
  "email": "usuario@example.com",
  "id": 1,
  "is_active": true,
  "is_verified": true
}
```

#### POST `/auth/token`
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "email=usuario@example.com&password=SenhaForte123"
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

### 2. Perfis (`/api/profiles`)

#### POST `/api/profiles/`
```bash
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "full_name": "João Silva",
    "university": "USP",
    "course": "Engenharia de Software",
    "semester": "6",
    "bio": "Desenvolvedor apaixonado",
    "is_public": true
  }'
```

---

### 3. Interesses (`/api/interests`)

#### POST `/api/interests/my-interests`
```bash
curl -X POST http://localhost:8000/api/interests/my-interests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "interest_names": ["Python", "JavaScript", "Machine Learning"]
  }'
```

---

### 4. Student Directory (`/api/students`)

#### GET `/api/students/explore`
```bash
# Listar todos
curl -X GET "http://localhost:8000/api/students/explore?limit=10" \
  -H "Authorization: Bearer {TOKEN}"

# Com filtro de universidade
curl -X GET "http://localhost:8000/api/students/explore?universities=USP&limit=10" \
  -H "Authorization: Bearer {TOKEN}"

# Com filtro de curso
curl -X GET "http://localhost:8000/api/students/explore?courses=Engenharia%20de%20Software" \
  -H "Authorization: Bearer {TOKEN}"

# Com filtro de interesses
curl -X GET "http://localhost:8000/api/students/explore?interests=Python&limit=10" \
  -H "Authorization: Bearer {TOKEN}"

# Com busca por nome
curl -X GET "http://localhost:8000/api/students/explore?search_name=Maria" \
  -H "Authorization: Bearer {TOKEN}"

# Com filtros combinados
curl -X GET "http://localhost:8000/api/students/explore?universities=USP&interests=Python" \
  -H "Authorization: Bearer {TOKEN}"
```

#### GET `/api/students/explore/facets`
```bash
# Retorna contadores de filtros disponíveis
curl -X GET "http://localhost:8000/api/students/explore/facets" \
  -H "Authorization: Bearer {TOKEN}"
```

**Response:**
```json
{
  "universities": [
    {"value": "USP", "count": 2},
    {"value": "UNICAMP", "count": 1}
  ],
  "courses": [
    {"value": "Engenharia de Software", "count": 2},
    {"value": "Ciência da Computação", "count": 1}
  ],
  "interests": [
    {"value": "Python", "count": 2},
    {"value": "JavaScript", "count": 2}
  ],
  "entry_years": []
}
```

#### GET `/api/students/suggestions`
```bash
# Retorna sugestões personalizadas (requer 3+ interesses)
curl -X GET "http://localhost:8000/api/students/suggestions?limit=5" \
  -H "Authorization: Bearer {TOKEN}"
```

#### GET `/api/students/university/{university_name}`
```bash
curl -X GET "http://localhost:8000/api/students/university/USP?limit=10" \
  -H "Authorization: Bearer {TOKEN}"

# Com filtro de curso
curl -X GET "http://localhost:8000/api/students/university/USP?course_filter=Engenharia%20de%20Software" \
  -H "Authorization: Bearer {TOKEN}"

# Com filtro de interesses
curl -X GET "http://localhost:8000/api/students/university/USP?interests=Python&interests=JavaScript" \
  -H "Authorization: Bearer {TOKEN}"
```

---

### 5. Threads (`/api/threads`)

#### POST `/api/threads/`
```bash
curl -X POST http://localhost:8000/api/threads/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "title": "Qual linguagem estudar?",
    "content": "Estou começando. Qual linguagem vocês recomendam?"
  }'
```

#### GET `/api/threads/`
```bash
curl -X GET http://localhost:8000/api/threads/ \
  -H "Authorization: Bearer {TOKEN}"
```

#### POST `/api/threads/{thread_id}/comments`
```bash
curl -X POST http://localhost:8000/api/threads/1/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "content": "Recomendo Python!"
  }'
```

---

## 📊 Exemplo de Fluxo Completo

```bash
# 1. Registrar usuário
REGISTER=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@example.com","password":"Senha123"}')

USER_ID=$(echo $REGISTER | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# 2. Fazer login
LOGIN=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "email=teste@example.com&password=Senha123")

TOKEN=$(echo $LOGIN | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Criar perfil
curl -s -X POST http://localhost:8000/api/profiles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"full_name":"João","university":"USP","course":"Eng. Software","is_public":true}'

# 4. Adicionar interesses
curl -s -X POST http://localhost:8000/api/interests/my-interests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"interest_names":["Python","JavaScript"]}'

# 5. Explorar alunos
curl -s -X GET "http://localhost:8000/api/students/explore?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## 🔧 Resolução de Problemas

### Erro: "API não está disponível"

**Solução:**
```bash
docker compose up -d
sleep 20
bash test_api.sh
```

### Erro: "Credenciais inválidas"

**Causa:** Token expirou (válido por 30 minutos)

**Solução:** Re-fazer login para obter novo token

### Erro: "Not Found" em rotas de profiles/threads

**Causa:** Estas rotas podem não estar completamente implementadas

**Solução:** Use as rotas funcionais listadas neste guia

### Erro: "UUID input should be a string"

**Causa:** Incompatibilidade entre tipos de dados (int vs UUID)

**Solução:** Aguarde correção no código ou use apenas os endpoints testados

---

## 🧹 Limpeza e Reset

### Limpar dados (mantém estrutura)
```bash
bash reset_db.sh
# Escolha opção 1
```

### Reset completo (recreia banco)
```bash
bash reset_db.sh
# Escolha opção 2
```

### Reset total (deleta volume Docker)
```bash
bash reset_db.sh
# Escolha opção 3
```

---

## 📈 Estatísticas do Script

- **Usuários criados:** 3
- **Perfis criados:** 3
- **Interesses adicionados:** 9 (3 por usuário)
- **Requisições curl:** ~30+
- **Tempo de execução:** ~5-10 segundos
- **Taxa de sucesso:** 70-80%

---

## 📝 Notas

- ✅ Endpoints de autenticação e student directory são os mais testados
- ⚠️ Alguns endpoints de threads e perfis podem não estar 100% implementados
- ✅ Todos os dados são persistidos no PostgreSQL
- ✅ Script é idempotente (pode ser rodado múltiplas vezes)

---

## 🔗 Referências

- **API Base URL:** http://localhost:8000
- **Database:** localhost:5432 (postgres/postgres)
- **Backend logs:** `docker compose logs backend -f`
- **Database logs:** `docker compose logs db -f`

---

**Criado em:** 2025-11-18
**Última atualização:** 2025-11-18
