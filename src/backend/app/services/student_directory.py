"""
Serviços para o diretório de alunos (Módulo 4: Descoberta e Agrupamento)
ADAPTADO PARA O NOVO SCHEMA LOCAL
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from typing import List, Optional
import logging

from app.models.user import User
from app.models.profile import Profile
from app.models.social import Friendship, Interest, UserInterest
from app.schemas.student_directory import (
    StudentCardOut,
    StudentFilters,
    StudentListResponse,
    FilterFacets,
    FilterFacet,
    SuggestionOut,
    SuggestionsResponse
)

logger = logging.getLogger(__name__)


class StudentDirectoryService:
    """Serviço para descoberta e exploração de alunos"""

    @staticmethod
    def get_students_list(
        db: Session,
        current_user_id: int,
        filters: StudentFilters
    ) -> StudentListResponse:
        """
        RF047 - Página "Explorar" com lista de alunos
        RF048 - Filtro de alunos por universidade
        RF049 - Filtro de alunos por curso
        RF050 - Filtro de alunos por interesses comuns
        RF054 - Busca de alunos por nome
        RF055 - Filtros combinados (múltiplos critérios simultâneos)
        """
        # Query base: perfis ativos excluindo o próprio usuário e apenas públicos
        query = db.query(Profile).filter(
            Profile.user_id != current_user_id,
            Profile.is_public == True  # Apenas perfis públicos
        )

        # RF054 - Busca por nome (mínimo 2 caracteres)
        if filters.search_name and len(filters.search_name) >= 2:
            search_pattern = f"%{filters.search_name.lower()}%"
            query = query.filter(
                func.lower(Profile.full_name).like(search_pattern)
            )

        # RF048 - Filtro por universidade (OR - múltipla seleção)
        if filters.universities:
            query = query.filter(Profile.university.in_(filters.universities))

        # RF049 - Filtro por curso (OR - múltipla seleção)
        if filters.courses:
            query = query.filter(Profile.course.in_(filters.courses))

        # RF050 - Filtro por interesses comuns
        if filters.interests:
            # Subquery para pegar perfis com pelo menos 1 interesse em comum
            interest_ids = db.query(Interest.id).filter(
                Interest.name.in_(filters.interests)
            ).subquery()

            user_ids_with_interests = db.query(UserInterest.user_id).filter(
                UserInterest.interest_id.in_(interest_ids)
            ).distinct().subquery()

            # Join com users para filtrar profiles
            query = query.join(User).filter(
                User.id.in_(user_ids_with_interests)
            )

        # Total de resultados (antes da paginação)
        total = query.count()

        # Ordenação
        if filters.order_by == "name":
            query = query.order_by(Profile.full_name)
        elif filters.order_by == "recent":
            query = query.order_by(Profile.created_at.desc())
        elif filters.order_by == "compatibility":
            # Será implementado com scoring de interesses
            query = query.order_by(Profile.full_name)  # Fallback
        else:  # random (padrão)
            query = query.order_by(func.random())

        # Paginação
        profiles = query.offset(filters.offset).limit(filters.limit).all()

        # Converter para StudentCardOut
        students = []
        for profile in profiles:
            # Buscar os 3 principais interesses
            user_interests = db.query(Interest.name).join(UserInterest).filter(
                UserInterest.user_id == profile.user_id
            ).limit(3).all()
            interests_list = [interest.name for interest in user_interests]

            # Verificar status de amizade
            friendship_status = StudentDirectoryService._get_friendship_status(
                db, current_user_id, profile.user_id
            )

            # Calcular score de compatibilidade (se filtrou por interesses)
            compatibility_score = None
            if filters.interests:
                compatibility_score = StudentDirectoryService._calculate_compatibility(
                    db, current_user_id, profile.user_id
                )

            students.append(StudentCardOut(
                id=profile.user_id,
                full_name=profile.full_name,
                nickname=profile.nickname,
                university=profile.university,
                course=profile.course,
                entry_year=None,  # Não existe no novo schema
                photo_url=profile.photo_url,
                interests=interests_list,
                friendship_status=friendship_status,
                compatibility_score=compatibility_score
            ))

        has_more = (filters.offset + filters.limit) < total

        return StudentListResponse(
            students=students,
            total=total,
            offset=filters.offset,
            limit=filters.limit,
            has_more=has_more
        )

    @staticmethod
    def _get_friendship_status(
        db: Session,
        user_id: int,
        other_user_id: int
    ) -> str:
        """
        Retorna o status de amizade entre dois usuários
        - 'connected': São amigos (status='accepted')
        - 'pending_sent': Solicitação enviada (aguardando aprovação)
        - 'pending_received': Solicitação recebida (pode aceitar)
        - 'not_connected': Não são amigos
        """
        # Verificar se existe friendship
        friendship = db.query(Friendship).filter(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == other_user_id),
                and_(Friendship.user_id == other_user_id, Friendship.friend_id == user_id)
            )
        ).first()

        if not friendship:
            return "not_connected"

        if friendship.status == "accepted":
            return "connected"

        if friendship.user_id == user_id:
            return "pending_sent"
        else:
            return "pending_received"

    @staticmethod
    def _calculate_compatibility(
        db: Session,
        user_id: int,
        other_user_id: int
    ) -> float:
        """
        Calcula score de compatibilidade baseado em interesses comuns
        Retorna valor entre 0-100
        """
        # Interesses do usuário atual
        user_interests = set(
            db.query(UserInterest.interest_id).filter(
                UserInterest.user_id == user_id
            ).all()
        )

        # Interesses do outro usuário
        other_interests = set(
            db.query(UserInterest.interest_id).filter(
                UserInterest.user_id == other_user_id
            ).all()
        )

        if not user_interests or not other_interests:
            return 0.0

        # Calcular interseção e união
        common = len(user_interests.intersection(other_interests))
        total = len(user_interests.union(other_interests))

        # Jaccard similarity * 100
        if total == 0:
            return 0.0

        return round((common / total) * 100, 1)

    @staticmethod
    def get_filter_facets(
        db: Session,
        current_user_id: int,
        applied_filters: Optional[StudentFilters] = None
    ) -> FilterFacets:
        """
        Retorna facets (contadores) para todos os filtros disponíveis
        Útil para UI mostrar quantos alunos existem em cada categoria
        """
        # Query base
        base_query = db.query(Profile).filter(
            Profile.user_id != current_user_id,
            Profile.is_public == True
        )

        # Contar por universidade
        universities = db.query(
            Profile.university,
            func.count(Profile.id).label('count')
        ).filter(
            Profile.user_id != current_user_id,
            Profile.is_public == True,
            Profile.university.isnot(None)
        ).group_by(Profile.university).order_by(Profile.university).all()

        university_facets = [
            FilterFacet(value=univ, count=count)
            for univ, count in universities
        ]

        # Contar por curso
        courses = db.query(
            Profile.course,
            func.count(Profile.id).label('count')
        ).filter(
            Profile.user_id != current_user_id,
            Profile.is_public == True,
            Profile.course.isnot(None)
        ).group_by(Profile.course).order_by(Profile.course).all()

        course_facets = [
            FilterFacet(value=course, count=count)
            for course, count in courses
        ]

        # Contar por interesse (top 50 mais populares)
        interests = db.query(
            Interest.name,
            func.count(UserInterest.user_id).label('count')
        ).join(UserInterest).join(User).join(Profile).filter(
            Profile.user_id != current_user_id,
            Profile.is_public == True
        ).group_by(Interest.name).order_by(
            func.count(UserInterest.user_id).desc()
        ).limit(50).all()

        interest_facets = [
            FilterFacet(value=interest, count=count)
            for interest, count in interests
        ]

        return FilterFacets(
            universities=university_facets,
            courses=course_facets,
            interests=interest_facets,
            entry_years=[]  # Não existe no novo schema
        )

    @staticmethod
    def get_university_page(
        db: Session,
        current_user_id: int,
        university_name: str,
        course_filter: Optional[str] = None,
        interest_filter: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20
    ):
        """
        RF053 - Página dedicada por universidade listando todos os alunos
        """
        # Query base: alunos da universidade
        query = db.query(Profile).filter(
            Profile.user_id != current_user_id,
            Profile.is_public == True,
            Profile.university == university_name
        )

        # Aplicar filtro por curso
        if course_filter:
            query = query.filter(Profile.course == course_filter)

        # Aplicar filtro por interesses
        if interest_filter:
            interest_ids = db.query(Interest.id).filter(
                Interest.name.in_(interest_filter)
            ).subquery()

            user_ids_with_interests = db.query(UserInterest.user_id).filter(
                UserInterest.interest_id.in_(interest_ids)
            ).distinct().subquery()

            query = query.join(User).filter(
                User.id.in_(user_ids_with_interests)
            )

        # Total
        total = query.count()

        # Paginação (ordem aleatória por padrão)
        profiles = query.order_by(func.random()).offset(offset).limit(limit).all()

        # Converter para StudentCardOut
        students = []
        for profile in profiles:
            user_interests = db.query(Interest.name).join(UserInterest).filter(
                UserInterest.user_id == profile.user_id
            ).limit(3).all()
            interests_list = [interest.name for interest in user_interests]

            friendship_status = StudentDirectoryService._get_friendship_status(
                db, current_user_id, profile.user_id
            )

            students.append(StudentCardOut(
                id=profile.user_id,
                full_name=profile.full_name,
                nickname=profile.nickname,
                university=profile.university,
                course=profile.course,
                entry_year=None,  # Não existe no novo schema
                photo_url=profile.photo_url,
                interests=interests_list,
                friendship_status=friendship_status,
                compatibility_score=None
            ))

        # Buscar cursos disponíveis nesta universidade
        courses_available = db.query(Profile.course).filter(
            Profile.university == university_name,
            Profile.course.isnot(None),
            Profile.is_public == True
        ).distinct().all()
        courses_list = [c[0] for c in courses_available]

        from app.schemas.student_directory import UniversityPageResponse, UniversityStats

        return UniversityPageResponse(
            university=UniversityStats(
                university_name=university_name,
                slug=university_name.lower().replace(" ", "-"),
                total_students=total,
                courses_available=courses_list
            ),
            students=students,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total
        )

    @staticmethod
    def get_connection_suggestions(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> SuggestionsResponse:
        """
        RF051 - Sugestões de conexão personalizadas baseadas em interesses comuns

        Algoritmo:
        1. Buscar interesses do usuário atual
        2. Encontrar outros usuários com interesses em comum
        3. Calcular score de compatibilidade (Jaccard similarity)
        4. Ordenar por score de compatibilidade (descending)
        5. Retornar top N sugestões

        Regras:
        - Não sugerir amigos existentes (status='accepted')
        - Não sugerir solicitações já enviadas (pending_sent)
        - Não sugerir o próprio usuário
        - Apenas perfis públicos
        - Usuário deve ter pelo menos 1 interesse para sugestões
        """
        # Buscar interesses do usuário atual
        user_interests = db.query(UserInterest.interest_id).filter(
            UserInterest.user_id == user_id
        ).all()

        user_interest_ids = set([ui[0] for ui in user_interests])

        if not user_interest_ids:
            return SuggestionsResponse(
                suggestions=[],
                total=0,
                message="Complete seu perfil com mais interesses para receber sugestões"
            )

        # Query base: perfis públicos, não o próprio usuário
        profiles = db.query(Profile).filter(
            Profile.user_id != user_id,
            Profile.is_public == True
        ).all()

        suggestions_data = []

        for profile in profiles:
            # Buscar interesses do outro usuário
            other_interests = db.query(UserInterest.interest_id).filter(
                UserInterest.user_id == profile.user_id
            ).all()

            other_interest_ids = set([oi[0] for oi in other_interests])

            if not other_interest_ids:
                continue

            # Calcular interesses em comum
            common_interests_ids = user_interest_ids.intersection(other_interest_ids)

            if not common_interests_ids:
                continue

            # Calcular Jaccard similarity
            compatibility_score = StudentDirectoryService._calculate_compatibility(
                db, user_id, profile.user_id
            )

            # Buscar nomes dos interesses em comum
            common_interest_names = db.query(Interest.name).filter(
                Interest.id.in_(common_interests_ids)
            ).all()
            common_interests_list = [i[0] for i in common_interest_names]

            # Verificar se já são amigos ou há solicitação pendente
            friendship = db.query(Friendship).filter(
                or_(
                    and_(Friendship.user_id == user_id, Friendship.friend_id == profile.user_id),
                    and_(Friendship.user_id == profile.user_id, Friendship.friend_id == user_id)
                )
            ).first()

            # Não sugerir amigos ou solicitações pendentes do usuário
            if friendship and (friendship.status == "accepted" or
                              (friendship.user_id == user_id and friendship.status == "pending")):
                continue

            # Buscar interesses do perfil (para StudentCardOut)
            profile_interests = db.query(Interest.name).join(UserInterest).filter(
                UserInterest.user_id == profile.user_id
            ).limit(3).all()
            interests_list = [i[0] for i in profile_interests]

            # Buscar status de amizade
            friendship_status = StudentDirectoryService._get_friendship_status(
                db, user_id, profile.user_id
            )

            suggestions_data.append({
                "student": StudentCardOut(
                    id=profile.user_id,
                    full_name=profile.full_name,
                    nickname=profile.nickname,
                    university=profile.university,
                    course=profile.course,
                    entry_year=None,
                    photo_url=profile.photo_url,
                    interests=interests_list,
                    friendship_status=friendship_status,
                    compatibility_score=compatibility_score
                ),
                "compatibility_score": compatibility_score,
                "common_interests": common_interests_list,
                "reason": f"Vocês compartilham {len(common_interests_list)} interesse(s) em comum"
            })

        # Ordenar por score de compatibilidade (descending)
        suggestions_data.sort(key=lambda x: x["compatibility_score"], reverse=True)

        # Limitar resultados
        suggestions_data = suggestions_data[:limit]

        # Converter para SuggestionOut
        from app.schemas.student_directory import SuggestionOut
        suggestions = [
            SuggestionOut(**item) for item in suggestions_data
        ]

        message = None
        if not suggestions:
            message = "Nenhuma sugestão disponível no momento. Explore mais alunos!"

        return SuggestionsResponse(
            suggestions=suggestions,
            total=len(suggestions),
            message=message
        )
