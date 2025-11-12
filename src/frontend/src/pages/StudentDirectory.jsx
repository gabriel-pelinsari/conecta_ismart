import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";
import api from "../api/axios";
import { FiSearch, FiX, FiChevronLeft, FiChevronRight } from "react-icons/fi";

const Wrap = styled.main`
  min-height: 100vh;
  padding: 80px 24px 40px 24px;
  background: ${({ theme }) => theme.colors.bg};
`;

const Container = styled.div`
  width: ${({ theme }) => theme.sizes.containerLarge};
  max-width: 100%;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 16px;
`;

const FiltersSection = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.lg};
  padding: 24px;
  margin-bottom: 32px;
`;

const FiltersRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 300px 300px;
  gap: 16px;
  align-items: end;

  @media (max-width: 968px) {
    grid-template-columns: 1fr;
  }
`;

const SearchInputWrapper = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`;

const SearchIcon = styled(FiSearch)`
  position: absolute;
  left: 16px;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 20px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px 12px 48px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  font-size: 15px;
  background: ${({ theme }) => theme.colors.bg};
  color: ${({ theme }) => theme.colors.text};

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
  }

  &::placeholder {
    color: ${({ theme }) => theme.colors.textMuted};
  }
`;

const FilterGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const FilterLabel = styled.label`
  font-size: 13px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.textMuted};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  font-size: 15px;
  background: ${({ theme }) => theme.colors.bg};
  color: ${({ theme }) => theme.colors.text};
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
  }

  option {
    background: ${({ theme }) => theme.colors.surface};
  }
`;

const ActiveFilters = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 16px;
`;

const FilterChip = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: ${({ theme }) => theme.colors.primary}20;
  color: ${({ theme }) => theme.colors.primary};
  padding: 6px 12px;
  border-radius: ${({ theme }) => theme.radii.full};
  font-size: 13px;
  font-weight: 500;

  button {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 0;
    font-size: 16px;

    &:hover {
      opacity: 0.7;
    }
  }
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const ResultsCount = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 15px;
`;

const StudentsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const StudentCard = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.lg};
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
  }
`;

const Avatar = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: ${({ $url, theme }) =>
    $url ? `url(${$url})` : theme.colors.outline};
  background-size: cover;
  background-position: center;
  margin-bottom: 16px;
  border: 3px solid ${({ theme }) => theme.colors.outline};
`;

const StudentName = styled.h3`
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const StudentInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
`;

const InfoItem = styled.p`
  margin: 0;
  font-size: 13px;
  color: ${({ theme }) => theme.colors.textMuted};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
`;

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
`;

const PageButton = styled.button`
  padding: 10px 16px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme, $active }) =>
    $active ? theme.colors.primary : theme.colors.surface};
  color: ${({ theme, $active }) =>
    $active ? "white" : theme.colors.text};
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover:not(:disabled) {
    background: ${({ theme, $active }) =>
      $active ? theme.colors.primary : theme.colors.outline};
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
`;

const PageInfo = styled.span`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 14px;
`;

const LoadingState = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 0;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 16px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: ${({ theme }) => theme.colors.textMuted};

  h3 {
    font-size: 20px;
    margin-bottom: 8px;
    color: ${({ theme }) => theme.colors.text};
  }

  p {
    font-size: 15px;
  }
`;

// Modal para detalhes do aluno
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radii.lg};
  padding: 32px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  color: ${({ theme }) => theme.colors.textMuted};
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: ${({ theme }) => theme.radii.md};

  &:hover {
    background: ${({ theme }) => theme.colors.outline};
  }
`;

const ModalHeader = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.outline};
`;

const ModalAvatar = styled.div`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: ${({ $url, theme }) =>
    $url ? `url(${$url})` : theme.colors.outline};
  background-size: cover;
  background-position: center;
  margin-bottom: 16px;
  border: 4px solid ${({ theme }) => theme.colors.outline};
`;

const ModalName = styled.h2`
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 700;
`;

const ModalSection = styled.div`
  margin-bottom: 20px;

  h3 {
    font-size: 14px;
    font-weight: 600;
    color: ${({ theme }) => theme.colors.textMuted};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
  }

  p {
    margin: 8px 0;
    font-size: 15px;
    color: ${({ theme }) => theme.colors.text};
  }
`;

const InterestsTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
`;

const Tag = styled.span`
  background: ${({ theme }) => theme.colors.primary}20;
  color: ${({ theme }) => theme.colors.primary};
  padding: 6px 12px;
  border-radius: ${({ theme }) => theme.radii.full};
  font-size: 13px;
  font-weight: 500;
`;

const ViewProfileButton = styled.button`
  width: 100%;
  padding: 14px;
  background: ${({ theme }) => theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${({ theme }) => theme.radii.md};
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 24px;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryDark};
    transform: translateY(-1px);
  }
`;

