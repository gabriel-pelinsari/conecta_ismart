import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";
import api from "../api/axios";
import { profileApi } from "../services/profileApi";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import { Field, Label, Input } from "../components/ui/TextField";

const Page = styled.main`
  min-height: 100vh;
  padding: 36px 24px 48px;
  display: flex;
  justify-content: center;
`;

const Container = styled.div`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const Header = styled.header`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const Title = styled.h1`
  margin: 0;
  font-size: 28px;
  letter-spacing: -0.02em;
`;

const Subtitle = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 15px;
`;

const Tabs = styled.div`
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
`;

const TabButton = styled.button`
  padding: 8px 18px;
  border-radius: ${({ theme }) => theme.radii.md};
  border: 1px solid
    ${({ $active, theme }) => ($active ? theme.colors.primary : theme.colors.outline)};
  background: ${({ $active, theme }) => ($active ? theme.colors.primary : theme.colors.surface)};
  color: ${({ $active, theme }) => ($active ? theme.colors.bg : theme.colors.text)};
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
`;

const StatCard = styled(Card)`
  padding: 18px 20px;
`;

const StatLabel = styled.span`
  font-size: 13px;
  margin-right: 8px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const StatValue = styled.strong`
  font-size: 15px;
  letter-spacing: -0.01em;
  color: ${({ theme }) => theme.colors.text};
`;

const UploadCard = styled(Card)`
  padding: 28px;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-top: 16px;
`;

const FilePicker = styled.label`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px dashed ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  cursor: pointer;
  transition: border-color 0.15s ease, color 0.15s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const FileName = styled.span`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text};
`;

const HiddenInput = styled.input`
  display: none;
`;

const Helper = styled.p`
  margin: 0;
  font-size: 13px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const ResultBox = styled.pre`
  max-height: 260px;
  overflow: auto;
  padding: 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
`;

const ErrorBox = styled.div`
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.danger};
  background: rgba(255, 59, 48, 0.1);
  color: ${({ theme }) => theme.colors.danger};
  font-size: 14px;
`;

const StudentsCard = styled(Card)`
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
`;

const StudentsHeader = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;

  @media (min-width: 720px) {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
`;

const StudentsHeaderText = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const StudentsTitle = styled.h2`
  margin: 0;
  font-size: 20px;
`;

const StudentsSubtitle = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 14px;
`;

const StudentsControls = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
`;

const SearchInputStyled = styled.input`
  padding: 10px 12px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.bg};
  color: ${({ theme }) => theme.colors.text};
  min-width: 220px;
  flex: 1;
`;

const StudentGrid = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const StudentRow = styled.div`
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.lg};
  padding: 16px 18px;
  background: ${({ theme }) => theme.colors.surface};
  flex-wrap: wrap;
`;

const Avatar = styled.div`
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 2px solid ${({ theme }) => theme.colors.outline};
  background: ${({ $src, theme }) =>
    $src ? `url(${$src}) center/cover no-repeat` : theme.colors.surface};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme.colors.primary};
  font-weight: 600;
  font-size: 18px;
`;

const StudentInfo = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const StudentName = styled.span`
  font-weight: 600;
  font-size: 16px;
`;

const StudentUniversity = styled.span`
  color: ${({ theme }) => theme.colors.text};
  font-size: 14px;
`;

const StudentMeta = styled.span`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 13px;
`;

const StudentStats = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const StudentActions = styled.div`
  display: flex;
  gap: 6px;
  flex-direction: column;
  width: 160px;
  min-width: 160px;
`;

const ActionButton = styled.button`
  padding: 8px 10px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.15s ease, transform 0.1s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
  }

  &:active {
    transform: translateY(1px);
  }
`;

const DangerButton = styled(ActionButton)`
  border-color: ${({ theme }) => theme.colors.danger};
  color: ${({ theme }) => theme.colors.danger};

  &:hover {
    border-color: ${({ theme }) => theme.colors.danger};
    background: ${({ theme }) => theme.colors.danger}11;
  }
`;

const EmptyState = styled.div`
  padding: 36px 0;
  text-align: center;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const LoadingState = styled(EmptyState)``;

const ErrorText = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.danger};
  font-size: 14px;
