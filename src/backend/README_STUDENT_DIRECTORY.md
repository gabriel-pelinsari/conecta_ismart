# 🎓 Diretório de Alunos - Módulo 4: Descoberta e Agrupamento

## 📋 Visão Geral

Implementação completa do sistema de descoberta e agrupamento de alunos da plataforma ISMART Conecta, incluindo:

- ✅ **RF047**: Página "Explorar" com lista de alunos
- ✅ **RF048**: Filtro por universidade
- ✅ **RF049**: Filtro por curso
- ✅ **RF050**: Filtro por interesses comuns
- ✅ **RF051**: Sugestões de conexão baseadas em vetorização
- ✅ **RF052**: Grupos automáticos por universidade
- ✅ **RF053**: Página dedicada por universidade
- ✅ **RF054**: Busca de alunos por nome
- ✅ **RF055**: Filtros combinados

## 🚀 Quick Start

### 1. Configurar Banco de Dados

Atualize o `.env` com as credenciais do Supabase:

```bash
POSTGRES_USER=postgres.wlroivffcmaktuzcaygv
POSTGRES_PASSWORD=sua-senha-aqui
POSTGRES_DB=postgres
POSTGRES_HOST=aws-1-us-east-2.pooler.supabase.com
POSTGRES_PORT=5432
```

### 2. Executar Migrations no Supabase

Abra o Supabase SQL Editor e execute:

```bash
cat migrations_supabase.sql
```

Cole todo o conteúdo no SQL Editor e execute.

### 3. Verificar Schema

```bash
python check_db_schema.py
```

### 4. Iniciar Backend

```bash
# Se estiver usando Docker
docker-compose up backend

# Ou diretamente
uvicorn app.main:app --reload
```

### 5. Testar Endpoints

Acesse a documentação interativa:
```
http://localhost:8000/docs
```

Ou use os exemplos de curl:
```bash
# Ver documentação completa
cat STUDENT_DIRECTORY_API.md
```

## 📂 Estrutura de Arquivos

### Arquivos Criados

```
src/backend/
├── app/
│   ├── api/
│   │   └── student_directory.py      # 9 endpoints novos
│   ├── models/
│   │   └── social.py                 # Atualizado (Friendship, UniversityGroup)
│   ├── schemas/
│   │   └── student_directory.py      # 12 schemas novos
│   └── services/
│       ├── student_directory.py      # Lógica de negócio
│       └── university_groups.py      # Gerenciamento de grupos
├── migrations_supabase.sql           # Migrations SQL para Supabase
├── check_db_schema.py               # Script de verificação
├── STUDENT_DIRECTORY_API.md         # Documentação completa da API
├── IMPLEMENTATION_SUMMARY.md         # Resumo da implementação
└── README_STUDENT_DIRECTORY.md      # Este arquivo
```

### Arquivos Modificados

```
src/backend/
├── app/
│   ├── main.py                      # + router student_directory
│   └── api/
│       └── profiles.py              # + hook para grupos automáticos
└── .env.example                     # + variáveis Supabase
```

## 🔗 Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/students/explore` | Lista alunos com filtros |
| GET | `/api/students/explore/facets` | Contadores de filtros |
| GET | `/api/students/suggestions` | Sugestões de conexão |
| GET | `/api/students/universities/{slug}` | Página de universidade |
| GET | `/api/students/my-university` | Minha universidade |
| GET | `/api/students/groups/my-university` | Meu grupo |
| GET | `/api/students/groups` | Todos os grupos |
| POST | `/api/students/groups/sync-all` | Sincronizar grupos (admin) |

## 🧪 Testes Rápidos

### Teste 1: Explorar Alunos

```bash
# Login e obter token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=seu-email@example.com&password=sua-senha" \
  | jq -r '.access_token')

# Explorar alunos
curl -X GET "http://localhost:8000/api/students/explore?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### Teste 2: Filtrar por Universidade

```bash
curl -X GET "http://localhost:8000/api/students/explore?universities=USP" \
  -H "Authorization: Bearer $TOKEN" | jq '.total'
```

### Teste 3: Sugestões de Conexão

```bash
curl -X GET "http://localhost:8000/api/students/suggestions?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.suggestions[0]'
```

### Teste 4: Meu Grupo de Universidade

```bash
curl -X GET "http://localhost:8000/api/students/groups/my-university" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### Teste 5: Sincronizar Grupos (Admin)

```bash
curl -X POST "http://localhost:8000/api/students/groups/sync-all" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
```

## 📊 Tabelas do Banco de Dados

### Novas Tabelas

```sql
-- RF052 - Grupos automáticos
university_groups
  - id (PK)
  - university_name (UNIQUE)
  - name
  - description
  - created_at
  - updated_at

university_group_members
  - group_id (FK -> university_groups)
  - user_id (FK -> users)
  - joined_at
  - PRIMARY KEY (group_id, user_id)
```

### Tabelas Atualizadas

```sql
-- RF047, RF051 - Status de amizade
friendships
  + status VARCHAR(20)          -- 'pending', 'accepted', 'rejected'
  + created_at TIMESTAMP
```

### Índices Criados

