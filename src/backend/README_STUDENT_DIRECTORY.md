# 🎓 Diretório de Alunos - Módulo 4: Descoberta e Agrupamento

## 📋 Visão Geral

Implementação completa do sistema de descoberta e agrupamento de alunos da plataforma ISMART Conecta, **adaptada para usar o schema existente do Supabase SEM migrations**.

- ✅ **RF047**: Página "Explorar" com lista de alunos
- ✅ **RF048**: Filtro por universidade
- ✅ **RF049**: Filtro por curso
- ✅ **RF050**: Filtro por interesses comuns
- ✅ **RF051**: Sugestões de conexão baseadas em vetorização
- ✅ **RF052**: Grupos virtuais por universidade (calculados dinamicamente)
- ✅ **RF053**: Página dedicada por universidade
- ✅ **RF054**: Busca de alunos por nome
- ✅ **RF055**: Filtros combinados

## ✨ Sem Migrations!

Esta implementação **NÃO requer criação de novas tabelas** ou modificações no banco de dados. Usa apenas as tabelas existentes do Supabase:
- `profiles`
- `connections`
- `interests`
- `profile_interests`
- `universities`

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

### 2. Iniciar Backend

```bash
# Instalar dependências (se necessário)
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Testar Endpoints

Acesse a documentação interativa:
```
http://localhost:8000/docs
```

## 📂 Estrutura de Arquivos

### Arquivos Criados (Adaptados para Supabase)

```
src/backend/
├── app/
│   ├── api/
│   │   └── student_directory_supabase.py    # 7 endpoints (sem migrations)
│   ├── models/
│   │   └── supabase_models.py               # Mapeia tabelas existentes
│   ├── schemas/
│   │   └── student_directory.py             # Schemas com UUID
│   └── services/
│       └── student_directory_supabase.py    # Lógica adaptada
├── NO_MIGRATIONS_SETUP.md                   # Guia de setup sem migrations
└── README_STUDENT_DIRECTORY.md              # Este arquivo
```

### Arquivos Modificados

```
src/backend/
├── app/
│   └── main.py                              # + router student_directory_supabase
└── .env                                     # + credenciais Supabase
```

## 🔗 Endpoints Implementados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/students/explore` | Lista alunos com filtros (RF047-RF055) |
| GET | `/api/students/explore/facets` | Contadores de filtros |
| GET | `/api/students/suggestions` | Sugestões de conexão (RF051) |
| GET | `/api/students/universities/{slug}` | Página de universidade (RF053) |
| GET | `/api/students/my-university` | Atalho minha universidade |
| GET | `/api/students/groups/my-university` | Meu grupo virtual (RF052) |
| GET | `/api/students/groups` | Todos os grupos virtuais (RF052) |

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

### Teste 4: Meu Grupo Virtual

