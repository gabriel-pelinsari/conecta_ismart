"""
Rotas da API para o diretório de alunos (Módulo 4: Descoberta e Agrupamento)
ADAPTADO PARA O SCHEMA EXISTENTE DO SUPABASE (sem migrations)
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.student_directory import (
    StudentListResponse,
    StudentFilters,
    FilterFacets,
    SuggestionsResponse,
    UniversityPageResponse,
    UniversityGroupOut
)
from app.services.student_directory_supabase import StudentDirectoryService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/students",
    tags=["Students Directory"]
)


@router.get("/explore", response_model=StudentListResponse)
def explore_students(
    # RF054 - Busca por nome
    search_name: Optional[str] = Query(None, min_length=2, description="Busca por nome (mínimo 2 caracteres)"),

    # RF048 - Filtro por universidade (múltipla seleção)
    universities: Optional[List[str]] = Query(None, description="Filtrar por universidade(s)"),

    # RF049 - Filtro por curso (múltipla seleção)
    courses: Optional[List[str]] = Query(None, description="Filtrar por curso(s)"),

    # RF050 - Filtro por interesses
    interests: Optional[List[str]] = Query(None, description="Filtrar por interesse(s)/tag(s)"),

    # Filtro adicional por ano de entrada
    entry_years: Optional[List[int]] = Query(None, description="Filtrar por ano(s) de entrada"),

    # Ordenação
    order_by: str = Query(
        "random",
        description="Ordenação: 'random', 'name', 'compatibility', 'recent'"
    ),

    # Paginação
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    limit: int = Query(20, ge=1, le=100, description="Limite de resultados (max 100)"),

    # Dependências
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **RF047 - Página "Explorar" com lista de alunos**

    Retorna lista paginada de alunos da plataforma com suporte a múltiplos filtros:
    - RF048: Filtro por universidade
    - RF049: Filtro por curso
    - RF050: Filtro por interesses comuns
    - RF054: Busca por nome
    - RF055: Filtros combinados (múltiplos critérios simultâneos)

    **Regras de negócio:**
    - Exibe apenas alunos com perfil público (show_university_course=true)
    - Não exibe o próprio usuário
    - Ordem padrão: aleatória (descoberta)
    - Load inicial: 20 alunos (configurável via limit)
    - Suporta infinite scroll via offset/limit
    - Informações exibidas: foto, nome, universidade, curso, ano entrada, 3 tags principais
    - Status de conexão visível: "not_connected", "pending_sent", "pending_received", "connected"
    """
    try:
        # Converter user.id para UUID
        user_uuid = UUID(str(current_user.id))

        filters = StudentFilters(
            search_name=search_name,
            universities=universities,
            courses=courses,
            interests=interests,
            entry_years=entry_years,
            order_by=order_by,
            offset=offset,
            limit=limit
        )

        result = StudentDirectoryService.get_students_list(
            db=db,
            current_user_id=user_uuid,
            filters=filters
        )

        logger.info(
            f"User {current_user.id} explored students: "
            f"{result.total} results, filters: {filters.dict(exclude_none=True)}"
        )

        return result

    except Exception as e:
        logger.error(f"Error exploring students: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar alunos: {str(e)}"
        )


@router.get("/explore/facets", response_model=FilterFacets)
def get_filter_facets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Retorna facets (contadores) para todos os filtros**

    Útil para exibir na UI:
    - Quantos alunos existem em cada universidade
    - Quantos alunos existem em cada curso
    - Top 50 interesses/tags mais populares (apenas aprovados)
    - Quantos alunos em cada ano de entrada

    Exemplo de uso na UI:
    ```
    USP (45)
    UNICAMP (30)
    FGV (28)
    ```
    """
    try:
        user_uuid = UUID(str(current_user.id))

        facets = StudentDirectoryService.get_filter_facets(
            db=db,
            current_user_id=user_uuid
        )

        return facets

    except Exception as e:
        logger.error(f"Error getting filter facets: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar facets de filtros: {str(e)}"
        )


@router.get("/suggestions", response_model=SuggestionsResponse)
def get_connection_suggestions(
    limit: int = Query(10, ge=1, le=50, description="Número de sugestões (max 50)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **RF051 - Sugestões de conexão baseadas em vetorização de interesses**

    Sistema de recomendação que utiliza similarity entre interesses (tags) para
    sugerir alunos com perfil compatível.

    **Regras de negócio:**
    - Algoritmo: cosine similarity (Jaccard simplificado)
    - Mínimo 3 interesses no perfil para gerar sugestões
    - Não sugere alunos já conectados ou com solicitação pendente
    - Limite: até 50 sugestões por vez
    - Exibe score de compatibilidade (0-100%)
    - Mostra interesses em comum

    **Resposta:**
    - Lista ordenada por compatibilidade (maior primeiro)
    - Cada sugestão inclui: aluno, score, interesses comuns, motivo
    - Se < 3 interesses: retorna mensagem "Complete seu perfil..."
    """
    try:
        user_uuid = UUID(str(current_user.id))

        suggestions = StudentDirectoryService.get_connection_suggestions(
            db=db,
            user_id=user_uuid,
            limit=limit
        )

        logger.info(
            f"User {current_user.id} got {suggestions.total} connection suggestions"
        )

        return suggestions

    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar sugestões de conexão: {str(e)}"
        )