- `idx_friendships_status`
- `idx_friendships_user_status`
- `idx_friendships_friend_status`
- `idx_profiles_university`
- `idx_profiles_course`
- `idx_profiles_semester`
- `idx_profiles_full_name_lower`
- `idx_profiles_university_course`
- E mais...

## 🔍 Recursos Principais

### 1. Sistema de Filtros Avançado

Combine múltiplos filtros simultaneamente:
- Universidade (múltipla seleção)
- Curso (múltipla seleção)
- Interesses/Tags (múltipla seleção)
- Semestre
- Busca por nome (case-insensitive)
- Ordenação (random, name, compatibility, recent)

### 2. Algoritmo de Sugestões

- **Algoritmo**: Jaccard Similarity
- **Input**: Interesses/tags do usuário
- **Output**: Lista ordenada por compatibilidade (0-100%)
- **Requer**: Mínimo 3 tags no perfil
- **Exclui**: Amigos atuais e solicitações pendentes

### 3. Grupos Automáticos

- **1 grupo por universidade**
- **Criação automática** ao cadastrar primeira pessoa
- **Adição automática** ao atualizar perfil
- **Gerenciamento de mudança** de universidade
- **Hook integrado** em `PUT /profiles/me`

### 4. Performance

- **Paginação**: Offset/limit padrão 20
- **Índices otimizados**: 15+ índices criados
- **Query optimization**: Subqueries e JOINs eficientes
- **Lazy loading**: Carrega apenas dados necessários

## 🎯 Casos de Uso

### Aluno explora outros alunos

```bash
# Ver 20 alunos aleatórios
GET /api/students/explore

# Filtrar alunos da USP
GET /api/students/explore?universities=USP

# Buscar "João" na USP com interesse em Python
GET /api/students/explore?search_name=João&universities=USP&interests=Python
```

### Aluno recebe sugestões personalizadas

```bash
# Sugestões baseadas nos meus interesses
GET /api/students/suggestions?limit=10

# Retorna alunos com maior compatibilidade
# Mostra interesses em comum
# Exclui quem já é amigo
```

### Aluno visualiza comunidade da universidade

```bash
# Ver todos os alunos da minha universidade
GET /api/students/my-university

# Ver grupo da minha universidade
GET /api/students/groups/my-university

# Ver alunos de outra universidade
GET /api/students/universities/unicamp
```

## 🔐 Autenticação

Todos os endpoints requerem autenticação JWT:

```bash
Authorization: Bearer <seu-token>
```

Obtido via:
```bash
POST /auth/login
```

## 📚 Documentação Completa

- **API Reference**: `STUDENT_DIRECTORY_API.md` (exemplos de curl completos)
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md` (detalhes técnicos)
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Supabase Database
POSTGRES_USER=postgres.wlroivffcmaktuzcaygv
POSTGRES_PASSWORD=sua-senha-supabase
POSTGRES_DB=postgres
POSTGRES_HOST=aws-1-us-east-2.pooler.supabase.com
POSTGRES_PORT=5432

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (para verificação)
EMAIL_SENDER=seu-email@gmail.com
EMAIL_APP_PASSWORD=sua-senha-app
```

## 🐛 Troubleshooting

### Erro: "Nenhuma tabela encontrada"

Execute as migrations:
```bash
# No Supabase SQL Editor
cat migrations_supabase.sql
```

### Erro: "Você ainda não cadastrou sua universidade"

Atualize o perfil:
```bash
PUT /profiles/me
{
  "university": "USP",
  "course": "Engenharia de Computação"
}
```

### Erro: "Complete seu perfil com mais tags"

Adicione pelo menos 3 interesses:
```bash
POST /profiles/me/interests
{
  "interests": ["Python", "Design", "Fotografia"]
}
```

### Grupos não aparecem

Sincronize manualmente (como admin):
```bash
POST /api/students/groups/sync-all
```

## 📈 Próximos Passos (Fase 2)

- [ ] Cache Redis para facets
- [ ] Elasticsearch para buscas complexas
- [ ] ML avançado para sugestões (TF-IDF, Word2Vec)
- [ ] Chat de grupo por universidade
- [ ] Histórico de buscas
- [ ] Filtros favoritos salvos

## 🤝 Contribuindo

Para adicionar novos filtros ou funcionalidades:

1. **Schema**: Adicione em `schemas/student_directory.py`
2. **Service**: Implemente lógica em `services/student_directory.py`
3. **Route**: Adicione endpoint em `api/student_directory.py`
4. **Migration**: Atualize `migrations_supabase.sql`
5. **Docs**: Documente em `STUDENT_DIRECTORY_API.md`

## 📝 Changelog

### v1.0.0 (2025-11-01)

- ✅ Implementados todos os RFs (RF047-RF055)
- ✅ 9 endpoints novos
- ✅ 2 tabelas novas
- ✅ 15+ índices para performance
- ✅ Algoritmo de sugestões (Jaccard Similarity)
- ✅ Grupos automáticos por universidade
- ✅ Hooks de atualização automática
- ✅ Documentação completa

---

**Desenvolvido para:** ISMART Conecta
**Data:** 2025-11-01
**Versão:** 1.0.0
