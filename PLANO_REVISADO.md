# 📋 Plano de Desenvolvimento Revisado - ISMART Conecta

**Data:** 2025-11-18
**Branch:** `claude/revise-plan-update-016ES5EhSztfW8UuPTWUkaSX`
**Status Atual:** 40-45% Completo

---

## 🎯 Resumo Executivo

O projeto **ISMART Conecta** possui uma base sólida com:
- ✅ **100% dos endpoints core** funcionando (11/11 endpoints validados)
- ✅ **Autenticação JWT** completa
- ✅ **Student Directory** com algoritmo de sugestões (Jaccard similarity)
- ✅ **Sistema de Threads/Forum** funcional
- ✅ **15 tabelas no banco de dados** configuradas

### O que falta implementar:
- ❌ **Sistema de Eventos** (0%)
- ❌ **Sistema de Gamificação** (lógica de pontos e níveis - 20%)
- ❌ **Sistema de Mentoria** (0%)
- ❌ **Sistema de Notificações** (0%)
- ❌ **Moderação Avançada** (20%)
- 🟨 **Endpoints de Gestão de Amizades** (50% - lógica existe, faltam endpoints)
- 🟨 **Endpoints de Grupos Universitários** (50% - service completo, faltam rotas)

---

## 📊 Estado Atual por Módulo

### ✅ Completos (85%+)
| Módulo | % | Arquivos | Status |
|--------|---|----------|--------|
| **Autenticação** | 95% | `app/api/auth.py` | Produção |
| **Perfis** | 85% | `app/api/profiles.py` | Produção |
| **Interesses** | 100% | `app/api/interests.py` | Produção |
| **Student Directory** | 95% | `app/api/student_directory.py` | Produção |
| **Threads/Forum** | 75% | `app/api/threads.py` | Funcional |

### 🟨 Parciais (20-50%)
| Módulo | % | Arquivos | Falta |
|--------|---|----------|-------|
| **Amizades** | 50% | `services/social_graph.py` | Endpoints de UI |
| **Grupos Universitários** | 50% | `services/university_groups.py` | Rotas API |
| **Gamificação** | 20% | `models/gamification.py` | Lógica de pontos |
| **Moderação** | 20% | `api/threads.py` | Sistema completo |

### ❌ Não Iniciados (0%)
- Sistema de Eventos
- Sistema de Mentoria
- Sistema de Notificações
- Painel Admin

---

## 🚀 Fases de Implementação

## **FASE 1: Completar Funcionalidades Existentes** (1-2 semanas)

### 1.1 Endpoints de Gestão de Amizades
**Prioridade:** 🔴 ALTA
**Tempo Estimado:** 2-3 dias
**Arquivo:** `app/api/friendships.py` (NOVO)

#### Endpoints a Criar:
```python
GET    /api/friendships/              # Listar amigos
GET    /api/friendships/pending/sent  # Solicitações enviadas
GET    /api/friendships/pending/received # Solicitações recebidas
DELETE /api/friendships/{user_id}     # Remover amizade
GET    /api/friendships/search        # Buscar amigos
```

**Service já existe:** `services/social_graph.py` ✅

---

### 1.2 Endpoints de Grupos Universitários
**Prioridade:** 🔴 ALTA
**Tempo Estimado:** 2 dias
**Arquivo:** `app/api/university_groups.py` (NOVO)

#### Endpoints a Criar:
```python
GET /api/university-groups/           # Listar todos os grupos
GET /api/university-groups/{id}/members # Membros do grupo
GET /api/university-groups/my-group   # Grupo do usuário
GET /api/university-groups/stats      # Estatísticas do grupo
```

**Service já existe:** `services/university_groups.py` ✅

---

### 1.3 Sistema de Pontos e Níveis (Gamificação)
**Prioridade:** 🟡 MÉDIA
**Tempo Estimado:** 3-4 dias
**Arquivos:**
- `services/stats_badges.py` (atualizar)
- `models/gamification.py` (adicionar pontos)

#### Lógica de Pontos:
```python
# RF098-RF105: Pontuação
+10 pontos  → Criar thread
+5 pontos   → Comentar
+2 pontos   → Receber upvote
+15 pontos  → Thread marcada como útil
+20 pontos  → Participar de evento
+50 pontos  → Completar perfil 100%

# RF106-RF109: Níveis
0-100 pts    → Novato
101-500 pts  → Colaborador
501-1000 pts → Conector
1000+ pts    → Embaixador
```

