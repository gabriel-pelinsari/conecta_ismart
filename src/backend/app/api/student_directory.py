"""
Rotas da API para o diretório de alunos (Módulo 4: Descoberta e Agrupamento)
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
    UniversityPageResponse
)
from app.services.student_directory import StudentDirectoryService
from app.services.university_groups import UniversityGroupService
from app.schemas.student_directory import UniversityGroupOut

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

    # Filtro adicional por semestre
    semesters: Optional[List[str]] = Query(None, description="Filtrar por semestre(s)"),

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
    - Exibe apenas alunos ativos e com perfil público
    - Não exibe o próprio usuário
    - Ordem padrão: aleatória (descoberta)
    - Load inicial: 20 alunos (configurável via limit)
    - Suporta infinite scroll via offset/limit
    - Informações exibidas: foto, nome, universidade, curso, semestre, 3 tags principais
    - Status de amizade visível: "not_friends", "pending_sent", "pending_received", "friends"
    """
    try:
        filters = StudentFilters(
            search_name=search_name,
            universities=universities,
            courses=courses,
            interests=interests,
            semesters=semesters,
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
            detail="Erro ao buscar alunos"
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
    - Quantos alunos em cada semestre

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
            detail="Erro ao buscar facets de filtros"
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
    - Mínimo 3 tags no perfil para gerar sugestões
    - Não sugere alunos já amigos ou com solicitação pendente
    - Limite: até 50 sugestões por vez
    - Exibe score de compatibilidade (0-100%)
    - Mostra interesses em comum

    **Resposta:**
    - Lista ordenada por compatibilidade (maior primeiro)
    - Cada sugestão inclui: aluno, score, interesses comuns, motivo
    - Se < 3 tags: retorna mensagem "Complete seu perfil..."
    """
    try:
        suggestions = StudentDirectoryService.get_connection_suggestions(
            db=db,
            user_id=current_user.id,
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
            detail="Erro ao buscar sugestões de conexão"
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
    - Exibe foto, nome, curso, semestre, tags de cada aluno da universidade
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
        result = StudentDirectoryService.get_university_page(
            db=db,
            current_user_id=current_user.id,
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

    except Exception as e:
        logger.error(f"Error getting university page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar página da universidade"
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
        # Buscar universidade do usuário atual
        from app.models.profile import Profile

        profile = db.query(Profile).filter(
            Profile.user_id == current_user.id
        ).first()

        if not profile or not profile.university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Você ainda não cadastrou sua universidade no perfil"
            )

        # Converter nome para slug
        university_slug = profile.university.lower().replace(" ", "-")

        result = StudentDirectoryService.get_university_page(
            db=db,
            current_user_id=current_user.id,
            university_slug=university_slug,
            course_filter=None,
            interest_filter=None,
            offset=offset,
            limit=limit
        )

        logger.info(
            f"User {current_user.id} viewed their university page: {profile.university}"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting my university: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar alunos da sua universidade"
        )


# === ENDPOINTS DE GRUPOS AUTOMÁTICOS (RF052) ===

@router.get("/groups/my-university", response_model=UniversityGroupOut)
def get_my_university_group(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **RF052 - Retorna o grupo automático da minha universidade**

    Cada universidade tem um grupo automático onde todos os alunos são membros.

    **Regras:**
    - Grupo criado automaticamente quando primeiro aluno se cadastra
    - Todos os alunos da universidade são membros automaticamente
    - Nome padrão: "[Nome da Universidade] - Comunidade ISMART"
    - Retorna 404 se usuário não tem universidade cadastrada
    """
    try:
        group = UniversityGroupService.get_user_group(db, current_user.id)

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Você ainda não cadastrou sua universidade ou o grupo não foi criado"
            )

        # Contar membros
        member_count = UniversityGroupService.get_group_members_count(db, group.id)

        return UniversityGroupOut(
            id=group.id,
            name=group.name,
            description=group.description,
            university_name=group.university_name,
            total_members=member_count,
            created_at=group.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting university group: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar grupo da universidade"
        )


@router.get("/groups", response_model=List[UniversityGroupOut])
def list_all_university_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **RF052 - Lista todos os grupos de universidades**

    Retorna lista de todos os grupos automáticos criados no sistema.

    **Útil para:**
    - Visualizar todas as universidades representadas na plataforma
    - Ver quantos alunos existem em cada universidade
    - Admin: monitorar distribuição de alunos
    """
    try:
        groups_data = UniversityGroupService.get_all_groups_with_stats(db)

        groups = [
            UniversityGroupOut(
                id=g["id"],
                name=g["name"],
                description=g["description"],
                university_name=g["university_name"],
                total_members=g["member_count"],
                created_at=g["created_at"]
            )
            for g in groups_data
        ]

        logger.info(f"User {current_user.id} listed {len(groups)} university groups")

        return groups

    except Exception as e:
        logger.error(f"Error listing university groups: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar grupos de universidades"
        )


@router.post("/groups/sync-all", status_code=status.HTTP_200_OK)
def sync_all_university_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **[ADMIN] Sincronizar todos os grupos de universidades**

    Cria grupos para todas as universidades e adiciona todos os alunos aos seus
    respectivos grupos automaticamente.

    **Útil para:**
    - Popular grupos inicialmente após migration
    - Corrigir inconsistências
    - Adicionar alunos que não foram adicionados automaticamente

    **Requer:** Usuário admin
    """
    try:
        # Verificar se é admin
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem sincronizar grupos"
            )

        result = UniversityGroupService.sync_all_users(db)

        logger.info(
            f"Admin {current_user.id} synced university groups: {result}"
        )

        return {
            "message": "Sincronização concluída com sucesso",
            "groups_created": result["groups_created"],
            "users_added": result["users_added"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing university groups: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao sincronizar grupos"
        )