`;

export default function Admin({ token }) {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("upload");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [meta, setMeta] = useState({ processed: 0, lastImport: "Nunca" });

  const [students, setStudents] = useState([]);
  const [studentsLoading, setStudentsLoading] = useState(false);
  const [studentsError, setStudentsError] = useState("");
  const [studentsLoaded, setStudentsLoaded] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setStudents([]);
    setStudentsLoaded(false);
  }, [token]);

  useEffect(() => {
    if (activeTab === "students" && !studentsLoaded) {
      fetchStudents();
    }
  }, [activeTab, studentsLoaded, token]);

  async function fetchStudents() {
    setStudentsLoading(true);
    setStudentsError("");
    try {
      const data = await profileApi.listUsers(token);
      setStudents(Array.isArray(data) ? data : []);
      setStudentsLoaded(true);
    } catch (err) {
      console.error(err);
      setStudentsError("Não foi possível carregar os alunos.");
    } finally {
      setStudentsLoading(false);
    }
  }

  const filteredStudents = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return students;
    return students.filter((student) => {
      const haystack = `${student.full_name || ""} ${student.nickname || ""} ${
        student.university || ""
      }`.toLowerCase();
      return haystack.includes(term);
    });
  }, [search, students]);

  async function handleUpload(e) {
    e.preventDefault();
    setError("");
    setResult("");

    if (!file) {
      setError("Selecione um arquivo .csv antes de enviar.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const res = await api.post("/auth/upload-csv", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });
      setResult(JSON.stringify(res.data, null, 2));
      setMeta({
        processed: res.data?.processed_count || 0,
        lastImport: new Date().toLocaleString("pt-BR"),
      });
    } catch (err) {
      console.error(err);
      setError("Erro ao enviar CSV. Verifique o arquivo e suas permissões.");
    } finally {
      setUploading(false);
    }
  }

  function handleFileChange(e) {
    const f = e.target.files?.[0];
    setError("");
    if (!f) {
      setFile(null);
      return;
    }
    if (!f.name.endsWith(".csv")) {
      setError("O arquivo deve ter extensão .csv");
      setFile(null);
      return;
    }
    setFile(f);
  }

  async function handleDeleteStudent(student) {
    const confirmed = window.confirm(`Remover ${student.full_name || student.nickname}?`);
    if (!confirmed) return;

    try {
      await profileApi.deleteUser(token, student.user_id);
      setStudents((prev) => prev.filter((item) => item.user_id !== student.user_id));
    } catch (err) {
      console.error(err);
      alert("Não foi possível remover o aluno.");
    }
  }

  function handleViewProfile(student) {
    navigate(`/profile/${student.user_id}`);
  }

  return (
    <Page>
      <Container>
        <Header>
          <Title>Painel administrativo</Title>
          <Subtitle>Importe dados e gerencie perfis da comunidade.</Subtitle>
        </Header>

        <Tabs role="tablist">
          <TabButton
            type="button"
            $active={activeTab === "upload"}
            onClick={() => setActiveTab("upload")}
          >
            Importar CSV
          </TabButton>
          <TabButton
            type="button"
            $active={activeTab === "students"}
            onClick={() => setActiveTab("students")}
          >
            Controle de alunos
          </TabButton>
        </Tabs>

        {activeTab === "upload" && (
          <>
            <Grid>
              <StatCard>
                <StatLabel>Última importação</StatLabel>
                <StatValue>{meta.lastImport}</StatValue>
              </StatCard>
              <StatCard>
                <StatLabel>Registros processados</StatLabel>
                <StatValue>{meta.processed}</StatValue>
              </StatCard>
            </Grid>

            <UploadCard as="section" aria-label="Administração - Upload de CSV">
              <Field>
                <Label>Arquivo CSV</Label>
                <FilePicker htmlFor="csv">
                  <span>{file ? "Trocar arquivo" : "Selecionar arquivo"}</span>
                  <FileName>{file ? file.name : "Nenhum arquivo selecionado"}</FileName>
                </FilePicker>
                <HiddenInput
                  id="csv"
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                />
                <Helper>Formato esperado: uma coluna chamada <code>email</code>.</Helper>
              </Field>

              <Form onSubmit={handleUpload} noValidate>
                <Button type="submit" disabled={!file || uploading}>
                  {uploading ? "Enviando..." : "Enviar CSV"}
                </Button>

                {error && <ErrorBox role="alert">{error}</ErrorBox>}
                {result && <ResultBox aria-live="polite">{result}</ResultBox>}
              </Form>
            </UploadCard>
          </>
        )}

        {activeTab === "students" && (
          <StudentsCard>
            <StudentsHeader>
              <StudentsHeaderText>
                <StudentsTitle>Controle de alunos</StudentsTitle>
                <StudentsSubtitle>Visualize os perfis já cadastrados.</StudentsSubtitle>
              </StudentsHeaderText>
              <StudentsControls>
                <SearchInputStyled
                  type="search"
                  placeholder="Buscar por nome, nickname ou universidade"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </StudentsControls>
            </StudentsHeader>

            {studentsError && <ErrorText>{studentsError}</ErrorText>}
            {studentsLoading && <LoadingState>Carregando alunos...</LoadingState>}

            {!studentsLoading && !studentsError && filteredStudents.length === 0 && (
              <EmptyState>Nenhum aluno encontrado.</EmptyState>
            )}

            {!studentsLoading && !studentsError && filteredStudents.length > 0 && (
              <StudentGrid>
                {filteredStudents.map((student) => {
                  const photoUrl = student.photo_url?.startsWith("/media")
                    ? `http://localhost:8000${student.photo_url}`
                    : student.photo_url;
                  const initials = (student.full_name || student.nickname || "?")
                    .charAt(0)
                    .toUpperCase();
                  return (
                    <StudentRow key={student.user_id}>
                      <Avatar $src={photoUrl}>{!photoUrl && initials}</Avatar>
                      <StudentInfo>
                        <StudentName>{student.full_name || "Sem nome"}</StudentName>
                        <StudentUniversity>
                          {student.university || "Universidade não informada"}
                        </StudentUniversity>
                        <StudentMeta>
                          {(student.course || "Curso não informado")}
                          {student.semester ? ` • ${student.semester}` : ""}
                        </StudentMeta>
                        <StudentStats>
                          <span>{student.stats?.threads_count ?? 0} threads</span>
                          <span>{student.stats?.comments_count ?? 0} comentários</span>
                          <span>{student.stats?.events_count ?? 0} eventos</span>
                        </StudentStats>
                      </StudentInfo>
                      <StudentActions>
                        <ActionButton type="button" onClick={() => handleViewProfile(student)}>
                          Ver perfil
                        </ActionButton>
                        <DangerButton type="button" onClick={() => handleDeleteStudent(student)}>
                          Remover
                        </DangerButton>
                      </StudentActions>
                    </StudentRow>
                  );
                })}
              </StudentGrid>
            )}
          </StudentsCard>
        )}
      </Container>
    </Page>
  );
}