#### Mudanças Necessárias:
1. **Adicionar campo `points` na tabela `user_stats`**
2. **Criar triggers/lógica para atribuir pontos**
3. **Endpoints:**
   ```python
   GET /api/gamification/points/history  # Histórico de pontos
   GET /api/gamification/level           # Nível atual e progresso
   GET /api/gamification/leaderboard     # Ranking
   ```

---

### 1.4 Sistema de Moderação Avançado
**Prioridade:** 🟡 MÉDIA
**Tempo Estimado:** 3 dias
**Arquivos:**
- `models/moderation.py` (NOVO)
- `api/moderation.py` (NOVO)

#### Endpoints a Criar:
```python
POST   /api/reports/thread/{id}        # Denunciar thread
POST   /api/reports/comment/{id}       # Denunciar comentário
POST   /api/reports/user/{id}          # Denunciar usuário
GET    /api/reports/                   # Listar denúncias (admin)
PUT    /api/reports/{id}/status        # Aprovar/rejeitar (admin)
```

#### Nova Tabela:
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    reporter_id INT NOT NULL,
    target_type VARCHAR(20),  -- 'thread', 'comment', 'user'
    target_id INT NOT NULL,
    category VARCHAR(50),     -- 'spam', 'offensive', 'harassment'
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP
);
```

---

## **FASE 2: Novos Sistemas Essenciais** (3-4 semanas)

### 2.1 Sistema de Notificações
**Prioridade:** 🔴 ALTA
**Tempo Estimado:** 1 semana
**Arquivos:**
- `models/notification.py` (NOVO)
- `api/notifications.py` (NOVO)
- `services/notification_service.py` (NOVO)

#### Tipos de Notificações (RF169-RF182):
```python
# Notificações para implementar
✓ Novo comentário em thread que você participa
✓ Solicitação de amizade recebida
✓ Solicitação de amizade aceita
✓ Novo mentee atribuído (se for mentor)
✓ Lembrete de evento (24h e 1h antes)
✓ Nova conquista de badge
✓ Recebeu upvote em comentário/thread
✓ Menção em comentário (@usuario)
```

#### Endpoints:
```python
GET    /api/notifications/           # Listar notificações
PUT    /api/notifications/{id}/read  # Marcar como lida
POST   /api/notifications/mark-all-read # Marcar todas como lidas
GET    /api/notifications/unread-count # Contador
PUT    /api/notifications/preferences # Configurar preferências
```

#### Nova Tabela:
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    content TEXT,
    link VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
```

---

### 2.2 Sistema de Eventos
**Prioridade:** 🔴 ALTA
**Tempo Estimado:** 1.5-2 semanas
**Arquivos:**
- `models/event.py` (NOVO)
- `api/events.py` (NOVO)
- `services/event_service.py` (NOVO)

#### Modelos Necessários:
```python
# models/event.py
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))  # 'workshop', 'meetup', 'study_group'
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    location = Column(String(300))
    university_id = Column(Integer, ForeignKey("university_groups.id"))
    max_participants = Column(Integer, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())

class EventParticipant(Base):
    __tablename__ = "event_participants"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    status = Column(String(20), default="confirmed")  # confirmed, maybe, declined
    attended = Column(Boolean, default=False)
    joined_at = Column(DateTime, server_default=func.now())
```

#### Endpoints (RF079-RF096):
```python
POST   /api/events/                  # Criar evento
GET    /api/events/                  # Listar eventos (com filtros)
GET    /api/events/{id}              # Detalhes do evento
PUT    /api/events/{id}              # Editar evento
DELETE /api/events/{id}              # Cancelar evento
POST   /api/events/{id}/rsvp         # Confirmar presença
GET    /api/events/{id}/participants # Listar participantes
GET    /api/events/calendar          # Visualização de calendário
GET    /api/events/my-events         # Meus eventos
```

#### Funcionalidades Especiais:
- **Lembretes automáticos:** 24h e 1h antes (via notificações)
- **Filtros avançados:** data, categoria, universidade, tipo
- **Limite de participantes:** validar antes de confirmar
- **+20 pontos** para quem participar e marcar presença

---

### 2.3 Sistema de Mentoria
**Prioridade:** 🟡 MÉDIA
**Tempo Estimado:** 1.5-2 semanas
**Arquivos:**
- `models/mentorship.py` (NOVO)
- `api/mentorship.py` (NOVO)
- `services/mentorship_service.py` (NOVO)

