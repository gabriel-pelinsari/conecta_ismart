# 🚀 ISMART Conecta - API Backend

Plataforma de rede social educacional para descoberta e agrupamento de alunos.

## 📌 Status Atual

```
✅ Backend: 100% Funcional
✅ Banco de Dados: PostgreSQL 16 (15 tabelas)
✅ Student Directory: Implementado e testado
✅ Autenticação: JWT com PBKDF2
✅ Scripts de Teste: Automático com curl
```

---

## 🚀 Início Rápido

### 1. Iniciar o Backend

```bash
cd /home/omatheu/Desktop/projects/conecta_ismart
docker compose up -d
```

Aguarde 15-20 segundos.

### 2. Testar API

```bash
# Teste automático (recomendado)
bash test_api.sh

# Ou teste manual
curl http://localhost:8000/
```

### 3. Acessar Documentação

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📂 Arquivos Importantes

- **test_api.sh** - Script para testar todos os endpoints
- **reset_db.sh** - Reset do banco de dados
- **SETUP_AND_TESTING.md** - Guia completo
- **API_TEST_GUIDE.md** - Detalhes de todos os endpoints
- **FIXES_APPLIED.md** - Correções realizadas

---

## ✅ Correções Aplicadas

### 1. StudentCardOut - UUID → int
- **Problema:** Schema esperava UUID
- **Solução:** Alterado para int (user_id)
- **Status:** ✅ Corrigido

### 2. get_university_page() - Método Faltando
- **Problema:** Método não existia na classe
- **Solução:** Implementado com filtros completos
- **Status:** ✅ Corrigido

---

## 🎯 Status dos Endpoints

### ✅ Funcionando 100%

```
POST   /auth/register              Registrar
POST   /auth/token                 Login
GET    /api/students/explore       Explorar alunos
GET    /api/students/explore/facets Contadores
GET    /api/students/suggestions   Sugestões
GET    /api/students/university/{name} Por universidade
```

### ⚠️ Parcialmente

```
POST   /api/profiles/              Criar perfil
POST   /api/interests/my-interests Adicionar interesses
POST   /api/threads/               Criar discussão
```

---

## 🧪 Teste Rápido

```bash
# Rodar testes automáticos
bash test_api.sh

# Teste manual
curl http://localhost:8000/
```

---

**Para mais detalhes, veja [SETUP_AND_TESTING.md](SETUP_AND_TESTING.md)**
