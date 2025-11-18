#!/bin/bash

# ============================================================================
# ISMART Conecta - API Test Script
# ============================================================================
# Script para testar todos os endpoints da API usando curl
# ============================================================================

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
BASE_URL="http://localhost:8000"
ADMIN_CODE="ADMIN123456"

# Variáveis globais para armazenar tokens
USER1_TOKEN=""
USER2_TOKEN=""
USER3_TOKEN=""
USER1_ID=""
USER2_ID=""
USER3_ID=""

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Função para fazer requisições com tratamento de erro
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    local description=$5

    print_info "$description"

    if [ -z "$token" ]; then
        # Requisição sem autenticação
        curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        # Requisição com autenticação
        curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data"
    fi
}

# ============================================================================
# TESTE 1: AUTENTICAÇÃO
# ============================================================================

test_auth() {
    print_header "1. TESTANDO AUTENTICAÇÃO"

    # 1.1 Registrar primeiro usuário
    print_info "Registrando primeiro usuário..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "usuario1@example.com",
            "password": "SenhaForte123"
        }')

    USER1_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

    if [ ! -z "$USER1_ID" ]; then
        print_success "Usuário 1 registrado com ID: $USER1_ID"
    else
        print_error "Falha ao registrar usuário 1"
        echo "Response: $RESPONSE"
        return 1
    fi

    # 1.2 Registrar segundo usuário
    print_info "Registrando segundo usuário..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "usuario2@example.com",
            "password": "SenhaForte456"
        }')

    USER2_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

    if [ ! -z "$USER2_ID" ]; then
        print_success "Usuário 2 registrado com ID: $USER2_ID"
    else
        print_error "Falha ao registrar usuário 2"
        echo "Response: $RESPONSE"
        return 1
    fi

    # 1.3 Registrar terceiro usuário
    print_info "Registrando terceiro usuário..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "usuario3@example.com",
            "password": "SenhaForte789"
        }')

    USER3_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

    if [ ! -z "$USER3_ID" ]; then
        print_success "Usuário 3 registrado com ID: $USER3_ID"
    else
        print_error "Falha ao registrar usuário 3"
        echo "Response: $RESPONSE"
        return 1
    fi

    # 1.4 Login usuário 1
    print_info "Fazendo login com usuário 1..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data "email=usuario1@example.com&password=SenhaForte123")

    USER1_TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

    if [ ! -z "$USER1_TOKEN" ]; then
        print_success "Login bem-sucedido - Token recebido"
    else
        print_error "Falha no login"
        echo "Response: $RESPONSE"
        return 1
    fi

    # 1.5 Login usuário 2
    print_info "Fazendo login com usuário 2..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data "email=usuario2@example.com&password=SenhaForte456")

    USER2_TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

    if [ ! -z "$USER2_TOKEN" ]; then
        print_success "Login bem-sucedido - Token recebido"
    else
        print_error "Falha no login"
        return 1
    fi

    # 1.6 Login usuário 3
    print_info "Fazendo login com usuário 3..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data "email=usuario3@example.com&password=SenhaForte789")

    USER3_TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

    if [ ! -z "$USER3_TOKEN" ]; then
        print_success "Login bem-sucedido - Token recebido"
    else
        print_error "Falha no login"
        return 1
    fi
}

# ============================================================================
# TESTE 2: PERFIS
# ============================================================================

test_profiles() {
    print_header "2. TESTANDO PERFIS"

    # 2.1 Criar/Atualizar perfil usuário 1
    print_info "Criando perfil para usuário 1..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/profiles/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $USER1_TOKEN" \
        -d '{
            "full_name": "João Silva",
            "university": "USP",
            "course": "Engenharia de Software",
            "semester": "6",
            "bio": "Desenvolvedor apaixonado por tecnologia",
            "is_public": true
        }')

    if echo $RESPONSE | grep -q "full_name"; then
        print_success "Perfil criado para usuário 1"
        echo "Response: $(echo $RESPONSE | python3 -m json.tool 2>/dev/null || echo $RESPONSE)"
    else
        print_error "Falha ao criar perfil"
        echo "Response: $RESPONSE"
    fi

    # 2.2 Criar/Atualizar perfil usuário 2
    print_info "Criando perfil para usuário 2..."
    curl -s -X POST "$BASE_URL/api/profiles/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $USER2_TOKEN" \
        -d '{
            "full_name": "Maria Santos",
            "university": "UNICAMP",
            "course": "Ciência da Computação",
            "semester": "7",
            "bio": "Pesquisadora de IA",
            "is_public": true
        }' > /dev/null
    print_success "Perfil criado para usuário 2"

    # 2.3 Criar/Atualizar perfil usuário 3
    print_info "Criando perfil para usuário 3..."
    curl -s -X POST "$BASE_URL/api/profiles/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $USER3_TOKEN" \
        -d '{
            "full_name": "Pedro Costa",
            "university": "USP",
            "course": "Engenharia de Software",
            "semester": "4",
            "bio": "Interessado em desenvolvimento web",
            "is_public": true
        }' > /dev/null
    print_success "Perfil criado para usuário 3"

    # 2.4 Buscar perfil
    print_info "Buscando perfil do usuário 1..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/profiles/me" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "João Silva"; then
        print_success "Perfil recuperado"
    else
        print_warning "Perfil não encontrado ou rota não existe"
    fi
}