#### Modelos Necessários:
```python
class Mentorship(Base):
    __tablename__ = "mentorships"

    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("users.id"))
    mentee_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="active")  # active, completed, cancelled
    matched_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

class MentorshipQueue(Base):
    __tablename__ = "mentorship_queue"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    requested_at = Column(DateTime, server_default=func.now())
    priority_score = Column(Float, default=0.0)
```

#### Regras de Negócio (RF068-RF078):
```python
# Elegibilidade de mentor
- Estudante a partir do 4º semestre
- Máximo 3 mentorados por mentor
- Auto-matching baseado em similaridade de interesses (cosine similarity)

# Auto-matching
- Calcular compatibilidade entre mentor e calouro
- Priorizar mentorados sem mentor
- Queue para estudantes aguardando mentor
```

#### Endpoints:
```python
GET    /api/mentorship/available-mentors  # Mentores disponíveis
POST   /api/mentorship/request-mentor     # Solicitar mentor
GET    /api/mentorship/my-mentees         # Meus mentorados (se for mentor)
GET    /api/mentorship/my-mentor          # Meu mentor (se for mentorado)
POST   /api/mentorship/{id}/complete      # Finalizar mentoria
GET    /api/mentorship/queue              # Fila de espera
```

#### Funcionalidades Especiais:
- **Badge de mentor:** atribuir automaticamente
- **Liberar WhatsApp:** permitir contato direto entre mentor e mentorado
- **Algoritmo de matching:** similaridade de interesses (cosine similarity)

---

## **FASE 3: Painel Admin e Refinamentos** (2-3 semanas)

### 3.1 Painel Administrativo
**Prioridade:** 🟢 BAIXA
**Tempo Estimado:** 2 semanas
**Arquivos:**
- `api/admin.py` (NOVO)
- Frontend admin panel

#### Funcionalidades:
```python
# Gestão de Usuários
GET    /api/admin/users              # Listar usuários
PUT    /api/admin/users/{id}/ban     # Banir usuário
GET    /api/admin/users/stats        # Estatísticas

# Gestão de Conteúdo
GET    /api/admin/threads/reported   # Threads denunciadas
PUT    /api/admin/threads/{id}/pin   # Fixar thread
PUT    /api/admin/threads/{id}/lock  # Trancar thread
DELETE /api/admin/threads/{id}       # Deletar thread

# Gestão de Badges
POST   /api/admin/badges             # Criar badge
PUT    /api/admin/badges/{id}        # Editar badge
POST   /api/admin/badges/{id}/assign # Atribuir badge manualmente

# Analytics
GET    /api/admin/analytics/overview # Dashboard geral
GET    /api/admin/analytics/engagement # Métricas de engajamento
```

---

### 3.2 Melhorias de Segurança e Performance

