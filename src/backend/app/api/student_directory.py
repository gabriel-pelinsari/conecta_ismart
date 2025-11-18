"""
Rotas da API para o diretório de alunos (Módulo 4: Descoberta e Agrupamento)
ADAPTADO PARA O NOVO SCHEMA LOCAL
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.student_directory import (
    StudentListResponse,
    StudentFilters,
    FilterFacets,
    SuggestionsResponse,
    UniversityPageResponse,
)
from app.services.student_directory import StudentDirectoryService

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
    - Exibe apenas alunos com perfil público (is_public=true)
    - Não exibe o próprio usuário
    - Ordem padrão: aleatória (descoberta)
    - Load inicial: 20 alunos (configurável via limit)
    - Suporta infinite scroll via offset/limit
    - Informações exibidas: foto, nome, universidade, curso, 3 tags principais
    - Status de conexão visível: "not_connected", "pending_sent", "pending_received", "connected"
    """
    try:
        filters = StudentFilters(
            search_name=search_name,
            universities=universities,
            courses=courses,
            interests=interests,
            entry_years=None,
            order_by=order_by,
            offset=offset,
            limit=limit
        )

        result = StudentDirectoryService.get_students_list(
            db=db,
            current_user_id=current_user.id,
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
    - Top 50 interesses/tags mais populares
    - Quantos alunos em cada ano de entrada

    Exemplo de uso na UI:
    ```
    USP (45)
    UNICAMP (30)
    FGV (28)
    ```
    """
    try:
        facets = StudentDirectoryService.get_filter_facets(
            db=db,
            current_user_id=current_user.id
        )

        return facets

    except Exception as e:
        logger.error(f"Error getting filter facets: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar filtros: {str(e)}"
        )


@router.get("/suggestions", response_model=SuggestionsResponse)
def get_suggestions(
    limit: int = Query(10, ge=1, le=50, description="Número máximo de sugestões"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **RF051 - Sugestões de conexão personalizadas**

    Retorna sugestões de alunos compatíveis baseadas em interesses comuns usando
    Jaccard similarity coefficient.

    **Pré-requisitos:**
    - Usuário deve ter pelo menos 3 interesses cadastrados

    **Exemplo de resposta:**
    ```json
    {
      "suggestions": [
        {
          "student": { ... },
          "compatibility_score": 85.5,
          "common_interests": ["Python", "Machine Learning", "Web Dev"],
          "reason": "Vocês compartilham 3 interesse(s) em comum"
        }
      ],
      "total": 12,
      "message": null
    }
    ```
    """
    try:
        result = StudentDirectoryService.get_connection_suggestions(
            db=db,
            user_id=current_user.id,
            limit=limit
        )

        logger.info(f"User {current_user.id} viewed suggestions: {result.total} suggestions")

        return result

    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar sugestões: {str(e)}"
        )


@router.get("/university/{university_name}", response_model=UniversityPageResponse)
def get_university_page(
    university_name: str,
    course_filter: Optional[str] = Query(None, description="Filtrar por curso (opcional)"),
    interests: Optional[List[str]] = Query(None, description="Filtrar por interesses (opcional)"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    limit: int = Query(20, ge=1, le=100, description="Limite de resultados"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **RF053 - Página dedicada por universidade**

    Retorna lista de alunos de uma universidade específica com suporte a filtros.

    **Exemplo:**
    ```
    GET /api/students/university/Universidade%20de%20S%C3%A3o%20Paulo
    ?course_filter=Engenharia de Software
    &interests=Python&interests=JavaScript
    &offset=0&limit=20
    ```
    """
    try:
        result = StudentDirectoryService.get_university_page(
            db=db,
            current_user_id=current_user.id,
            university_name=university_name,
            course_filter=course_filter,
            interest_filter=interests,
            offset=offset,
            limit=limit
        )

        logger.info(
            f"User {current_user.id} viewed {university_name}: "
            f"{result.total} students"
        )

        return result

    except Exception as e:
        logger.error(f"Error getting university page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar universidade: {str(e)}"
        )