```bash
curl -X GET "http://localhost:8000/api/students/groups/my-university" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

## 📊 Tabelas do Banco de Dados (Existentes)

### Tabelas Usadas (Já no Supabase)

| Tabela | Uso | Campos Principais |
|--------|-----|-------------------|
| `profiles` | Perfis dos alunos | id (UUID), full_name, university_id, course, entry_year |
| `connections` | Status de conexão | requester_id, addressee_id, status ('pendente', 'aceita', 'rejeitada') |
| `interests` | Tags/interesses | id (bigint), name, approved |
| `profile_interests` | Associação perfil-interesse | profile_id (UUID), interest_id (bigint) |
| `universities` | Dados das universidades | id (bigint), name, address |

### Nenhuma Tabela Nova!

✅ RF052 (Grupos) implementado como **grupos virtuais** calculados dinamicamente
- Não cria tabelas `university_groups` ou `university_group_members`
- Grupos são calculados em tempo real a partir dos alunos de cada universidade

## 🔍 Recursos Principais

### 1. Sistema de Filtros Avançado

Combine múltiplos filtros simultaneamente:
- **Universidade** (múltipla seleção)
- **Curso** (múltipla seleção)
- **Interesses/Tags** (múltipla seleção, apenas aprovados)
- **Ano de entrada** (substitui "semestre")
- **Busca por nome** (case-insensitive, mínimo 2 caracteres)
- **Ordenação** (random, name, compatibility, recent)

### 2. Algoritmo de Sugestões (RF051)

- **Algoritmo**: Jaccard Similarity
- **Input**: Interesses/tags do usuário
- **Output**: Lista ordenada por compatibilidade (0-100%)
- **Requer**: Mínimo 3 interesses no perfil
- **Exclui**: Alunos já conectados e solicitações pendentes

### 3. Grupos Virtuais (RF052)

- **Calculados dinamicamente** (sem tabela)
- **1 grupo por universidade** (todos os alunos daquela universidade)
- **Sempre atualizado** (conta em tempo real)
- **Sem sincronização** necessária

### 4. Performance

- **Paginação**: Offset/limit padrão 20
- **Eager loading**: Carrega relationships necessários
- **Query optimization**: JOINs eficientes
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

# Ver grupo virtual da minha universidade
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

- **Setup Guide**: `NO_MIGRATIONS_SETUP.md` (instruções detalhadas sem migrations)
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

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

### Erro: "Cannot convert UUID to string"

**Causa:** Inconsistência entre tipos de ID

**Solução:** O código já faz a conversão automaticamente. Certifique-se de usar os modelos corretos:
- Use `supabase_models.py` para queries de alunos
- Use `student_directory_supabase.py` para serviços

### Erro: "Você ainda não cadastrou sua universidade"

**Causa:** Perfil sem `university_id`

**Solução:** Atualize o perfil com uma universidade válida:
```bash
PUT /profiles/me
{
  "university_id": 1,
  "course": "Engenharia de Computação"
}
```

### Erro: "Complete seu perfil com mais interesses"

**Causa:** Menos de 3 interesses cadastrados para usar sugestões

**Solução:** Adicione pelo menos 3 interesses aprovados ao perfil via endpoints existentes de interests.

### Erro: "Table 'profiles' not found"

**Causa:** Conexão incorreta com Supabase

**Solução:**
1. Verifique as credenciais no `.env`
2. Teste a conexão manualmente
3. Verifique se o pooler do Supabase está ativo

## 🔄 Adaptações do Schema Original

### Campos Mapeados

| Campo Original | Campo Supabase | Tipo |
|----------------|----------------|------|
| `id` (Integer) | `id` (UUID) | Convertido automaticamente |
| `semester` | `entry_year` (Integer) | Substituído |
| `is_public` | `show_university_course` (Boolean) | Equivalente |
| `university` (String) | `university_id` → `universities.name` | Via relationship |

### Status de Conexão

| Código | Supabase | Significado |
|--------|----------|-------------|
| `not_connected` | - | Não existe conexão |
| `pending_sent` | `pendente` (requester) | Solicitação enviada |
| `pending_received` | `pendente` (addressee) | Solicitação recebida |
| `connected` | `aceita` | Conectados |

## 📈 Próximos Passos (Fase 2)

- [ ] Cache Redis para facets
- [ ] Elasticsearch para buscas complexas
- [ ] ML avançado para sugestões (TF-IDF, Word2Vec)
- [ ] Chat de grupo por universidade
- [ ] Histórico de buscas
- [ ] Filtros favoritos salvos

## 📝 Changelog

### v2.0.0 (2025-11-01) - Adaptação Supabase

- ✅ Implementados todos os RFs (RF047-RF055)
- ✅ 7 endpoints funcionais
- ✅ **Zero tabelas novas** (usa schema existente)
- ✅ Grupos virtuais (RF052) calculados dinamicamente
- ✅ Adaptação para UUID e schema Supabase
- ✅ Algoritmo de sugestões (Jaccard Similarity)
- ✅ **Sem migrations necessárias**
- ✅ Documentação completa

---

**Desenvolvido para:** ISMART Conecta
**Data:** 2025-11-01
**Versão:** 2.0.0 (Adaptado para Supabase - SEM MIGRATIONS)
