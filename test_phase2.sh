#!/bin/bash

# ISMART Conecta - Phase 2 Features Test Script
# Testa: Notifications, Events, Mentorship

API_URL="http://localhost:8000"
ADMIN_EMAIL="admin@ismart.com"
ADMIN_PASSWORD="Admin@123"
USER1_EMAIL="user1@ismart.com"
USER1_PASSWORD="User@123"
USER2_EMAIL="user2@ismart.com"
USER2_PASSWORD="User@123"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_section() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"
}

print_test() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

# Function to make API calls and check response
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4

    if [ -z "$data" ]; then
        curl -s -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token"
    else
        curl -s -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data"
    fi
}

# Check API availability
print_section "Verificando API"
print_test "Testando conexão com API..."
RESPONSE=$(curl -s "$API_URL/")
if echo "$RESPONSE" | grep -q "online"; then
    print_success "API está disponível"
else
    print_error "API não está respondendo"
    exit 1
fi

# ==================== AUTHENTICATION ====================
print_section "1. Autenticação - Criando usuários de teste"

print_test "Registrando usuário 1 ($USER1_EMAIL)..."
RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER1_EMAIL\",\"password\":\"$USER1_PASSWORD\",\"nome_completo\":\"User One\",\"matricula\":\"123456\"}")

if echo "$RESPONSE" | grep -q "user_id"; then
    USER1_ID=$(echo "$RESPONSE" | jq -r '.user_id')
    print_success "Usuário 1 criado (ID: $USER1_ID)"
else
    print_error "Erro ao criar usuário 1"
fi

print_test "Registrando usuário 2 ($USER2_EMAIL)..."
RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER2_EMAIL\",\"password\":\"$USER2_PASSWORD\",\"nome_completo\":\"User Two\",\"matricula\":\"789012\"}")

if echo "$RESPONSE" | grep -q "user_id"; then
    USER2_ID=$(echo "$RESPONSE" | jq -r '.user_id')
    print_success "Usuário 2 criado (ID: $USER2_ID)"
else
    print_error "Erro ao criar usuário 2"
fi

# Get tokens
print_test "Obtendo tokens de autenticação..."
TOKEN1=$(curl -s -X POST "$API_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER1_EMAIL\",\"password\":\"$USER1_PASSWORD\"}" | jq -r '.access_token')

TOKEN2=$(curl -s -X POST "$API_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$USER2_EMAIL\",\"password\":\"$USER2_PASSWORD\"}" | jq -r '.access_token')

if [ "$TOKEN1" != "null" ] && [ -n "$TOKEN1" ]; then
    print_success "Token 1 obtido"
else
    print_error "Erro ao obter token 1"
fi

if [ "$TOKEN2" != "null" ] && [ -n "$TOKEN2" ]; then
    print_success "Token 2 obtido"
else
    print_error "Erro ao obter token 2"
fi

# ==================== NOTIFICATIONS ====================
print_section "2. Notificações (Phase 2)"

print_test "Listando notificações do usuário 1..."
RESPONSE=$(api_call GET "/api/notifications/" "" "$TOKEN1")
if echo "$RESPONSE" | grep -q "notifications\|id"; then
    COUNT=$(echo "$RESPONSE" | jq '.notifications | length')
    print_success "Notificações listadas (Total: $COUNT)"
else
    print_error "Erro ao listar notificações"
fi

print_test "Verificando contador de notificações não lidas..."
RESPONSE=$(api_call GET "/api/notifications/unread-count" "" "$TOKEN1")
if echo "$RESPONSE" | grep -q "unread_count"; then
    COUNT=$(echo "$RESPONSE" | jq '.unread_count')
    print_success "Contador obtido (Não lidas: $COUNT)"
else
    print_error "Erro ao obter contador"
fi

print_test "Consultando preferências de notificações..."
RESPONSE=$(api_call GET "/api/notifications/preferences" "" "$TOKEN1")
if echo "$RESPONSE" | grep -q "preferences\|enabled"; then
    print_success "Preferências obtidas"
else
    print_error "Erro ao obter preferências"
fi

print_test "Listando tipos de notificações disponíveis..."
RESPONSE=$(api_call GET "/api/notifications/types" "" "$TOKEN1")
if echo "$RESPONSE" | grep -q "types\|\[\]"; then
    COUNT=$(echo "$RESPONSE" | jq '.types | length' 2>/dev/null || echo "tipos listados")
    print_success "Tipos de notificação listados"
else
    print_error "Erro ao listar tipos"
fi

# ==================== EVENTS ====================
print_section "3. Eventos (Phase 2)"

print_test "Criando novo evento..."
EVENT_DATA="{
    \"title\":\"Workshop de Python\",
    \"description\":\"Aprendendo Python do zero\",
    \"event_type\":\"workshop\",
    \"start_time\":\"2025-12-15T14:00:00\",
    \"end_time\":\"2025-12-15T16:00:00\",
    \"location\":\"Sala 101\",
    \"is_online\":false,
    \"capacity\":30
}"
RESPONSE=$(api_call POST "/api/events/" "$EVENT_DATA" "$TOKEN1")
if echo "$RESPONSE" | grep -q "id\|title"; then
    EVENT_ID=$(echo "$RESPONSE" | jq -r '.id')
    print_success "Evento criado (ID: $EVENT_ID)"
