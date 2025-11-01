"""
Serviços para o diretório de alunos (Módulo 4: Descoberta e Agrupamento)
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, case, text
from typing import List, Optional, Tuple
import logging
from collections import Counter
import math

from app.models.user import User
from app.models.profile import Profile
from app.models.social import Friendship, UserInterest, Interest
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
        # Query base: usuários ativos com perfil público
        query = db.query(Profile).join(User).filter(
            User.is_active == True,
            User.id != current_user_id,  # Não mostrar o próprio usuário
            Profile.is_public == True
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
            # Subquery para pegar usuários com pelo menos 1 interesse em comum
            interest_ids = db.query(Interest.id).filter(
                Interest.name.in_(filters.interests)
            ).subquery()

            user_ids_with_interests = db.query(UserInterest.user_id).filter(
                UserInterest.interest_id.in_(interest_ids)
            ).distinct().subquery()

            query = query.filter(Profile.user_id.in_(user_ids_with_interests))

        # Filtro por semestre
        if filters.semesters:
            query = query.filter(Profile.semester.in_(filters.semesters))

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
                semester=profile.semester,
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
        - 'friends': São amigos
        - 'pending_sent': Solicitação enviada (aguardando aprovação)
        - 'pending_received': Solicitação recebida (pode aceitar)
        - 'not_friends': Não são amigos
        """
        # Verificar se existe friendship
        friendship = db.query(Friendship).filter(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == other_user_id),
                and_(Friendship.user_id == other_user_id, Friendship.friend_id == user_id)
            )
        ).first()

        if not friendship:
            return "not_friends"

        if friendship.status == "accepted":
            return "friends"

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
            db.query(Interest.id).join(UserInterest).filter(
                UserInterest.user_id == user_id
            ).all()
        )

        # Interesses do outro usuário
        other_interests = set(
            db.query(Interest.id).join(UserInterest).filter(
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
        base_query = db.query(Profile).join(User).filter(
            User.is_active == True,
            User.id != current_user_id,
            Profile.is_public == True
        )

        # Contar por universidade
        universities = db.query(
            Profile.university,
            func.count(Profile.id).label('count')
        ).join(User).filter(
            User.is_active == True,
            User.id != current_user_id,
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
        ).join(User).filter(
            User.is_active == True,
            User.id != current_user_id,
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
        ).join(UserInterest).join(User).filter(
            User.is_active == True,
            User.id != current_user_id
        ).group_by(Interest.name).order_by(
            func.count(UserInterest.user_id).desc()
        ).limit(50).all()

        interest_facets = [
            FilterFacet(value=interest, count=count)
            for interest, count in interests
        ]

        # Contar por semestre
        semesters = db.query(
            Profile.semester,
            func.count(Profile.id).label('count')
        ).join(User).filter(
            User.is_active == True,
            User.id != current_user_id,
            Profile.is_public == True,
            Profile.semester.isnot(None)
        ).group_by(Profile.semester).order_by(Profile.semester).all()

        semester_facets = [
            FilterFacet(value=semester, count=count)
            for semester, count in semesters
        ]

        return FilterFacets(
            universities=university_facets,
            courses=course_facets,
            interests=interest_facets,
            semesters=semester_facets
        )

    @staticmethod
    def get_connection_suggestions(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> SuggestionsResponse:
        """
        RF051 - Sugestões de conexão baseadas em vetorização de interesses
        Usa cosine similarity (Jaccard simplificado) para sugerir alunos compatíveis
        """
        # Verificar se usuário tem pelo menos 3 tags
        user_interests_count = db.query(UserInterest).filter(
            UserInterest.user_id == user_id
        ).count()

        if user_interests_count < 3:
            return SuggestionsResponse(
                suggestions=[],
                total=0,
                message="Complete seu perfil com pelo menos 3 tags para receber sugestões personalizadas"
            )

        # Buscar interesses do usuário
        user_interest_ids = [
            i.interest_id for i in
            db.query(UserInterest.interest_id).filter(
                UserInterest.user_id == user_id
            ).all()
        ]

        # Buscar usuários que NÃO são amigos e têm interesses em comum
        friends_ids = db.query(Friendship.friend_id).filter(
            Friendship.user_id == user_id,
            Friendship.status == "accepted"
        ).union(
            db.query(Friendship.user_id).filter(
                Friendship.friend_id == user_id,
                Friendship.status == "accepted"
            )
        ).subquery()

        pending_ids = db.query(Friendship.friend_id).filter(
            Friendship.user_id == user_id,
            Friendship.status == "pending"
        ).union(
            db.query(Friendship.user_id).filter(
                Friendship.friend_id == user_id,
                Friendship.status == "pending"
            )
        ).subquery()

        # Candidatos: usuários ativos, públicos, não amigos, com interesses em comum
        candidates = db.query(Profile).join(User).filter(
            User.is_active == True,
            User.id != user_id,
            Profile.is_public == True,
            Profile.user_id.notin_(friends_ids),
            Profile.user_id.notin_(pending_ids)
        ).all()

        # Calcular score de compatibilidade para cada candidato
        suggestions_data = []
        for candidate_profile in candidates:
            candidate_interests = [
                i.interest_id for i in
                db.query(UserInterest.interest_id).filter(
                    UserInterest.user_id == candidate_profile.user_id
                ).all()
            ]

            # Calcular interesses em comum
            common = set(user_interest_ids).intersection(set(candidate_interests))
            if not common:
                continue  # Pular se não tem nada em comum

            # Jaccard similarity
            total = len(set(user_interest_ids).union(set(candidate_interests)))
            score = (len(common) / total) * 100 if total > 0 else 0

            # Buscar nomes dos interesses em comum
            common_interest_names = db.query(Interest.name).filter(
                Interest.id.in_(common)
            ).limit(5).all()
            common_names = [name[0] for name in common_interest_names]

            suggestions_data.append({
                'profile': candidate_profile,
                'score': score,
                'common_interests': common_names,
                'common_count': len(common)
            })

        # Ordenar por score (descendente)
        suggestions_data.sort(key=lambda x: x['score'], reverse=True)

        # Limitar resultados
        suggestions_data = suggestions_data[:limit]

        # Converter para SuggestionOut
        suggestions = []
        for data in suggestions_data:
            profile = data['profile']

            # Buscar top 3 interesses do candidato
            candidate_interest_names = db.query(Interest.name).join(UserInterest).filter(
                UserInterest.user_id == profile.user_id
            ).limit(3).all()
            interests_list = [i.name for i in candidate_interest_names]

            # Gerar motivo da sugestão
            reason = f"Vocês compartilham {data['common_count']} interesse(s) em comum"

            student_card = StudentCardOut(
                id=profile.user_id,
                full_name=profile.full_name,
                nickname=profile.nickname,
                university=profile.university,
                course=profile.course,
                semester=profile.semester,
                photo_url=profile.photo_url,
                interests=interests_list,
                friendship_status="not_friends",
                compatibility_score=data['score']
            )

            suggestions.append(SuggestionOut(
                student=student_card,
                compatibility_score=data['score'],
                common_interests=data['common_interests'],
                reason=reason
            ))

        return SuggestionsResponse(
            suggestions=suggestions,
            total=len(suggestions),
            message=None
        )

    @staticmethod
    def get_university_page(
        db: Session,
        current_user_id: int,
        university_slug: str,
        course_filter: Optional[str] = None,
        interest_filter: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20
    ):
        """
        RF053 - Página dedicada por universidade listando todos os alunos
        """
        # Normalizar slug para nome de universidade
        # (assumindo que slug é o nome da universidade normalizado)
        university_name = university_slug.replace("-", " ").title()

        # Query base: alunos da universidade
        query = db.query(Profile).join(User).filter(
            User.is_active == True,
            User.id != current_user_id,
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

            query = query.filter(Profile.user_id.in_(user_ids_with_interests))

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
                semester=profile.semester,
                photo_url=profile.photo_url,
                interests=interests_list,
                friendship_status=friendship_status,
                compatibility_score=None
            ))

        # Buscar cursos disponíveis nesta universidade
        courses_available = db.query(Profile.course).filter(
            Profile.university == university_name,
            Profile.course.isnot(None)
        ).distinct().all()
        courses_list = [c[0] for c in courses_available]

        from app.schemas.student_directory import UniversityPageResponse, UniversityStats

        return UniversityPageResponse(
            university=UniversityStats(
                university_name=university_name,
                slug=university_slug,
                total_students=total,
                courses_available=courses_list
            ),
            students=students,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total
        )