@router.get("/universities/{university_slug}", response_model=UniversityPageResponse)
def get_university_page(
    university_slug: str,
    course: Optional[str] = Query(None, description="Filtrar por curso"),
    interests: Optional[List[str]] = Query(None, description="Filtrar por interesse(s)"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **RF053 - Página dedicada por universidade listando todos os alunos**

    Página específica para cada universidade exibindo lista de todos os alunos
    daquela instituição com filtros e opções de conexão.

    **URL padrão:** `/universidades/{slug-universidade}` (ex: `/universidades/usp`)

    **Regras de negócio:**
    - Exibe foto, nome, curso, ano entrada, tags de cada aluno da universidade
    - Ordenação padrão: aleatória (descoberta)
    - Filtros: curso e tags disponíveis
    - Botão "Adicionar amigo" em cada card
    - Infinite scroll com pagination

    **Resposta:**
    - Estatísticas da universidade (nome, total de alunos, cursos disponíveis)
    - Lista paginada de alunos
    - Metadados de paginação
    """
    try:
        user_uuid = UUID(str(current_user.id))

        result = StudentDirectoryService.get_university_page(
            db=db,
            current_user_id=user_uuid,
            university_slug=university_slug,
            course_filter=course,
            interest_filter=interests,
            offset=offset,
            limit=limit
        )

        logger.info(
            f"User {current_user.id} viewed university page: {university_slug}, "
            f"{result.total} students"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting university page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar página da universidade: {str(e)}"
        )


@router.get("/my-university", response_model=UniversityPageResponse)
def get_my_university_students(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Atalho: Ver alunos da minha universidade**

    Retorna página da universidade do usuário atual (RF048 - RN006).

    **Regras:**
    - Busca automaticamente a universidade do perfil do usuário
    - Retorna erro 404 se usuário não tem universidade cadastrada
    - Comportamento idêntico a GET /universities/{slug}
    """
    try:
        user_uuid = UUID(str(current_user.id))

        # Buscar perfil do usuário atual
        from app.models.supabase_models import ProfileSupabase
        from sqlalchemy.orm import joinedload

        profile = db.query(ProfileSupabase).options(
            joinedload(ProfileSupabase.university)
        ).filter(
            ProfileSupabase.id == user_uuid
        ).first()

        if not profile or not profile.university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Você ainda não cadastrou sua universidade no perfil"
            )

        # Converter nome para slug
        university_slug = profile.university.name.lower().replace(" ", "-")

        result = StudentDirectoryService.get_university_page(
            db=db,
            current_user_id=user_uuid,
            university_slug=university_slug,
            course_filter=None,
            interest_filter=None,
            offset=offset,
            limit=limit
        )

        logger.info(
            f"User {current_user.id} viewed their university page: {profile.university.name}"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting my university: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar alunos da sua universidade: {str(e)}"
        )


# === ENDPOINTS DE GRUPOS VIRTUAIS (RF052) ===
# Grupos não são armazenados em tabela, são gerados dinamicamente

@router.get("/groups/my-university", response_model=UniversityGroupOut)
def get_my_university_group(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **RF052 - Retorna o "grupo virtual" da minha universidade**

    Cada universidade tem um grupo virtual (não armazenado em tabela) onde todos
    os alunos são considerados membros.

    **Regras:**
    - Grupo calculado dinamicamente a partir dos alunos da universidade
    - Não requer criação ou sincronização
    - Retorna 404 se usuário não tem universidade cadastrada
    """
    try:
        user_uuid = UUID(str(current_user.id))

        # Buscar perfil do usuário
        from app.models.supabase_models import ProfileSupabase

        profile = db.query(ProfileSupabase).filter(
            ProfileSupabase.id == user_uuid
        ).first()

        if not profile or not profile.university_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Você ainda não cadastrou sua universidade no perfil"
            )

        group_info = StudentDirectoryService.get_university_group_info(
            db, profile.university_id
        )

        if not group_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo da universidade não encontrado"
            )

        return group_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting university group: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar grupo da universidade: {str(e)}"
        )


@router.get("/groups", response_model=List[UniversityGroupOut])
def list_all_university_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **RF052 - Lista todos os "grupos virtuais" de universidades**

    Retorna lista de todas as universidades com alunos cadastrados.
    Grupos são calculados dinamicamente, não armazenados em tabela.

    **Útil para:**
    - Visualizar todas as universidades representadas na plataforma
    - Ver quantos alunos existem em cada universidade
    - Admin: monitorar distribuição de alunos
    """
    try:
        groups = StudentDirectoryService.get_all_university_groups(db)

        logger.info(f"User {current_user.id} listed {len(groups)} university groups")

        return groups

    except Exception as e:
        logger.error(f"Error listing university groups: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar grupos de universidades: {str(e)}"
        )