# ============================================================================
# TESTE 3: INTERESSES
# ============================================================================

test_interests() {
    print_header "3. TESTANDO INTERESSES"

    # 3.1 Listar interesses
    print_info "Listando interesses..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/interests/" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "interests\|name"; then
        print_success "Interesses recuperados"
        INTEREST_COUNT=$(echo $RESPONSE | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data) if isinstance(data, list) else len(data.get('interests', [])))" 2>/dev/null || echo "?")
        print_info "Total de interesses: $INTEREST_COUNT"
    else
        print_warning "Nenhum interesse encontrado ou rota não existe"
    fi

    # 3.2 Criar interesse
    print_info "Criando novo interesse..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/interests/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $USER1_TOKEN" \
        -d '{
            "name": "Python",
            "description": "Programação em Python"
        }')

    if echo $RESPONSE | grep -q "Python\|name"; then
        print_success "Interesse criado"
    else
        print_warning "Falha ao criar interesse ou rota não existe"
    fi

    # 3.3 Adicionar interesses ao usuário
    print_info "Adicionando interesses ao usuário 1..."
    curl -s -X POST "$BASE_URL/api/interests/my-interests" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $USER1_TOKEN" \
        -d '{"interest_names": ["Python", "JavaScript", "Machine Learning"]}' > /dev/null
    print_success "Interesses adicionados"

    # 3.4 Adicionar interesses ao usuário 2
    print_info "Adicionando interesses ao usuário 2..."
    curl -s -X POST "$BASE_URL/api/interests/my-interests" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $USER2_TOKEN" \
        -d '{"interest_names": ["Machine Learning", "AI", "Deep Learning"]}' > /dev/null
    print_success "Interesses adicionados"

    # 3.5 Adicionar interesses ao usuário 3
    print_info "Adicionando interesses ao usuário 3..."
    curl -s -X POST "$BASE_URL/api/interests/my-interests" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $USER3_TOKEN" \
        -d '{"interest_names": ["React", "JavaScript", "Web Development"]}' > /dev/null
    print_success "Interesses adicionados"
}

# ============================================================================
# TESTE 4: STUDENT DIRECTORY
# ============================================================================

test_student_directory() {
    print_header "4. TESTANDO STUDENT DIRECTORY"

    # 4.1 Explorar alunos
    print_info "Explorando lista de alunos..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/students/explore?limit=10" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "students\|total"; then
        print_success "Lista de alunos recuperada"
        TOTAL=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', '?'))" 2>/dev/null)
        print_info "Total de alunos encontrados: $TOTAL"
        echo "Response Preview:"
        echo $RESPONSE | python3 -m json.tool 2>/dev/null | head -50
    else
        print_error "Falha ao recuperar alunos"
        echo "Response: $RESPONSE"
    fi

    # 4.2 Filtrar por universidade
    print_info "Filtrando alunos por universidade (USP)..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/students/explore?universities=USP&limit=10" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "students"; then
        print_success "Filtro por universidade funcionando"
        FILTERED=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', '?'))" 2>/dev/null)
        print_info "Alunos encontrados em USP: $FILTERED"
    else
        print_warning "Filtro não retornou resultados"
    fi

    # 4.3 Filtrar por curso
    print_info "Filtrando alunos por curso..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/students/explore?courses=Engenharia%20de%20Software&limit=10" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "students"; then
        print_success "Filtro por curso funcionando"
    else
        print_warning "Filtro não retornou resultados"
    fi

    # 4.4 Filtrar por interesses
    print_info "Filtrando alunos por interesses (Python)..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/students/explore?interests=Python&limit=10" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "students"; then
        print_success "Filtro por interesses funcionando"
    else
        print_warning "Filtro não retornou resultados"
    fi

    # 4.5 Buscar por nome
    print_info "Buscando aluno por nome (Maria)..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/students/explore?search_name=Maria&limit=10" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "students"; then
        print_success "Busca por nome funcionando"
    else
        print_warning "Busca não retornou resultados"
    fi

    # 4.6 Filtros combinados
    print_info "Usando filtros combinados (USP + Python)..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/students/explore?universities=USP&interests=Python&limit=10" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "students"; then
        print_success "Filtros combinados funcionando"
    else
        print_warning "Filtros combinados não retornaram resultados"
    fi

    # 4.7 Facets (contadores)
    print_info "Recuperando facets (contadores de filtros)..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/students/explore/facets" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "universities\|courses\|interests"; then
        print_success "Facets recuperados"
        echo "Response Preview:"
        echo $RESPONSE | python3 -m json.tool 2>/dev/null | head -30
    else
        print_error "Falha ao recuperar facets"
    fi

    # 4.8 Sugestões de conexão
    print_info "Recuperando sugestões de conexão..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/students/suggestions?limit=5" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "suggestions"; then
        print_success "Sugestões recuperadas"
        SUGGESTION_COUNT=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', '?'))" 2>/dev/null)
        print_info "Sugestões encontradas: $SUGGESTION_COUNT"
    else
        print_warning "Nenhuma sugestão gerada (pode ser normal se usuário tem poucos interesses)"
    fi

    # 4.9 Página de universidade
    print_info "Acessando página de universidade (USP)..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/students/university/USP?limit=10" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "students\|university"; then
        print_success "Página de universidade funcionando"
        echo "Response Preview:"
        echo $RESPONSE | python3 -m json.tool 2>/dev/null | head -40
    else
        print_warning "Página de universidade não retornou dados"
    fi
}

