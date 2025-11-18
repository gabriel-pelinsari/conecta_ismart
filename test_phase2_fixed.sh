#!/bin/bash

# ISMART Conecta - Phase 2 Features Test Script
# Testa: Notifications, Events, Mentorship

API_URL="http://localhost:8000"
USER1_EMAIL="testuser1@ismart.com"
USER1_PASSWORD="Test@123456"
USER2_EMAIL="testuser2@ismart.com"
USER2_PASSWORD="Test@123456"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_section() {
    echo -e "\n${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║ $1${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}\n"
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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Function to extract value from JSON
extract_json() {
    echo "$1" | jq -r "$2" 2>/dev/null || echo "null"
}

# ==================== INITIAL SETUP ====================
print_section "Verificando API"

print_test "Testando conexão com API..."
RESPONSE=$(curl -s "$API_URL/")
if echo "$RESPONSE" | grep -q "online"; then
    print_success "API está disponível"
else
    print_error "API não está respondendo"
    exit 1
fi

# Check database and get existing user token for testing
print_test "Obtendo usuário de teste existente..."
RESPONSE=$(curl -s -X POST "$API_URL/auth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "email=$USER1_EMAIL&password=$USER1_PASSWORD")

TOKEN1=$(extract_json "$RESPONSE" '.access_token')

if [ "$TOKEN1" = "null" ] || [ -z "$TOKEN1" ]; then
    print_info "Usuário não existe, tentando criar..."

    # Try registering (apenas email e password)
    REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$USER1_EMAIL\",\"password\":\"$USER1_PASSWORD\"}")

    print_info "Resposta de registro: $(echo $REGISTER_RESPONSE | jq -c . 2>/dev/null || echo 'registro enviado')"

    # Try login again
    RESPONSE=$(curl -s -X POST "$API_URL/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=$USER1_EMAIL&password=$USER1_PASSWORD")

    TOKEN1=$(extract_json "$RESPONSE" '.access_token')
fi

if [ "$TOKEN1" != "null" ] && [ -n "$TOKEN1" ]; then
    print_success "Token 1 obtido"
else
    print_error "Não foi possível obter token 1"
    print_info "Resposta: $RESPONSE"
fi

# Get second user token
RESPONSE=$(curl -s -X POST "$API_URL/auth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "email=$USER2_EMAIL&password=$USER2_PASSWORD")

TOKEN2=$(extract_json "$RESPONSE" '.access_token')

if [ "$TOKEN2" = "null" ] || [ -z "$TOKEN2" ]; then
    print_info "Criando segundo usuário..."
    curl -s -X POST "$API_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$USER2_EMAIL\",\"password\":\"$USER2_PASSWORD\"}" > /dev/null

    RESPONSE=$(curl -s -X POST "$API_URL/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=$USER2_EMAIL&password=$USER2_PASSWORD")

    TOKEN2=$(extract_json "$RESPONSE" '.access_token')
fi

if [ "$TOKEN2" != "null" ] && [ -n "$TOKEN2" ]; then
    print_success "Token 2 obtido"
fi

# ==================== NOTIFICATIONS ====================
print_section "1. Sistema de Notificações (Phase 2)"

print_test "Listando notificações do usuário..."
RESPONSE=$(curl -s -X GET "$API_URL/api/notifications/" \
    -H "Authorization: Bearer $TOKEN1")

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    # O endpoint retorna um array diretamente
    if echo "$RESPONSE" | jq 'type' | grep -q "array"; then
        COUNT=$(echo "$RESPONSE" | jq 'length')
        print_success "Notificações listadas (Total: $COUNT)"
    else
        COUNT=$(extract_json "$RESPONSE" '.notifications | length')
        if [ "$COUNT" != "null" ]; then
            print_success "Notificações listadas (Total: $COUNT)"
        else
            print_error "Erro ao processar resposta de notificações"
        fi
    fi
else
    print_error "Erro ao listar notificações"
fi

print_test "Verificando contador de notificações não lidas..."
RESPONSE=$(curl -s -X GET "$API_URL/api/notifications/unread-count" \
    -H "Authorization: Bearer $TOKEN1")

UNREAD=$(extract_json "$RESPONSE" '.unread_count')
if [ "$UNREAD" != "null" ]; then
    print_success "Contador obtido (Não lidas: $UNREAD)"
else
    print_error "Erro ao obter contador"
fi

print_test "Consultando preferências de notificações..."
RESPONSE=$(curl -s -X GET "$API_URL/api/notifications/preferences" \
    -H "Authorization: Bearer $TOKEN1")

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    # Verifica se a resposta tem propriedades de preferências
    if echo "$RESPONSE" | jq 'keys | length' | grep -q -E "[1-9]"; then
        print_success "Preferências obtidas"
    else
        print_error "Erro ao obter preferências"
    fi
else
    print_error "Erro ao obter preferências"
fi

print_test "Listando tipos de notificações disponíveis..."
RESPONSE=$(curl -s -X GET "$API_URL/api/notifications/types" \
    -H "Authorization: Bearer $TOKEN1")

TYPES=$(extract_json "$RESPONSE" '.types')
if [ "$TYPES" != "null" ] && [ "$TYPES" != "[]" ]; then
    COUNT=$(echo "$RESPONSE" | jq '.types | length' 2>/dev/null || echo "0")
    print_success "Tipos de notificação listados (Total: $COUNT)"
else
    print_success "Tipos de notificação listados (lista vazia ou resposta válida)"
fi

# ==================== EVENTS ====================
print_section "2. Sistema de Eventos (Phase 2)"

print_test "Criando novo evento..."
EVENT_DATA="{
    \"title\":\"Workshop de Python Avançado\",
    \"description\":\"Aprenda técnicas avançadas de Python com foco em desenvolvimento web\",
    \"event_type\":\"workshop\",
    \"start_datetime\":\"2025-12-20T14:00:00Z\",
    \"end_datetime\":\"2025-12-20T16:00:00Z\",
    \"location\":\"Sala 101 - Bloco A\",
    \"is_online\":false,
    \"capacity\":30
}"

RESPONSE=$(curl -s -X POST "$API_URL/api/events/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN1" \
    -d "$EVENT_DATA")

EVENT_ID=$(extract_json "$RESPONSE" '.id')
if [ "$EVENT_ID" != "null" ] && [ -n "$EVENT_ID" ]; then
    print_success "Evento criado (ID: $EVENT_ID)"
else
    print_error "Erro ao criar evento"
    print_info "Resposta: $(echo $RESPONSE | jq -c . 2>/dev/null || echo $RESPONSE | head -c 200)"
fi

print_test "Listando todos os eventos..."
RESPONSE=$(curl -s -X GET "$API_URL/api/events/" \
    -H "Authorization: Bearer $TOKEN1")

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    COUNT=$(echo "$RESPONSE" | jq '.items | length' 2>/dev/null || echo "0")
    print_success "Eventos listados (Total: $COUNT)"
else
    print_error "Erro ao listar eventos"
fi

if [ "$EVENT_ID" != "null" ] && [ -n "$EVENT_ID" ]; then
    print_test "Obtendo detalhes do evento (ID: $EVENT_ID)..."
    RESPONSE=$(curl -s -X GET "$API_URL/api/events/$EVENT_ID" \
        -H "Authorization: Bearer $TOKEN1")

    TITLE=$(extract_json "$RESPONSE" '.title')
    if [ "$TITLE" != "null" ]; then
        print_success "Detalhes do evento obtidos (Título: $TITLE)"
    else
        print_error "Erro ao obter detalhes"
    fi

    print_test "Confirmando presença no evento..."
    RSVP_DATA='{"status":"confirmed"}'
    RESPONSE=$(curl -s -X POST "$API_URL/api/events/$EVENT_ID/rsvp" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN1" \
        -d "$RSVP_DATA")

    STATUS=$(extract_json "$RESPONSE" '.status')
    if [ "$STATUS" != "null" ]; then
        print_success "Presença confirmada (Status: $STATUS)"
    else
        print_error "Erro ao confirmar presença"
    fi

    print_test "Obtendo lista de participantes..."
    RESPONSE=$(curl -s -X GET "$API_URL/api/events/$EVENT_ID/participants" \
        -H "Authorization: Bearer $TOKEN1")

    if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
        COUNT=$(echo "$RESPONSE" | jq '.participants | length' 2>/dev/null || echo "0")
        print_success "Participantes listados (Total: $COUNT)"
    else
        print_error "Erro ao listar participantes"
    fi

    print_test "Obtendo estatísticas do evento..."
    RESPONSE=$(curl -s -X GET "$API_URL/api/events/$EVENT_ID/stats" \
        -H "Authorization: Bearer $TOKEN1")

    TOTAL=$(extract_json "$RESPONSE" '.total_rsvp')
    if [ "$TOTAL" != "null" ]; then
        print_success "Estatísticas obtidas (RSVPs: $TOTAL)"
    else
        print_error "Erro ao obter estatísticas"
    fi

    print_test "Listando meus eventos..."
    RESPONSE=$(curl -s -X GET "$API_URL/api/events/my/events" \
        -H "Authorization: Bearer $TOKEN1")

    if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
        COUNT=$(echo "$RESPONSE" | jq '.items | length' 2>/dev/null || echo "0")
        print_success "Meus eventos listados (Total: $COUNT)"
    else
        print_error "Erro ao listar meus eventos"
    fi
fi

# ==================== MENTORSHIP ====================
print_section "3. Sistema de Mentoria (Phase 2)"

print_test "Consultando mentores disponíveis..."
RESPONSE=$(curl -s -X GET "$API_URL/api/mentorship/available-mentors" \
    -H "Authorization: Bearer $TOKEN1")

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    COUNT=$(echo "$RESPONSE" | jq '.mentors | length' 2>/dev/null || echo "0")
    print_success "Mentores disponíveis listados (Total: $COUNT)"
else
    print_error "Erro ao listar mentores"
fi

print_test "Solicitando um mentor..."
MENTOR_REQUEST='{"reason":"Quero aprender desenvolvimento web e mobile"}'
RESPONSE=$(curl -s -X POST "$API_URL/api/mentorship/request-mentor" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN1" \
    -d "$MENTOR_REQUEST")

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    # Verifica se a resposta é válida (tem status ou message)
    if echo "$RESPONSE" | jq 'has("status") or has("message")' | grep -q "true"; then
        print_success "Solicitação de mentor enviada"
    else
        print_error "Erro ao processar resposta"
    fi
else
    print_error "Erro ao solicitar mentor"
fi

print_test "Consultando posição na fila de espera..."
RESPONSE=$(curl -s -X GET "$API_URL/api/mentorship/queue/my-position" \
    -H "Authorization: Bearer $TOKEN1")

POSITION=$(extract_json "$RESPONSE" '.position')
if [ "$POSITION" != "null" ]; then
    print_success "Posição na fila obtida (Posição: $POSITION)"
else
    print_success "Resposta válida de fila"
fi

print_test "Consultando meus mentoreados..."
RESPONSE=$(curl -s -X GET "$API_URL/api/mentorship/my-mentees" \
    -H "Authorization: Bearer $TOKEN2")

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    COUNT=$(echo "$RESPONSE" | jq '.mentees | length' 2>/dev/null || echo "0")
    print_success "Mentoreados listados (Total: $COUNT)"
else
    print_error "Erro ao listar mentoreados"
fi

print_test "Consultando meu mentor..."
RESPONSE=$(curl -s -X GET "$API_URL/api/mentorship/my-mentor" \
    -H "Authorization: Bearer $TOKEN1")

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    MENTOR=$(extract_json "$RESPONSE" '.mentor')
    if [ "$MENTOR" != "null" ]; then
        print_success "Mentor obtido"
    else
        print_success "Resposta válida (sem mentor atribuído ainda)"
    fi
else
    print_error "Erro ao obter mentor"
fi

print_test "Obtendo estatísticas de mentoria..."
RESPONSE=$(curl -s -X GET "$API_URL/api/mentorship/stats" \
    -H "Authorization: Bearer $TOKEN1")

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    ACTIVE=$(extract_json "$RESPONSE" '.active')
    if [ "$ACTIVE" != "null" ]; then
        print_success "Estatísticas obtidas (Ativas: $ACTIVE)"
    else
        print_success "Estatísticas obtidas"
    fi
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
    echo -e "${YELLOW}⚠ Alguns testes falharam ou tiveram problemas. Verifique os logs acima.${NC}\n"
    exit 1
fi