else
    print_error "Erro ao criar evento: $(echo $RESPONSE | jq -r '.detail' 2>/dev/null || echo $RESPONSE)"
fi

print_test "Listando todos os eventos..."
RESPONSE=$(api_call GET "/api/events/" "" "$TOKEN1")
if echo "$RESPONSE" | grep -q "events\|items"; then
    COUNT=$(echo "$RESPONSE" | jq '.items | length' 2>/dev/null || echo "eventos")
    print_success "Eventos listados"
else
    print_error "Erro ao listar eventos"
fi

if [ -n "$EVENT_ID" ] && [ "$EVENT_ID" != "null" ]; then
    print_test "Obtendo detalhes do evento ($EVENT_ID)..."
    RESPONSE=$(api_call GET "/api/events/$EVENT_ID" "" "$TOKEN1")
    if echo "$RESPONSE" | grep -q "title\|description"; then
        print_success "Detalhes do evento obtidos"
    else
        print_error "Erro ao obter detalhes"
    fi

    print_test "Confirmando presença no evento..."
    RSVP_DATA="{\"status\":\"confirmed\"}"
    RESPONSE=$(api_call POST "/api/events/$EVENT_ID/rsvp" "$RSVP_DATA" "$TOKEN1")
    if echo "$RESPONSE" | grep -q "status\|confirmed"; then
        print_success "Presença confirmada"
    else
        print_error "Erro ao confirmar presença"
    fi

    print_test "Obtendo lista de participantes..."
    RESPONSE=$(api_call GET "/api/events/$EVENT_ID/participants" "" "$TOKEN1")
    if echo "$RESPONSE" | grep -q "participants"; then
        COUNT=$(echo "$RESPONSE" | jq '.participants | length')
        print_success "Participantes listados (Total: $COUNT)"
    else
        print_error "Erro ao listar participantes"
    fi

    print_test "Obtendo estatísticas do evento..."
    RESPONSE=$(api_call GET "/api/events/$EVENT_ID/stats" "" "$TOKEN1")
    if echo "$RESPONSE" | grep -q "total_participants\|confirmed\|maybe"; then
        print_success "Estatísticas obtidas"
    else
        print_error "Erro ao obter estatísticas"
    fi
fi

# ==================== MENTORSHIP ====================
print_section "4. Mentoria (Phase 2)"

print_test "Consultando mentores disponíveis..."
RESPONSE=$(api_call GET "/api/mentorship/available-mentors" "" "$TOKEN1")
if echo "$RESPONSE" | grep -q "mentors\|\[\]"; then
    print_success "Lista de mentores obtida"
else
    print_error "Erro ao listar mentores"
fi

print_test "Solicitando um mentor..."
MENTOR_REQUEST="{\"reason\":\"Quero aprender desenvolvimento web\"}"
RESPONSE=$(api_call POST "/api/mentorship/request-mentor" "$MENTOR_REQUEST" "$TOKEN1")
if echo "$RESPONSE" | grep -q "id\|queue"; then
    print_success "Solicitação de mentor enviada"
else
    print_error "Erro ao solicitar mentor: $(echo $RESPONSE | jq '.detail' 2>/dev/null || echo 'erro desconhecido')"
fi

print_test "Consultando posição na fila..."
RESPONSE=$(api_call GET "/api/mentorship/queue/my-position" "" "$TOKEN1")
if echo "$RESPONSE" | grep -q "position\|queue"; then
    POSITION=$(echo "$RESPONSE" | jq '.position' 2>/dev/null || echo "fila")
    print_success "Posição na fila obtida"
else
    print_error "Erro ao obter posição"
fi

print_test "Consultando meus mentoreados (mentor)..."
RESPONSE=$(api_call GET "/api/mentorship/my-mentees" "" "$TOKEN2")
if echo "$RESPONSE" | grep -q "mentees\|\[\]"; then
    print_success "Lista de mentoreados obtida"
else
    print_error "Erro ao listar mentoreados"
fi

print_test "Obtendo estatísticas de mentoria..."
RESPONSE=$(api_call GET "/api/mentorship/stats" "" "$TOKEN1")
if echo "$RESPONSE" | grep -q "active\|completed\|cancelled"; then
    print_success "Estatísticas de mentoria obtidas"
else
    print_error "Erro ao obter estatísticas"
fi

# ==================== SUMMARY ====================
print_section "Resumo dos Testes"

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo -e "${GREEN}✓ Testes passaram: ${TESTS_PASSED}${NC}"
echo -e "${RED}✗ Testes falharam: ${TESTS_FAILED}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Total: ${TOTAL}${NC}\n"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}\n"
    exit 0
else
    echo -e "${RED}⚠ Alguns testes falharam. Verifique os logs acima.${NC}\n"
    exit 1
fi