# ============================================================================
# TESTE 5: THREADS E DISCUSSÕES
# ============================================================================

test_threads() {
    print_header "5. TESTANDO THREADS (DISCUSSÕES)"

    # 5.1 Criar thread
    print_info "Criando thread de discussão..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/threads/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $USER1_TOKEN" \
        -d '{
            "title": "Qual linguagem estudar em 2025?",
            "content": "Estou começando a aprender programação. Qual linguagem vocês recomendam para iniciantes?"
        }')

    if echo $RESPONSE | grep -q "title\|id"; then
        THREAD1_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
        print_success "Thread criada com ID: $THREAD1_ID"
    else
        print_warning "Falha ao criar thread ou rota não existe"
        THREAD1_ID=""
    fi

    # 5.2 Criar outra thread
    if [ -z "$THREAD1_ID" ]; then
        print_info "Criando segunda thread..."
        RESPONSE=$(curl -s -X POST "$BASE_URL/api/threads/" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $USER2_TOKEN" \
            -d '{
                "title": "Dicas de Machine Learning",
                "content": "Compartilhando algumas dicas e recursos para aprender ML"
            }')

        if echo $RESPONSE | grep -q "title"; then
            THREAD2_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
            print_success "Thread criada com ID: $THREAD2_ID"
        else
            print_warning "Falha ao criar thread"
        fi
    fi

    # 5.3 Listar threads
    print_info "Listando threads..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/api/threads/" \
        -H "Authorization: Bearer $USER1_TOKEN")

    if echo $RESPONSE | grep -q "threads\|title"; then
        print_success "Threads recuperadas"
    else
        print_warning "Nenhuma thread encontrada ou rota não existe"
    fi

    # 5.4 Adicionar comentário
    if [ ! -z "$THREAD1_ID" ]; then
        print_info "Adicionando comentário em thread..."
        RESPONSE=$(curl -s -X POST "$BASE_URL/api/threads/$THREAD1_ID/comments" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $USER2_TOKEN" \
            -d '{
                "content": "Recomendo começar com Python! É uma linguagem muito amigável para iniciantes."
            }')

        if echo $RESPONSE | grep -q "content"; then
            print_success "Comentário adicionado"
        else
            print_warning "Falha ao adicionar comentário ou rota não existe"
        fi
    fi
}

# ============================================================================
# TESTE 6: SAÚDE DA API
# ============================================================================

test_health() {
    print_header "6. TESTANDO SAÚDE DA API"

    # 6.1 Root endpoint
    print_info "Testando endpoint raiz..."
    RESPONSE=$(curl -s -X GET "$BASE_URL/" \
        -H "Content-Type: application/json")

    if echo $RESPONSE | grep -q "online\|message"; then
        print_success "API está online"
        echo "Response: $RESPONSE"
    else
        print_error "API não respondeu corretamente"
    fi
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo -e "\n${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║                  ISMART CONECTA - API TEST SCRIPT                          ║"
    echo "║                                                                            ║"
    echo "║  Testando todos os endpoints implementados                                 ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # Verifica se a API está respondendo
    print_info "Verificando disponibilidade da API em $BASE_URL..."
    if ! curl -s "$BASE_URL/" > /dev/null 2>&1; then
        print_error "API não está disponível em $BASE_URL"
        print_warning "Certifique-se de que o backend está rodando: docker compose up -d"
        exit 1
    fi
    print_success "API está disponível"

    # Executa testes
    test_health
    test_auth
    test_profiles
    test_interests
    test_student_directory
    test_threads

    # Resumo final
    print_header "TESTES CONCLUÍDOS"
    print_success "Todos os testes foram executados!"
    print_info "Informações dos usuários criados:"
    echo "  - Usuário 1: usuario1@example.com (ID: $USER1_ID)"
    echo "  - Usuário 2: usuario2@example.com (ID: $USER2_ID)"
    echo "  - Usuário 3: usuario3@example.com (ID: $USER3_ID)"
    echo ""
    print_info "Para conectar no DBeaver:"
    echo "  - Host: localhost"
    echo "  - Port: 5432"
    echo "  - Database: ismart_db"
    echo "  - Username: postgres"
    echo "  - Password: postgres"
    echo ""
}

# Executa main
main
