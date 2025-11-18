#!/bin/bash

# ============================================================================
# ISMART Conecta - Database Reset Script
# ============================================================================
# Script para limpar e resetar o banco de dados
# ============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

main() {
    print_header "DATABASE RESET TOOL"

    print_info "Opções:"
    echo "1. Limpar todos os dados (manter estrutura)"
    echo "2. Dropar e recriar banco (reset completo)"
    echo "3. Dropar volume Docker (reset total)"
    echo ""
    read -p "Escolha uma opção (1-3): " option

    case $option in
        1)
            print_info "Limpando todos os dados..."
            docker compose exec db psql -U postgres -d ismart_db -c "
                DELETE FROM comment_votes CASCADE;
                DELETE FROM thread_votes CASCADE;
                DELETE FROM comments CASCADE;
                DELETE FROM threads CASCADE;
                DELETE FROM user_badges CASCADE;
                DELETE FROM badges CASCADE;
                DELETE FROM university_group_members CASCADE;
                DELETE FROM university_groups CASCADE;
                DELETE FROM user_interests CASCADE;
                DELETE FROM interests CASCADE;
                DELETE FROM friendships CASCADE;
                DELETE FROM profiles CASCADE;
                DELETE FROM user_stats CASCADE;
                DELETE FROM users CASCADE;
            "
            print_success "Banco de dados limpo com sucesso!"
            ;;

        2)
            print_warning "Esta ação irá dropar todo o banco de dados!"
            read -p "Tem certeza? (sim/nao): " confirm
            if [ "$confirm" = "sim" ]; then
                print_info "Derrubando container do banco..."
                docker compose down db
                print_success "Container do banco derrubado"

                print_info "Aguardando..."
                sleep 5

                print_info "Reiniciando container..."
                docker compose up -d db
                print_success "Container reiniciado"

                print_info "Aguardando banco ficar pronto..."
                sleep 15

                print_info "Executando migrations..."
                docker compose exec backend alembic upgrade head
                print_success "Database reset completo!"
            else
                print_info "Operação cancelada"
            fi
            ;;

        3)
            print_warning "Esta ação irá deletar TODO O VOLUME DO BANCO!"
            read -p "Tem certeza? (sim/nao): " confirm
            if [ "$confirm" = "sim" ]; then
                print_info "Parando containers..."
                docker compose down -v
                print_success "Containers e volumes deletados"

                print_info "Aguardando..."
                sleep 5

                print_info "Reiniciando..."
                docker compose up -d
                print_info "Aguardando banco ficar pronto..."
                sleep 20
                print_success "Reset total completo! Todos os dados foram deletados."
            else
                print_info "Operação cancelada"
            fi
            ;;

        *)
            print_warning "Opção inválida"
            exit 1
            ;;
    esac

    print_info ""
    print_info "Próximos passos:"
    echo "  - Execute o script de testes: ./test_api.sh"
    echo "  - Acesse o banco: psql -h localhost -U postgres -d ismart_db"
    echo ""
}

main
