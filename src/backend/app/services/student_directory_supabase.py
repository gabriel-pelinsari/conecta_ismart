"""
Serviços para o diretório de alunos (Módulo 4: Descoberta e Agrupamento)
ADAPTADO PARA O SCHEMA EXISTENTE DO SUPABASE (sem migrations)
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_, text
from typing import List, Optional
import logging
from uuid import UUID

from app.models.supabase_models import (
    ProfileSupabase,
    Connection,
    Interest,
    ProfileInterest,
    University
)
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
        current_user_id: UUID,
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
        # Query base: perfis ativos excluindo o próprio usuário
        query = db.query(ProfileSupabase).filter(
            ProfileSupabase.id != current_user_id,
            ProfileSupabase.show_university_course == True  # Perfis públicos
        ).options(
            joinedload(ProfileSupabase.university)  # Eager load university
        )

        # RF054 - Busca por nome (mínimo 2 caracteres)
        if filters.search_name and len(filters.search_name) >= 2:
            search_pattern = f"%{filters.search_name.lower()}%"
            query = query.filter(
                func.lower(ProfileSupabase.full_name).like(search_pattern)
            )

        # RF048 - Filtro por universidade (OR - múltipla seleção)
        if filters.universities:
            # Buscar IDs das universidades pelos nomes
            university_ids = db.query(University.id).filter(
                University.name.in_(filters.universities)
            ).subquery()
            query = query.filter(ProfileSupabase.university_id.in_(university_ids))

        # RF049 - Filtro por curso (OR - múltipla seleção)
        if filters.courses:
            query = query.filter(ProfileSupabase.course.in_(filters.courses))

        # RF050 - Filtro por interesses comuns
        if filters.interests:
            # Subquery para pegar perfis com pelo menos 1 interesse em comum
            interest_ids = db.query(Interest.id).filter(
                Interest.name.in_(filters.interests)
            ).subquery()

            profile_ids_with_interests = db.query(ProfileInterest.profile_id).filter(
                ProfileInterest.interest_id.in_(interest_ids)
            ).distinct().subquery()

            query = query.filter(ProfileSupabase.id.in_(profile_ids_with_interests))

        # Filtro por ano de entrada
        if filters.entry_years:
            query = query.filter(ProfileSupabase.entry_year.in_(filters.entry_years))

        # Total de resultados (antes da paginação)
        total = query.count()

        # Ordenação
        if filters.order_by == "name":
            query = query.order_by(ProfileSupabase.full_name)
        elif filters.order_by == "recent":
            query = query.order_by(ProfileSupabase.created_at.desc())
        elif filters.order_by == "compatibility":
            # Será implementado com scoring de interesses
            query = query.order_by(ProfileSupabase.full_name)  # Fallback
        else:  # random (padrão)
            query = query.order_by(func.random())

        # Paginação
        profiles = query.offset(filters.offset).limit(filters.limit).all()

        # Converter para StudentCardOut
        students = []
        for profile in profiles:
            # Buscar os 3 principais interesses
            user_interests = db.query(Interest.name).join(ProfileInterest).filter(
                ProfileInterest.profile_id == profile.id
            ).limit(3).all()
            interests_list = [interest.name for interest in user_interests]

            # Verificar status de conexão
            connection_status = StudentDirectoryService._get_connection_status(
                db, current_user_id, profile.id
            )

            # Calcular score de compatibilidade (se filtrou por interesses)
            compatibility_score = None
            if filters.interests:
                compatibility_score = StudentDirectoryService._calculate_compatibility(
                    db, current_user_id, profile.id
                )

            # Nome da universidade
            university_name = profile.university.name if profile.university else None

            students.append(StudentCardOut(
                id=profile.id,
                full_name=profile.full_name,
                nickname=profile.nickname,
                university=university_name,
                course=profile.course,
                entry_year=profile.entry_year,
                photo_url=profile.photo_url,
                interests=interests_list,
                friendship_status=connection_status,
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
    def _get_connection_status(
        db: Session,
        user_id: UUID,
        other_user_id: UUID
    ) -> str:
        """
        Retorna o status de conexão entre dois usuários
        - 'connected': São amigos (status='aceita')
        - 'pending_sent': Solicitação enviada (aguardando aprovação)
        - 'pending_received': Solicitação recebida (pode aceitar)
        - 'not_connected': Não são amigos
        """
        # Verificar se existe connection
        connection = db.query(Connection).filter(
            or_(
                and_(Connection.requester_id == user_id, Connection.addressee_id == other_user_id),
                and_(Connection.requester_id == other_user_id, Connection.addressee_id == user_id)
            )
        ).first()

        if not connection:
            return "not_connected"

        if connection.status == "aceita":
            return "connected"

        if connection.requester_id == user_id:
            return "pending_sent"
        else:
            return "pending_received"

    @staticmethod
    def _calculate_compatibility(
        db: Session,
        user_id: UUID,
        other_user_id: UUID
    ) -> float:
        """
        Calcula score de compatibilidade baseado em interesses comuns
        Retorna valor entre 0-100
        """
        # Interesses do usuário atual
        user_interests = set(
            db.query(Interest.id).join(ProfileInterest).filter(
                ProfileInterest.profile_id == user_id
            ).all()
        )

        # Interesses do outro usuário
        other_interests = set(
            db.query(Interest.id).join(ProfileInterest).filter(
                ProfileInterest.profile_id == other_user_id
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
        current_user_id: UUID,
        applied_filters: Optional[StudentFilters] = None
    ) -> FilterFacets:
        """
        Retorna facets (contadores) para todos os filtros disponíveis
        Útil para UI mostrar quantos alunos existem em cada categoria
        """
        # Query base
        base_query = db.query(ProfileSupabase).filter(
            ProfileSupabase.id != current_user_id,
            ProfileSupabase.show_university_course == True
        )

        # Contar por universidade
        universities = db.query(
            University.name,
            func.count(ProfileSupabase.id).label('count')
        ).join(ProfileSupabase).filter(
            ProfileSupabase.id != current_user_id,
            ProfileSupabase.show_university_course == True,
            ProfileSupabase.university_id.isnot(None)
        ).group_by(University.name).order_by(University.name).all()

        university_facets = [
            FilterFacet(value=univ, count=count)
            for univ, count in universities
        ]

        # Contar por curso
        courses = db.query(
            ProfileSupabase.course,
            func.count(ProfileSupabase.id).label('count')
        ).filter(
            ProfileSupabase.id != current_user_id,
            ProfileSupabase.show_university_course == True,
            ProfileSupabase.course.isnot(None)
        ).group_by(ProfileSupabase.course).order_by(ProfileSupabase.course).all()

        course_facets = [
            FilterFacet(value=course, count=count)
            for course, count in courses
        ]

        # Contar por interesse (top 50 mais populares, apenas aprovados)
        interests = db.query(
            Interest.name,
            func.count(ProfileInterest.profile_id).label('count')
        ).join(ProfileInterest).join(ProfileSupabase).filter(
            ProfileSupabase.id != current_user_id,
            Interest.approved == True  # Apenas interesses aprovados
        ).group_by(Interest.name).order_by(
            func.count(ProfileInterest.profile_id).desc()
        ).limit(50).all()

        interest_facets = [
            FilterFacet(value=interest, count=count)
            for interest, count in interests
        ]

        # Contar por ano de entrada
        entry_years = db.query(
            ProfileSupabase.entry_year,
            func.count(ProfileSupabase.id).label('count')
        ).filter(
            ProfileSupabase.id != current_user_id,
            ProfileSupabase.show_university_course == True,
            ProfileSupabase.entry_year.isnot(None)
        ).group_by(ProfileSupabase.entry_year).order_by(ProfileSupabase.entry_year.desc()).all()

        entry_year_facets = [
            FilterFacet(value=str(year), count=count)
            for year, count in entry_years
        ]

        return FilterFacets(
            universities=university_facets,
            courses=course_facets,
            interests=interest_facets,
            entry_years=entry_year_facets
        )

    @staticmethod
    def get_connection_suggestions(
        db: Session,
        user_id: UUID,
        limit: int = 10
    ) -> SuggestionsResponse:
        """
        RF051 - Sugestões de conexão baseadas em vetorização de interesses
        Usa cosine similarity (Jaccard simplificado) para sugerir alunos compatíveis
        """
        # Verificar se usuário tem pelo menos 3 interesses
        user_interests_count = db.query(ProfileInterest).filter(
            ProfileInterest.profile_id == user_id
        ).count()

        if user_interests_count < 3:
            return SuggestionsResponse(
                suggestions=[],
                total=0,
                message="Complete seu perfil com pelo menos 3 interesses para receber sugestões personalizadas"
            )

        # Buscar interesses do usuário
        user_interest_ids = [
            i.interest_id for i in
            db.query(ProfileInterest.interest_id).filter(
                ProfileInterest.profile_id == user_id
            ).all()
        ]

        # Buscar usuários que NÃO são amigos e têm interesses em comum
        connected_ids = db.query(Connection.addressee_id).filter(
            Connection.requester_id == user_id,
            Connection.status == "aceita"
        ).union(
            db.query(Connection.requester_id).filter(
                Connection.addressee_id == user_id,
                Connection.status == "aceita"
            )
        ).subquery()

        pending_ids = db.query(Connection.addressee_id).filter(
            Connection.requester_id == user_id,
            Connection.status == "pendente"
        ).union(
            db.query(Connection.requester_id).filter(
                Connection.addressee_id == user_id,
                Connection.status == "pendente"
            )
        ).subquery()

        # Candidatos: perfis públicos, não conectados, com interesses em comum
        candidates = db.query(ProfileSupabase).options(
            joinedload(ProfileSupabase.university)
        ).filter(
            ProfileSupabase.id != user_id,
            ProfileSupabase.show_university_course == True,
            ProfileSupabase.id.notin_(connected_ids),
            ProfileSupabase.id.notin_(pending_ids)
        ).all()

        # Calcular score de compatibilidade para cada candidato
        suggestions_data = []
        for candidate in candidates:
            candidate_interests = [
                i.interest_id for i in
                db.query(ProfileInterest.interest_id).filter(
                    ProfileInterest.profile_id == candidate.id
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
                'profile': candidate,
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
            candidate_interest_names = db.query(Interest.name).join(ProfileInterest).filter(
                ProfileInterest.profile_id == profile.id
            ).limit(3).all()
            interests_list = [i.name for i in candidate_interest_names]

            # Gerar motivo da sugestão
            reason = f"Vocês compartilham {data['common_count']} interesse(s) em comum"

            university_name = profile.university.name if profile.university else None

            student_card = StudentCardOut(
                id=profile.id,
                full_name=profile.full_name,
                nickname=profile.nickname,
                university=university_name,
                course=profile.course,
                entry_year=profile.entry_year,
                photo_url=profile.photo_url,
                interests=interests_list,
                friendship_status="not_connected",
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
        current_user_id: UUID,
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
        university_name = university_slug.replace("-", " ").title()

        # Buscar universidade
        university = db.query(University).filter(
            University.name == university_name
        ).first()

        if not university:
            # Tentar buscar case-insensitive
            university = db.query(University).filter(
                func.lower(University.name) == university_name.lower()
            ).first()

        if not university:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Universidade não encontrada")

        # Query base: alunos da universidade
        query = db.query(ProfileSupabase).options(
            joinedload(ProfileSupabase.university)
        ).filter(
            ProfileSupabase.id != current_user_id,
            ProfileSupabase.show_university_course == True,
            ProfileSupabase.university_id == university.id
        )

        # Aplicar filtro por curso
        if course_filter:
            query = query.filter(ProfileSupabase.course == course_filter)

        # Aplicar filtro por interesses
        if interest_filter:
            interest_ids = db.query(Interest.id).filter(
                Interest.name.in_(interest_filter)
            ).subquery()

            profile_ids_with_interests = db.query(ProfileInterest.profile_id).filter(
                ProfileInterest.interest_id.in_(interest_ids)
            ).distinct().subquery()

            query = query.filter(ProfileSupabase.id.in_(profile_ids_with_interests))

        # Total
        total = query.count()

        # Paginação (ordem aleatória por padrão)
        profiles = query.order_by(func.random()).offset(offset).limit(limit).all()

        # Converter para StudentCardOut
        students = []
        for profile in profiles:
            user_interests = db.query(Interest.name).join(ProfileInterest).filter(
                ProfileInterest.profile_id == profile.id
            ).limit(3).all()
            interests_list = [interest.name for interest in user_interests]

            connection_status = StudentDirectoryService._get_connection_status(
                db, current_user_id, profile.id
            )

            students.append(StudentCardOut(
                id=profile.id,
                full_name=profile.full_name,
                nickname=profile.nickname,
                university=university.name,
                course=profile.course,
                entry_year=profile.entry_year,
                photo_url=profile.photo_url,
                interests=interests_list,
                friendship_status=connection_status,
                compatibility_score=None
            ))

        # Buscar cursos disponíveis nesta universidade
        courses_available = db.query(ProfileSupabase.course).filter(
            ProfileSupabase.university_id == university.id,
            ProfileSupabase.course.isnot(None)
        ).distinct().all()
        courses_list = [c[0] for c in courses_available]

        from app.schemas.student_directory import UniversityPageResponse, UniversityStats

        return UniversityPageResponse(
            university=UniversityStats(
                university_name=university.name,
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

    @staticmethod
    def get_university_group_info(db: Session, university_id: int):
        """
        RF052 - Retorna informações do "grupo virtual" de uma universidade
        Não armazena em tabela, calcula dinamicamente
        """
        university = db.query(University).filter(University.id == university_id).first()

        if not university:
            return None

        # Contar membros
        total_members = db.query(ProfileSupabase).filter(
            ProfileSupabase.university_id == university_id,
            ProfileSupabase.show_university_course == True
        ).count()

        from app.schemas.student_directory import UniversityGroupOut

        return UniversityGroupOut(
            university_id=university.id,
            university_name=university.name,
            total_members=total_members,
            description=f"Comunidade de alunos da {university.name} na plataforma ISMART Conecta"
        )

    @staticmethod
    def get_all_university_groups(db: Session):
        """
        RF052 - Lista todos os "grupos virtuais" de universidades
        """
        universities = db.query(University).order_by(University.name).all()

        groups = []
        for university in universities:
            total_members = db.query(ProfileSupabase).filter(
                ProfileSupabase.university_id == university.id,
                ProfileSupabase.show_university_course == True
            ).count()

            if total_members > 0:  # Apenas universidades com alunos
                from app.schemas.student_directory import UniversityGroupOut

                groups.append(UniversityGroupOut(
                    university_id=university.id,
                    university_name=university.name,
                    total_members=total_members,
                    description=f"Comunidade de alunos da {university.name} na plataforma ISMART Conecta"
                ))

        return groups
