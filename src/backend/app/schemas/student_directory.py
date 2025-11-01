"""
Schemas para o diretório de alunos (Módulo 4: Descoberta e Agrupamento)
Adaptado para usar UUID (schema Supabase existente)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# === SCHEMAS DE INTERESSE ===
class InterestBase(BaseModel):
    name: str


class InterestOut(InterestBase):
    id: int

    class Config:
        from_attributes = True


# === SCHEMAS DE ALUNO (STUDENT CARD) ===
class StudentCardOut(BaseModel):
    """Schema para exibir cards de alunos na página Explorar"""
    id: UUID
    full_name: str
    nickname: Optional[str] = None
    university: Optional[str] = None  # Nome da universidade (via relationship)
    course: Optional[str] = None
    entry_year: Optional[int] = None  # Substituindo "semester"
    photo_url: Optional[str] = None
    interests: List[str] = Field(default_factory=list, description="Top 3 interesses principais")
    friendship_status: Optional[str] = Field(
        default=None,
        description="Status: 'not_connected', 'pending_sent', 'pending_received', 'connected'"
    )
    compatibility_score: Optional[float] = Field(
        default=None,
        description="Score de compatibilidade baseado em interesses (0-100%)"
    )

    class Config:
        from_attributes = True


# === SCHEMAS DE FILTROS ===
class StudentFilters(BaseModel):
    """Filtros para busca e descoberta de alunos (RF055 - Filtros combinados)"""
    # RF054 - Busca por nome
    search_name: Optional[str] = Field(None, description="Busca por nome (case-insensitive, mínimo 2 caracteres)")

    # RF048 - Filtro por universidade
    universities: Optional[List[str]] = Field(None, description="Lista de universidades (OR)")

    # RF049 - Filtro por curso
    courses: Optional[List[str]] = Field(None, description="Lista de cursos (OR)")

    # RF050 - Filtro por interesses
    interests: Optional[List[str]] = Field(None, description="Lista de interesses/tags (OR)")

    # Filtro adicional por ano de entrada
    entry_years: Optional[List[int]] = Field(None, description="Lista de anos de entrada (OR)")

    # Ordenação
    order_by: Optional[str] = Field(
        default="random",
        description="Ordenação: 'random', 'name', 'compatibility', 'recent'"
    )

    # Paginação
    offset: int = Field(default=0, ge=0, description="Offset para paginação")
    limit: int = Field(default=20, ge=1, le=100, description="Limite de resultados (max 100)")


class StudentListResponse(BaseModel):
    """Resposta da listagem de alunos com metadados"""
    students: List[StudentCardOut]
    total: int = Field(description="Total de alunos que correspondem aos filtros")
    offset: int
    limit: int
    has_more: bool = Field(description="Se há mais resultados disponíveis")


# === SCHEMAS DE SUGESTÕES (RF051) ===
class SuggestionOut(BaseModel):
    """Sugestão de conexão baseada em vetorização de interesses"""
    student: StudentCardOut
    compatibility_score: float = Field(description="Score de compatibilidade (0-100%)")
    common_interests: List[str] = Field(description="Interesses em comum")
    reason: str = Field(description="Motivo da sugestão")

    class Config:
        from_attributes = True


class SuggestionsResponse(BaseModel):
    """Resposta de sugestões de conexão"""
    suggestions: List[SuggestionOut]
    total: int
    message: Optional[str] = Field(
        default=None,
        description="Mensagem informativa (ex: 'Complete seu perfil com mais tags')"
    )


# === SCHEMAS DE UNIVERSIDADE (RF053) ===
class UniversityStats(BaseModel):
    """Estatísticas de uma universidade"""
    university_name: str
    slug: str
    total_students: int
    courses_available: List[str] = Field(description="Cursos disponíveis nesta universidade")


class UniversityPageResponse(BaseModel):
    """Resposta da página dedicada de uma universidade"""
    university: UniversityStats
    students: List[StudentCardOut]
    total: int
    offset: int
    limit: int
    has_more: bool


# === SCHEMAS DE GRUPOS (RF052) ===
# NOTA: Grupos não são armazenados no banco, são gerados dinamicamente
class UniversityGroupOut(BaseModel):
    """Grupo virtual por universidade (não armazenado em tabela)"""
    university_id: int
    university_name: str
    total_members: int
    description: str = "Comunidade de alunos desta universidade"

    class Config:
        from_attributes = True


# === SCHEMAS DE CONTADORES/FACETS ===
class FilterFacet(BaseModel):
    """Facet para filtros com contador"""
    value: str
    count: int
    is_selected: bool = False


class FilterFacets(BaseModel):
    """Facets disponíveis para todos os filtros"""
    universities: List[FilterFacet] = Field(description="Universidades com contador de alunos")
    courses: List[FilterFacet] = Field(description="Cursos com contador de alunos")
    interests: List[FilterFacet] = Field(description="Interesses/tags populares com contador")
    entry_years: List[FilterFacet] = Field(description="Anos de entrada com contador de alunos")