export default function StudentDirectory() {
  const navigate = useNavigate();
  
  // Estados
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUniversity, setSelectedUniversity] = useState("");
  const [selectedCourse, setSelectedCourse] = useState("");
  
  // Opções de filtros disponíveis
  const [universities, setUniversities] = useState([]);
  const [courses, setCourses] = useState([]);
  
  // Paginação
  const [currentPage, setCurrentPage] = useState(1);
  const [totalStudents, setTotalStudents] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const studentsPerPage = 12;
  
  // Modal
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadFilterOptions();
  }, []);

  useEffect(() => {
    loadStudents();
  }, [currentPage, searchTerm, selectedUniversity, selectedCourse]);

  async function loadFilterOptions() {
    try {
      const token = localStorage.getItem("token");
      
      // Carregar facets de filtros
      const response = await api.get("/api/students/explore/facets", {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      const facets = response.data;
      
      // Extrair universidades e cursos únicos
      setUniversities(facets.universities.map(f => f.value));
      setCourses(facets.courses.map(f => f.value));
      
      console.log("✅ Filtros carregados:", {
        universities: facets.universities.length,
        courses: facets.courses.length
      });
    } catch (err) {
      console.error("❌ Erro ao carregar filtros:", err);
    }
  }

  async function loadStudents() {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      
      // Construir query params
      const params = new URLSearchParams({
        offset: (currentPage - 1) * studentsPerPage,
        limit: studentsPerPage,
        order_by: "random", // Priorizar mesma universidade
      });
      
      if (searchTerm && searchTerm.length >= 2) {
        params.append("search_name", searchTerm);
      }
      
      if (selectedUniversity) {
        params.append("universities", selectedUniversity);
      }
      
      if (selectedCourse) {
        params.append("courses", selectedCourse);
      }
      
      const response = await api.get(`/api/students/explore?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      setStudents(response.data.students);
      setTotalStudents(response.data.total);
      setHasMore(response.data.has_more);
      
      console.log(`✅ ${response.data.students.length} alunos carregados (página ${currentPage})`);
    } catch (err) {
      console.error("❌ Erro ao carregar alunos:", err);
      setError("Erro ao carregar alunos");
    } finally {
      setLoading(false);
    }
  }

  async function loadStudentDetails(userId) {
    try {
      const token = localStorage.getItem("token");
      const response = await api.get(`/profiles/public/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      setSelectedStudent(response.data);
      setShowModal(true);
      
      console.log("✅ Detalhes do aluno carregados:", userId);
    } catch (err) {
      console.error("❌ Erro ao carregar detalhes do aluno:", err);
    }
  }

  function handleRemoveFilter(filterType) {
    if (filterType === "university") {
      setSelectedUniversity("");
    } else if (filterType === "course") {
      setSelectedCourse("");
    } else if (filterType === "search") {
      setSearchTerm("");
    }
    setCurrentPage(1);
  }

  function handleCardClick(student) {
    loadStudentDetails(student.id);
  }

  function handleCloseModal() {
    setShowModal(false);
    setSelectedStudent(null);
  }

  function handleViewFullProfile(userId) {
    navigate(`/profile/${userId}`);
  }

  const totalPages = Math.ceil(totalStudents / studentsPerPage);
  const hasActiveFilters = searchTerm || selectedUniversity || selectedCourse;

  if (error) {
    return (
      <Wrap>
        <Container>
          <Title>{error}</Title>
        </Container>
      </Wrap>
    );
  }

  return (
    <Wrap>
      <Container>
        <Header>
          <Title>Diretório de Alunos</Title>
          <Subtitle>Encontre e conecte-se com outros alunos ISMART</Subtitle>
        </Header>

        <FiltersSection>
          <FiltersRow>
            <SearchInputWrapper>
              <SearchIcon />
              <SearchInput
                type="text"
                placeholder="Buscar por nome..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
              />
            </SearchInputWrapper>

            <FilterGroup>
              <FilterLabel>Faculdade</FilterLabel>
              <Select
                value={selectedUniversity}
                onChange={(e) => {
                  setSelectedUniversity(e.target.value);
                  setCurrentPage(1);
                }}
              >
                <option value="">Todas as faculdades</option>
                {universities.map((uni) => (
                  <option key={uni} value={uni}>
                    {uni}
                  </option>
                ))}
              </Select>
            </FilterGroup>

            <FilterGroup>
              <FilterLabel>Curso</FilterLabel>
              <Select
                value={selectedCourse}
                onChange={(e) => {
                  setSelectedCourse(e.target.value);
                  setCurrentPage(1);
                }}
              >
                <option value="">Todos os cursos</option>
                {courses.map((course) => (
                  <option key={course} value={course}>
                    {course}
                  </option>
                ))}
              </Select>
            </FilterGroup>
          </FiltersRow>

          {hasActiveFilters && (
            <ActiveFilters>
              {searchTerm && (
                <FilterChip>
                  Busca: "{searchTerm}"
                  <button onClick={() => handleRemoveFilter("search")}>
                    <FiX />
                  </button>
                </FilterChip>
              )}
              {selectedUniversity && (
                <FilterChip>
                  {selectedUniversity}
                  <button onClick={() => handleRemoveFilter("university")}>
                    <FiX />
                  </button>
                </FilterChip>
              )}
              {selectedCourse && (
                <FilterChip>
                  {selectedCourse}
                  <button onClick={() => handleRemoveFilter("course")}>
                    <FiX />
                  </button>
                </FilterChip>
              )}
            </ActiveFilters>
          )}
        </FiltersSection>

        <ResultsHeader>
          <ResultsCount>
            {loading ? "Carregando..." : `${totalStudents} ${totalStudents === 1 ? "aluno encontrado" : "alunos encontrados"}`}
          </ResultsCount>
        </ResultsHeader>

        {loading ? (
          <LoadingState>Carregando alunos...</LoadingState>
        ) : students.length === 0 ? (
          <EmptyState>
            <h3>Nenhum aluno encontrado</h3>
            <p>Tente ajustar os filtros para ver mais resultados.</p>
          </EmptyState>
        ) : (
          <>
            <StudentsGrid>
              {students.map((student) => (
                <StudentCard
                  key={student.id}
                  onClick={() => handleCardClick(student)}
                >
                  <Avatar
                    $url={
                      student.photo_url?.startsWith("/media")
                        ? `http://localhost:8000${student.photo_url}`
                        : student.photo_url
                    }
                  />
                  <StudentName>{student.full_name}</StudentName>
                  <StudentInfo>
                    {student.university && (
                      <InfoItem>📍 {student.university}</InfoItem>
                    )}
                    {student.course && (
                      <InfoItem>📚 {student.course}</InfoItem>
                    )}
                    {student.semester && (
                      <InfoItem>🎓 {student.semester}</InfoItem>
                    )}
                  </StudentInfo>
                </StudentCard>
              ))}
            </StudentsGrid>

            {totalPages > 1 && (
              <Pagination>
                <PageButton
                  onClick={() => setCurrentPage((p) => p - 1)}
                  disabled={currentPage === 1}
                >
                  <FiChevronLeft /> Anterior
                </PageButton>

                <PageInfo>
                  Página {currentPage} de {totalPages}
                </PageInfo>

                <PageButton
                  onClick={() => setCurrentPage((p) => p + 1)}
                  disabled={!hasMore}
                >
                  Próxima <FiChevronRight />
                </PageButton>
              </Pagination>
            )}
          </>
        )}
      </Container>

      {/* Modal de detalhes */}
      {showModal && selectedStudent && (
        <ModalOverlay onClick={handleCloseModal}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <CloseButton onClick={handleCloseModal}>
              <FiX />
            </CloseButton>

            <ModalHeader>
              <ModalAvatar
                $url={
                  selectedStudent.photo_url?.startsWith("/media")
                    ? `http://localhost:8000${selectedStudent.photo_url}`
                    : selectedStudent.photo_url
                }
              />
              <ModalName>{selectedStudent.full_name}</ModalName>
              {selectedStudent.nickname && (
                <p style={{ color: "var(--text-muted)", margin: 0 }}>
                  @{selectedStudent.nickname}
                </p>
              )}
            </ModalHeader>

            {selectedStudent.bio && (
              <ModalSection>
                <h3>Sobre</h3>
                <p>{selectedStudent.bio}</p>
              </ModalSection>
            )}

            <ModalSection>
              <h3>Informações Acadêmicas</h3>
              {selectedStudent.university && (
                <p>📍 Universidade: {selectedStudent.university}</p>
              )}
              {selectedStudent.course && (
                <p>📚 Curso: {selectedStudent.course}</p>
              )}
              {selectedStudent.semester && (
                <p>📖 Semestre: {selectedStudent.semester}</p>
              )}
            </ModalSection>

            {selectedStudent.interests && selectedStudent.interests.length > 0 && (
              <ModalSection>
                <h3>Interesses</h3>
                <InterestsTags>
                  {selectedStudent.interests.map((interest, index) => (
                    <Tag key={index}>{interest}</Tag>
                  ))}
                </InterestsTags>
              </ModalSection>
            )}

            <ViewProfileButton onClick={() => handleViewFullProfile(selectedStudent.user_id)}>
              Ver Perfil Completo
            </ViewProfileButton>
          </ModalContent>
        </ModalOverlay>
      )}
    </Wrap>
  );
}
