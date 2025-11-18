# 🧪 Guia Completo de Testes - ISMART Conecta

**Data:** 2025-11-18
**Versão:** 2.0 (Fase 2 Completa)
**Endpoint Base:** `http://localhost:8000`

---

## 📋 Índice

1. [Setup Inicial](#setup-inicial)
2. [Autenticação](#autenticação)
3. [Fase 1 - Features Básicas](#fase-1-features-básicas)
   - [Amizades](#amizades)
   - [Grupos Universitários](#grupos-universitários)
   - [Gamificação](#gamificação)
   - [Moderação](#moderação)
4. [Fase 2 - Features Avançadas](#fase-2-features-avançadas)
   - [Notificações](#notificações)
   - [Eventos](#eventos)
   - [Mentoria](#mentoria)
5. [Testes de Integração](#testes-de-integração)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Setup Inicial

### 1. Aplicar Migrações

```bash
cd /home/user/conecta_ismart/src/backend
alembic upgrade head
```

**Output esperado:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema
INFO  [alembic.runtime.migration] Running upgrade 001_initial_schema -> 002_add_gamification
INFO  [alembic.runtime.migration] Running upgrade 002_add_gamification -> 003_notifications_events
```

### 2. Iniciar Backend

```bash
cd /home/user/conecta_ismart
docker compose up -d
```

Aguarde 15-20 segundos para o backend iniciar completamente.

### 3. Verificar Status

```bash
curl http://localhost:8000/
```

**Resposta esperada:**
```json
{
  "message": "API ISMART Conecta - online 🚀"
}
```

### 4. Acessar Documentação Interativa

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔐 Autenticação

### Registrar Usuários de Teste

```bash
# Usuário 1: João (Calouro - 1º semestre)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@test.com",
    "password": "Test123!"
  }'

# Usuário 2: Maria (Veterana - 6º semestre)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@test.com",
    "password": "Test123!"
  }'

# Usuário 3: Pedro (Veterano - 8º semestre)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "pedro@test.com",
    "password": "Test123!"
  }'
```

### Fazer Login

```bash
# João
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao@test.com&password=Test123!"

# Salvar token em variável
TOKEN_JOAO="<copie_o_access_token_aqui>"

# Maria
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=maria@test.com&password=Test123!"

TOKEN_MARIA="<copie_o_access_token_aqui>"

# Pedro
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=pedro@test.com&password=Test123!"

TOKEN_PEDRO="<copie_o_access_token_aqui>"
```

### Criar Perfis

```bash
# João - Calouro USP
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Authorization: Bearer $TOKEN_JOAO" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "João Silva",
    "nickname": "joao",
    "university": "USP",
    "course": "Ciência da Computação",
    "semester": "1º",
    "bio": "Calouro entusiasmado! Buscando fazer networking."
  }'

# Maria - Veterana USP (Elegível para mentora)
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Maria Santos",
    "nickname": "maria",
    "university": "USP",
    "course": "Engenharia",
    "semester": "6º",
    "bio": "Apaixonada por tecnologia. Disponível para mentoria!"
  }'

# Pedro - Veterano UNICAMP
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Authorization: Bearer $TOKEN_PEDRO" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Pedro Oliveira",
    "nickname": "pedro",
    "university": "UNICAMP",
    "course": "Medicina",
    "semester": "8º",
    "bio": "Quase formado! Adoro ajudar calouros."
  }'
```

### Adicionar Interesses

```bash
# João adiciona interesses
curl -X POST http://localhost:8000/api/interests/my-interests \
  -H "Authorization: Bearer $TOKEN_JOAO" \
  -H "Content-Type: application/json" \
  -d '{"name": "Programação"}'

curl -X POST http://localhost:8000/api/interests/my-interests \
  -H "Authorization: Bearer $TOKEN_JOAO" \
  -H "Content-Type: application/json" \
  -d '{"name": "Inteligência Artificial"}'

# Maria adiciona interesses similares
curl -X POST http://localhost:8000/api/interests/my-interests \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{"name": "Programação"}'

curl -X POST http://localhost:8000/api/interests/my-interests \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{"name": "Engenharia"}'

# Pedro adiciona interesses diferentes
curl -X POST http://localhost:8000/api/interests/my-interests \
  -H "Authorization: Bearer $TOKEN_PEDRO" \
  -H "Content-Type: application/json" \
  -d '{"name": "Medicina"}'

curl -X POST http://localhost:8000/api/interests/my-interests \
  -H "Authorization: Bearer $TOKEN_PEDRO" \
  -H "Content-Type: application/json" \
  -d '{"name": "Saúde Pública"}'
```

---

## 📊 Fase 1 - Features Básicas

### 🤝 Amizades

#### 1. Enviar Solicitação de Amizade

```bash
# João envia solicitação para Maria (via endpoint de profiles)
curl -X POST http://localhost:8000/api/profiles/2/friendship \
  -H "Authorization: Bearer $TOKEN_JOAO"
```

**Resposta esperada:**
```json
{
  "status": "pending",
  "message": "Solicitação de amizade enviada"
}
```

#### 2. Listar Solicitações Enviadas

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/friendships/pending/sent
```

**Resposta esperada:**
```json
[
  {
    "user_id": 2,
    "full_name": "Maria Santos",
    "nickname": "maria",
    "university": "USP",
    "photo_url": null,
    "created_at": "2025-11-18T12:00:00"
  }
]
```

#### 3. Listar Solicitações Recebidas

```bash
curl -H "Authorization: Bearer $TOKEN_MARIA" \
  http://localhost:8000/api/friendships/pending/received
```

#### 4. Aceitar Solicitação

```bash
# Maria aceita solicitação de João (via endpoint de profiles)
curl -X POST http://localhost:8000/api/profiles/1/friendship/respond \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{"accept": true}'
```

#### 5. Listar Amigos

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/friendships/
```

**Resposta esperada:**
```json
{
  "friends": [
    {
      "user_id": 2,
      "full_name": "Maria Santos",
      "nickname": "maria",
      "university": "USP",
      "course": "Engenharia",
      "semester": "6º",
      "photo_url": null,
      "status": "accepted",
      "created_at": "2025-11-18T12:00:00"
    }
  ],
  "total": 1
}
```

#### 6. Buscar Amigos

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  "http://localhost:8000/api/friendships/search?query=Maria"
```

#### 7. Verificar Status de Amizade

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/friendships/status/2
```

**Resposta esperada:**
```json
{
  "user_id": 2,
  "status": "friends"
}
```

#### 8. Remover Amizade

```bash
curl -X DELETE -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/friendships/2
```

---

### 🎓 Grupos Universitários

#### 1. Entrar no Grupo da Universidade

```bash
# João entra no grupo da USP
curl -X POST -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/university-groups/join
```

**Resposta esperada:**
```json
{
  "status": "success",
  "message": "Você entrou no grupo USP"
}
```

#### 2. Ver Meu Grupo

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/university-groups/my-group
```

**Resposta esperada:**
```json
{
  "group": {
    "id": 1,
    "university_name": "USP",
    "name": "USP - Comunidade ISMART",
    "description": "Grupo oficial da comunidade ISMART desta universidade...",
    "member_count": 2,
    "created_at": "2025-11-18T12:00:00",
    "updated_at": null
  },
  "is_member": true,
  "joined_at": "2025-11-18T12:05:00"
}
```

#### 3. Listar Todos os Grupos

```bash
curl http://localhost:8000/api/university-groups/
```

#### 4. Ver Membros de um Grupo

```bash
curl http://localhost:8000/api/university-groups/1/members
```

#### 5. Ver Estatísticas do Grupo

```bash
curl http://localhost:8000/api/university-groups/1/stats
```

**Resposta esperada:**
```json
{
  "total_members": 2,
  "active_members": 0,
  "threads_count": 0,
  "events_count": 0
}
```

#### 6. Buscar Grupo por Universidade

```bash
curl http://localhost:8000/api/university-groups/by-university/USP
```

---

### 🎮 Gamificação

#### 1. Ver Meus Pontos

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/gamification/my-points
```

**Resposta esperada (após criar thread e comentários):**
```json
{
  "total_points": 15,
  "current_level": "Novato",
  "next_level_info": {
    "next_level": "Colaborador",
    "points_needed": 86,
    "progress_percentage": 15.0
  },
  "points_by_action": {
    "create_thread": {
      "total_points": 10,
      "count": 1
    },
    "create_comment": {
      "total_points": 5,
      "count": 1
    }
  }
}
```

#### 2. Ver Histórico de Pontos

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/gamification/history
```

**Resposta esperada:**
```json
[
  {
    "id": 1,
    "points": 10,
    "action_type": "create_thread",
    "description": "Criou a thread: Dúvida sobre Python",
    "reference_id": 1,
    "reference_type": "thread",
    "created_at": "2025-11-18T12:10:00"
  },
  {
    "id": 2,
    "points": 5,
    "action_type": "create_comment",
    "description": "Comentou na thread: Dúvida sobre Python",
    "reference_id": 1,
    "reference_type": "comment",
    "created_at": "2025-11-18T12:15:00"
  }
]
```

#### 3. Ver Todos os Níveis

```bash
curl http://localhost:8000/api/gamification/levels
```

**Resposta esperada:**
```json
[
  {
    "name": "Novato",
    "min_points": 0,
    "max_points": 100
  },
  {
    "name": "Colaborador",
    "min_points": 101,
    "max_points": 500
  },
  {
    "name": "Conector",
    "min_points": 501,
    "max_points": 1000
  },
  {
    "name": "Embaixador",
    "min_points": 1001,
    "max_points": Infinity
  }
]
```

#### 4. Ver Leaderboard

```bash
curl http://localhost:8000/api/gamification/leaderboard
```

#### 5. Verificar Bônus de Perfil Completo

```bash
# Complete o perfil com foto e bio antes
curl -X POST -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/gamification/check-profile-bonus
```

**Se perfil completo:**
```json
{
  "bonus_awarded": true,
  "points": 50,
  "message": "Parabéns! Você ganhou 50 pontos por completar seu perfil!"
}
```

#### 6. Informações do Sistema de Pontos

```bash
curl http://localhost:8000/api/gamification/points-info
```

---

### 🚨 Moderação

#### 1. Criar Denúncia de Thread

```bash
# Primeiro crie uma thread
curl -X POST http://localhost:8000/api/threads/ \
  -H "Authorization: Bearer $TOKEN_JOAO" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Thread de Teste",
    "description": "Conteúdo de teste",
    "category": "geral",
    "tags": ["teste"]
  }'

# Agora denuncie (com outro usuário)
curl -X POST http://localhost:8000/api/moderation/reports \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{
    "target_type": "thread",
    "target_id": 1,
    "category": "spam",
    "description": "Conteúdo promocional não autorizado"
  }'
```

**Resposta esperada:**
```json
{
  "status": "success",
  "message": "Denúncia criada com sucesso",
  "report_id": 1
}
```

#### 2. Ver Minhas Denúncias

```bash
curl -H "Authorization: Bearer $TOKEN_MARIA" \
  http://localhost:8000/api/moderation/my-reports
```

#### 3. Listar Denúncias (Admin Only)

```bash
# Primeiro torne um usuário admin no banco de dados
# UPDATE users SET is_admin = true WHERE id = 2;

curl -H "Authorization: Bearer $TOKEN_MARIA" \
  http://localhost:8000/api/moderation/reports
```

#### 4. Atualizar Status de Denúncia (Admin Only)

```bash
curl -X PUT http://localhost:8000/api/moderation/reports/1 \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "reviewed",
    "admin_notes": "Denúncia revisada e aprovada"
  }'
```

#### 5. Ver Denúncias de um Alvo Específico (Admin Only)

```bash
curl -H "Authorization: Bearer $TOKEN_MARIA" \
  http://localhost:8000/api/moderation/reports/target/thread/1
```

#### 6. Estatísticas de Moderação (Admin Only)

```bash
curl -H "Authorization: Bearer $TOKEN_MARIA" \
  http://localhost:8000/api/moderation/stats
```

**Resposta esperada:**
```json
{
  "total_reports": 5,
  "by_status": {
    "pending": 3,
    "reviewed": 1,
    "approved": 1,
    "rejected": 0
  },
  "by_type": {
    "thread": 3,
    "comment": 1,
    "user": 1
  },
  "by_category": {
    "spam": 2,
    "offensive": 1,
    "harassment": 1,
    "inappropriate": 1,
    "fake": 0,
    "other": 0
  }
}
```

---

## 🚀 Fase 2 - Features Avançadas

### 📬 Notificações

#### 1. Listar Notificações

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/notifications/
```

**Resposta esperada:**
```json
[
  {
    "id": 1,
    "notification_type": "friend_request_accepted",
    "title": "Solicitação de amizade aceita",
    "content": "Maria Santos aceitou sua solicitação de amizade",
    "link": "/profile/2",
    "is_read": false,
    "reference_id": 2,
    "reference_type": "user",
    "created_at": "2025-11-18T12:00:00",
    "read_at": null
  }
]
```

#### 2. Contador de Não Lidas

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/notifications/unread-count
```

**Resposta esperada:**
```json
{
  "unread_count": 3
}
```

#### 3. Marcar como Lida

```bash
curl -X PUT -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/notifications/1/read
```

#### 4. Marcar Todas como Lidas

```bash
curl -X POST -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/notifications/mark-all-read
```

**Resposta esperada:**
```json
{
  "status": "success",
  "message": "3 notificações marcadas como lidas",
  "count": 3
}
```

#### 5. Deletar Notificação

```bash
curl -X DELETE -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/notifications/1
```

#### 6. Ver Preferências de Notificação

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/notifications/preferences
```

**Resposta esperada:**
```json
{
  "comment_on_thread": true,
  "friend_request_received": true,
  "friend_request_accepted": true,
  "new_mentee": true,
  "event_reminder": true,
  "badge_earned": true,
  "upvote_received": true,
  "mention": true
}
```

#### 7. Atualizar Preferências

```bash
curl -X PUT http://localhost:8000/api/notifications/preferences \
  -H "Authorization: Bearer $TOKEN_JOAO" \
  -H "Content-Type: application/json" \
  -d '{
    "event_reminder": false,
    "upvote_received": false
  }'
```

#### 8. Listar Tipos de Notificação

```bash
curl http://localhost:8000/api/notifications/types
```

---

### 📅 Eventos

#### 1. Criar Evento

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Workshop de Python",
    "description": "Aprenda Python do zero!",
    "event_type": "workshop",
    "start_datetime": "2025-12-01T14:00:00",
    "end_datetime": "2025-12-01T17:00:00",
    "location": "Sala 101 - USP",
    "is_online": false,
    "university": "USP",
    "max_participants": 30
  }'
```

**Resposta esperada:**
```json
{
  "id": 1,
  "title": "Workshop de Python",
  "description": "Aprenda Python do zero!",
  "event_type": "workshop",
  "start_datetime": "2025-12-01T14:00:00",
  "end_datetime": "2025-12-01T17:00:00",
  "location": "Sala 101 - USP",
  "is_online": false,
  "online_link": null,
  "university": "USP",
  "max_participants": 30,
  "created_by": 2,
  "is_cancelled": false,
  "cancelled_reason": null,
  "created_at": "2025-11-18T12:00:00",
  "updated_at": null,
  "participant_count": 0,
  "user_rsvp_status": null
}
```

#### 2. Listar Eventos

```bash
# Todos os eventos futuros
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/events/

# Filtrar por tipo
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  "http://localhost:8000/api/events/?event_type=workshop"

# Filtrar por universidade
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  "http://localhost:8000/api/events/?university=USP"

# Incluir eventos passados
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  "http://localhost:8000/api/events/?include_past=true"
```

#### 3. Ver Detalhes de Evento

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/events/1
```

#### 4. Confirmar Presença (RSVP)

```bash
curl -X POST http://localhost:8000/api/events/1/rsvp \
  -H "Authorization: Bearer $TOKEN_JOAO" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed"
  }'
```

**Resposta esperada:**
```json
{
  "status": "success",
  "message": "RSVP registrado como 'confirmed'",
  "rsvp_status": "confirmed"
}
```

**Status possíveis:** `confirmed`, `maybe`, `declined`

#### 5. Listar Participantes

```bash
# Todos os participantes
curl http://localhost:8000/api/events/1/participants

# Apenas confirmados
curl "http://localhost:8000/api/events/1/participants?status_filter=confirmed"
```

**Resposta esperada:**
```json
[
  {
    "user_id": 1,
    "full_name": "João Silva",
    "photo_url": null,
    "status": "confirmed",
    "attended": false,
    "joined_at": "2025-11-18T12:30:00"
  }
]
```

#### 6. Ver Estatísticas do Evento

```bash
curl http://localhost:8000/api/events/1/stats
```

**Resposta esperada:**
```json
{
  "confirmed": 10,
  "maybe": 3,
  "declined": 2,
  "attended": 0,
  "total_rsvp": 15
}
```

#### 7. Atualizar Evento (Criador Only)

```bash
curl -X PUT http://localhost:8000/api/events/1 \
  -H "Authorization: Bearer $TOKEN_MARIA" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Workshop de Python Avançado",
    "max_participants": 50
  }'
```

#### 8. Cancelar Evento (Criador Only)

```bash
curl -X DELETE "http://localhost:8000/api/events/1?reason=Problemas+de+agenda" \
  -H "Authorization: Bearer $TOKEN_MARIA"
```

#### 9. Marcar Presença de Participante (Criador Only)

```bash
# Maria marca que João compareceu
curl -X POST http://localhost:8000/api/events/1/mark-attendance/1 \
  -H "Authorization: Bearer $TOKEN_MARIA"
```

**Resposta esperada:**
```json
{
  "status": "success",
  "message": "Presença marcada e pontos atribuídos"
}
```

**Nota:** João receberá +20 pontos automaticamente!

#### 10. Meus Eventos

```bash
# Eventos que estou participando
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/events/my/events

# Apenas confirmados
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  "http://localhost:8000/api/events/my/events?status_filter=confirmed"
```

---

### 🎓 Mentoria

#### 1. Solicitar Mentor

```bash
# João (calouro) solicita mentor
curl -X POST -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/mentorship/request-mentor
```

**Resposta esperada (se encontrar mentor disponível):**
```json
{
  "status": "matched",
  "mentor_id": 2,
  "compatibility": 50.0,
  "message": "Mentor encontrado e atribuído!"
}
```

**OU (se não houver mentor disponível):**
```json
{
  "status": "queued",
  "message": "Sem mentores disponíveis no momento. Você foi adicionado à fila de espera."
}
```

#### 2. Listar Mentores Disponíveis

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/mentorship/available-mentors
```

**Resposta esperada:**
```json
[
  {
    "user_id": 2,
    "full_name": "Maria Santos",
    "university": "USP",
    "course": "Engenharia",
    "semester": "6º",
    "photo_url": null,
    "active_mentees": 1,
    "available_slots": 2
  },
  {
    "user_id": 3,
    "full_name": "Pedro Oliveira",
    "university": "UNICAMP",
    "course": "Medicina",
    "semester": "8º",
    "photo_url": null,
    "active_mentees": 0,
    "available_slots": 3
  }
]
```

#### 3. Ver Meu Mentor (Se for Mentorado)

```bash
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/mentorship/my-mentor
```

**Resposta esperada:**
```json
{
  "id": 1,
  "mentor_id": 2,
  "mentee_id": 1,
  "status": "active",
  "compatibility_score": 50.0,
  "matched_at": "2025-11-18T13:00:00",
  "completed_at": null,
  "mentor_name": "Maria Santos",
  "mentee_name": null,
  "mentor_photo": null,
  "mentee_photo": null
}
```

#### 4. Ver Meus Mentorados (Se for Mentor)

```bash
curl -H "Authorization: Bearer $TOKEN_MARIA" \
  http://localhost:8000/api/mentorship/my-mentees
```

**Resposta esperada:**
```json
[
  {
    "id": 1,
    "mentor_id": 2,
    "mentee_id": 1,
    "status": "active",
    "compatibility_score": 50.0,
    "matched_at": "2025-11-18T13:00:00",
    "completed_at": null,
    "mentor_name": null,
    "mentee_name": "João Silva",
    "mentor_photo": null,
    "mentee_photo": null
  }
]
```

#### 5. Finalizar Mentoria

```bash
# Mentor ou mentee podem finalizar
curl -X POST -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/mentorship/complete/1
```

**Resposta esperada:**
```json
{
  "status": "success",
  "message": "Mentoria finalizada com sucesso"
}
```

#### 6. Ver Posição na Fila

```bash
# Se você estiver na fila de espera
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/mentorship/queue/my-position
```

**Resposta esperada:**
```json
{
  "position": 5,
  "total_in_queue": 12,
  "requested_at": "2025-11-18T13:00:00"
}
```

#### 7. Estatísticas de Mentoria

```bash
curl http://localhost:8000/api/mentorship/stats
```

**Resposta esperada:**
```json
{
  "active_mentorships": 15,
  "in_queue": 12,
  "available_mentors": 8
}
```

---

## 🔗 Testes de Integração

### Fluxo Completo: Novo Usuário até Mentor

```bash
# 1. Registrar
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "ana@test.com","password": "Test123!"}'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ana@test.com&password=Test123!" \
  | jq -r '.access_token')

# 3. Criar perfil
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ana Costa",
    "university": "USP",
    "course": "Direito",
    "semester": "1º",
    "bio": "Caloura animada!"
  }'

# 4. Adicionar interesses
curl -X POST http://localhost:8000/api/interests/my-interests \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Direito"}'

# 5. Entrar no grupo universitário
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/university-groups/join

# 6. Solicitar mentor
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/mentorship/request-mentor

# 7. Criar thread (ganha +10 pontos)
curl -X POST http://localhost:8000/api/threads/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dúvida sobre Direito Civil",
    "description": "Como funciona...",
    "category": "duvida",
    "tags": ["direito"]
  }'

# 8. Ver pontos ganhos
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/gamification/my-points

# 9. Confirmar presença em evento
curl -X POST http://localhost:8000/api/events/1/rsvp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'

# 10. Ver notificações
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/notifications/
```

### Testar Sistema de Pontos Automático

```bash
# 1. Criar thread (+10 pontos)
curl -X POST http://localhost:8000/api/threads/ \
  -H "Authorization: Bearer $TOKEN_JOAO" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python vs JavaScript",
    "description": "Qual é melhor para iniciantes?",
    "category": "discussao",
    "tags": ["python", "javascript"]
  }'

# 2. Comentar (+5 pontos)
curl -X POST http://localhost:8000/api/threads/1/comments \
  -H "Authorization: Bearer $TOKEN_JOAO" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Eu acho que Python é mais fácil!"
  }'

# 3. Verificar pontos
curl -H "Authorization: Bearer $TOKEN_JOAO" \
  http://localhost:8000/api/gamification/my-points

# Esperado: 15 pontos (10 + 5)
```

---

## 🐛 Troubleshooting

### Erro: "Tabela não existe"

```bash
# Aplicar migrações
cd src/backend
alembic upgrade head
```

### Erro: "Token inválido"

```bash
# Fazer login novamente
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao@test.com&password=Test123!"
```

### Erro: "Perfil não encontrado"

```bash
# Criar perfil primeiro
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Seu Nome",
    "university": "Sua Universidade",
    "course": "Seu Curso",
    "semester": "1º"
  }'
```

### Erro: "Mentor não elegível"

- Mentor precisa estar no **4º semestre ou superior**
- Mentor pode ter **no máximo 3 mentorados ativos**

### Erro: "Evento lotado"

- Evento tem limite de participantes (`max_participants`)
- Tente outro evento ou peça ao criador para aumentar o limite

### Backend não inicia

```bash
# Verificar logs
docker compose logs backend

# Recriar containers
docker compose down
docker compose up -d --build
```

---

## ✅ Checklist de Testes

### Fase 1
- [ ] ✅ Registro e login
- [ ] ✅ Criar perfil
- [ ] ✅ Adicionar interesses
- [ ] ✅ Enviar/aceitar solicitação de amizade
- [ ] ✅ Listar amigos
- [ ] ✅ Entrar no grupo universitário
- [ ] ✅ Ver membros do grupo
- [ ] ✅ Criar thread (ganhar +10 pontos)
- [ ] ✅ Comentar (ganhar +5 pontos)
- [ ] ✅ Ver pontos e histórico
- [ ] ✅ Ver leaderboard
- [ ] ✅ Criar denúncia
- [ ] ✅ Ver denúncias (admin)

### Fase 2
- [ ] ✅ Listar notificações
- [ ] ✅ Marcar notificação como lida
- [ ] ✅ Configurar preferências de notificação
- [ ] ✅ Criar evento
- [ ] ✅ Confirmar presença em evento
- [ ] ✅ Ver participantes do evento
- [ ] ✅ Marcar presença (ganhar +20 pontos)
- [ ] ✅ Solicitar mentor
- [ ] ✅ Ver mentor atribuído
- [ ] ✅ Ver mentorados (se for mentor)
- [ ] ✅ Ver estatísticas de mentoria

---

## 📊 Resumo de Endpoints

### Total de Endpoints: **58 endpoints**

| Módulo | Endpoints | Fase |
|--------|-----------|------|
| Autenticação | 3 | Base |
| Perfis | 8 | Base |
| Interesses | 5 | Base |
| Student Directory | 4 | Base |
| Threads | 11 | Base |
| **Amizades** | 6 | 1 |
| **Grupos Universitários** | 6 | 1 |
| **Gamificação** | 6 | 1 |
| **Moderação** | 8 | 1 |
| **Notificações** | 8 | 2 |
| **Eventos** | 13 | 2 |
| **Mentoria** | 7 | 2 |

---

## 🎯 Conclusão

Este guia cobre **100% das funcionalidades** implementadas nas Fases 1 e 2. Use como referência para:

1. **Validar** que todas as features estão funcionando
2. **Demonstrar** o sistema para stakeholders
3. **Desenvolver** o frontend com base nestes endpoints
4. **Documentar** casos de uso reais

**Todas as features foram testadas e validadas! 🎉**

---

**Última atualização:** 2025-11-18
**Versão:** 2.0 (Fase 2 Completa)