#### Implementar:
1. **Rate Limiting** (usando slowapi)
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)

   @router.post("/auth/login")
   @limiter.limit("5/minute")
   async def login(...):
       ...
   ```

2. **Paginação Universal**
   ```python
   # Adicionar em todos os endpoints de listagem
   def paginate(skip: int = 0, limit: int = 20):
       return {"skip": skip, "limit": limit}
   ```

3. **Versionamento de API**
   ```python
   # Mudar de /api/... para /api/v1/...
   router = APIRouter(prefix="/api/v1")
   ```

4. **Logging Avançado**
   ```python
   # Adicionar logs estruturados
   import structlog
   logger = structlog.get_logger()
   ```

5. **Testes Automatizados**
   ```bash
   # Criar suite de testes
   mkdir tests/
   pytest tests/
   ```

---

## 📅 Cronograma Sugerido

### Semana 1-2: Fase 1
- [x] ~~Análise do estado atual~~ (COMPLETO)
- [ ] Endpoints de Amizades (2 dias)
- [ ] Endpoints de Grupos Universitários (2 dias)
- [ ] Sistema de Pontos/Níveis (3 dias)
- [ ] Sistema de Moderação (3 dias)

### Semana 3-4: Fase 2.1
- [ ] Sistema de Notificações (5 dias)
- [ ] Testes e ajustes (2 dias)

### Semana 5-7: Fase 2.2
- [ ] Sistema de Eventos - Modelos e API (5 dias)
- [ ] Sistema de Eventos - Lembretes (2 dias)
- [ ] Sistema de Eventos - Filtros e Calendário (3 dias)
- [ ] Testes e ajustes (2 dias)

### Semana 8-9: Fase 2.3
- [ ] Sistema de Mentoria - Modelos e API (4 dias)
- [ ] Sistema de Mentoria - Auto-matching (3 dias)
- [ ] Testes e ajustes (2 dias)

### Semana 10-12: Fase 3
- [ ] Painel Admin (10 dias)
- [ ] Melhorias de segurança (2 dias)
- [ ] Testes finais (3 dias)

---

## 🎯 Métricas de Sucesso

### Fase 1 (Completar Existentes)
- ✅ Todos os 4 novos módulos de API funcionando
- ✅ Sistema de pontos atribuindo automaticamente
- ✅ Moderação permitindo denúncias em 3 tipos de conteúdo

### Fase 2 (Novos Sistemas)
- ✅ Notificações sendo enviadas para 8 tipos de eventos
- ✅ Eventos podem ser criados e ter confirmações
- ✅ Mentoria fazendo matching automático

### Fase 3 (Admin e Polish)
- ✅ Admin pode gerenciar conteúdo e usuários
- ✅ API com rate limiting e versionamento
- ✅ 80%+ de cobertura de testes

---

## 🔧 Ferramentas e Tecnologias Atuais

### Backend
- **Framework:** FastAPI 0.104+
- **Banco de Dados:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.x
- **Autenticação:** JWT (python-jose)
- **Hash de Senhas:** PBKDF2
- **Migrações:** Alembic

### Frontend (não analisado em detalhes)
- React (detectado em /src/frontend)

### DevOps
- **Containerização:** Docker + Docker Compose
- **Scripts de Teste:** Bash (test_api.sh)

---

## 📝 Notas Técnicas

### Pontos Positivos
1. ✅ **Código limpo** - sem TODOs, bem organizado
2. ✅ **Separação de concerns** - models/services/routes
3. ✅ **Schemas Pydantic** - validação forte de dados
4. ✅ **JWT implementado corretamente**
5. ✅ **Relacionamentos de DB bem definidos**

### Pontos de Atenção
1. ⚠️ **Sem testes automatizados** - criar suite pytest
2. ⚠️ **Sem rate limiting** - vulnerável a abuse
3. ⚠️ **Sem paginação universal** - performance em listas grandes
4. ⚠️ **Sem API versioning** - dificulta mudanças futuras
5. ⚠️ **Error handling inconsistente** - padronizar respostas de erro

---

## 🚀 Próximos Passos Imediatos

### Para começar a Fase 1:

1. **Criar branch de trabalho**
   ```bash
   git checkout -b feature/friendships-api
   ```

2. **Criar arquivo de rotas de amizades**
   ```bash
   touch src/backend/app/api/friendships.py
   ```

3. **Implementar endpoints usando service existente**
   - Reutilizar `services/social_graph.py`
   - Adicionar schemas Pydantic
   - Registrar router em `main.py`

4. **Testar endpoints**
   ```bash
   # Adicionar testes ao test_api.sh
   curl -X GET http://localhost:8000/api/friendships/
   ```

5. **Commit e PR**
   ```bash
   git add .
   git commit -m "feat: add friendship management endpoints"
   git push origin feature/friendships-api
   ```

---

## 📚 Documentação de Referência

- **ENDPOINT_STATUS.md** - Status dos 11 endpoints atuais
- **API_TEST_GUIDE.md** - Exemplos de uso da API
- **SETUP_AND_TESTING.md** - Guia de setup completo
- **FIXES_APPLIED.md** - Histórico de correções

---

## ✨ Conclusão

O projeto **ISMART Conecta** tem uma **base sólida de 40-45% completa**. As próximas 12 semanas de desenvolvimento vão adicionar:

- ✅ **Gestão completa de amizades** (Fase 1)
- ✅ **Sistema de pontos e níveis** (Fase 1)
- ✅ **Sistema de notificações** (Fase 2)
- ✅ **Sistema de eventos** (Fase 2)
- ✅ **Sistema de mentoria** (Fase 2)
- ✅ **Painel administrativo** (Fase 3)

Ao final, teremos uma **rede social educacional completa** com todas as funcionalidades planejadas nos requisitos funcionais.

---

**Pronto para começar? 🚀**

Aguardo aprovação para iniciar a **Fase 1** com os endpoints de amizades e grupos universitários!
