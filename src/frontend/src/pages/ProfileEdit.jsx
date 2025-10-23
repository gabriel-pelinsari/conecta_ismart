import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import { Field, Label, Input } from "../components/ui/TextField";
import PhotoUploader from "../components/Profile/PhotoUploader";
import InterestManager from "../components/Profile/InterestManager";
import SocialLinksEditor from "../components/Profile/SocialLinksEditor";
import { useProfile } from "../hooks/useProfile";
import { useProfileUpdate } from "../hooks/useProfileUpdate";

const Wrap = styled.main`
  min-height: 100vh;
  padding: 80px 24px 40px 24px;
  background: ${({ theme }) => theme.colors.bg};
`;

const Container = styled.div`
  width: ${({ theme }) => theme.sizes.containerWidthDesktop};
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  margin: 0 auto;

  @media (max-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: ${({ theme }) => theme.sizes.containerWidthMobile};
  }
`;

const PageHeader = styled.div`
  margin-bottom: 32px;
  text-align: center;
`;

const Title = styled.h1`
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.02em;
`;

const Subtitle = styled.p`
  margin: 0;
  font-size: 16px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const FormCard = styled(Card)`
  display: flex;
  flex-direction: column;
  gap: 32px;
  margin-bottom: 24px;
`;

const FormSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 28px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.outline};

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
`;

const SectionTitle = styled.h2`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
  letter-spacing: -0.01em;
`;

const PhotoSection = styled(FormSection)`
  align-items: center;
  text-align: center;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  @media (max-width: ${({ theme }) => theme.breakpoints.mobile}) {
    grid-template-columns: 1fr;
  }
`;

const FullWidth = styled.div`
  grid-column: 1 / -1;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
  font-family: inherit;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  resize: vertical;
  min-height: 120px;

  &::placeholder {
    color: ${({ theme }) => theme.colors.textMuted};
  }

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15);
  }
`;

const CharCount = styled.span`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
  align-self: flex-end;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 16px;
  margin-top: 8px;

  @media (max-width: ${({ theme }) => theme.breakpoints.mobile}) {
    flex-direction: column-reverse;
  }
`;

const SaveButton = styled(Button)`
  flex: 1;
  padding: 14px 24px;
  background: ${({ theme }) => theme.colors.primary};
  color: white;
  border: none;
  font-weight: 600;
  font-size: 15px;

  &:hover:not(:disabled) {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const CancelButton = styled(Button)`
  flex: 1;
  padding: 14px 24px;
  font-size: 15px;
  font-weight: 600;
`;

const SuccessBox = styled.div`
  padding: 14px 16px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  color: ${({ theme }) => theme.colors.success};
  background: rgba(52, 199, 89, 0.1);
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  margin-bottom: 16px;
`;

const ErrorBox = styled.div`
  padding: 14px 16px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  color: ${({ theme }) => theme.colors.danger};
  background: rgba(255, 59, 48, 0.1);
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  margin-bottom: 16px;
`;

const LoadingBox = styled.div`
  padding: 40px 24px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 14px;
  text-align: center;
`;

const TwoColumnGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;

  @media (max-width: ${({ theme }) => theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
  }
`;

const GridSection = styled(FormSection)``;

export default function ProfileEdit() {
  const navigate = useNavigate();
  const { profile, loading: profileLoading, refetch } = useProfile();
  const { updateProfile, updating, error: updateError } = useProfileUpdate();

  const [formData, setFormData] = useState({
    full_name: "",
    nickname: "",
    university: "",
    course: "",
    semester: "",
    bio: "",
    linkedin: "",
    instagram: "",
    whatsapp: "",
    show_whatsapp: false,
  });

  const [success, setSuccess] = useState(false);
  const [formError, setFormError] = useState("");

  useEffect(() => {
    if (profile) {
      setFormData({
        full_name: profile.full_name || "",
        nickname: profile.nickname || "",
        university: profile.university || "",
        course: profile.course || "",
        semester: profile.semester || "",
        bio: profile.bio || "",
        linkedin: profile.linkedin || "",
        instagram: profile.instagram || "",
        whatsapp: profile.whatsapp || "",
        show_whatsapp: profile.show_whatsapp || false,
      });
    }
  }, [profile]);

  function handleInputChange(field, value) {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    setSuccess(false);
    setFormError("");
  }

  function handleSocialChange(newData) {
    setFormData((prev) => ({
      ...prev,
      ...newData,
    }));
    setSuccess(false);
    setFormError("");
  }

  function handlePhotoUploadSuccess(photoUrl) {
    refetch();
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError("");
    setSuccess(false);

    if (!formData.full_name.trim()) {
      setFormError("Nome completo é obrigatório");
      return;
    }

    try {
      await updateProfile(formData);
      setSuccess(true);

      setTimeout(() => {
        navigate("/profile");
      }, 1500);
    } catch (err) {
      console.error("Erro ao atualizar perfil:", err);
      setFormError(updateError || "Erro ao atualizar perfil");
    }
  }

  if (profileLoading) {
    return (
      <Wrap>
        <Container>
          <PageHeader>
            <Title>Editar Perfil</Title>
            <Subtitle>Atualize suas informações e personalização</Subtitle>
          </PageHeader>
          <LoadingBox>Carregando perfil...</LoadingBox>
        </Container>
      </Wrap>
    );
  }

  if (!profile) {
    return (
      <Wrap>
        <Container>
          <PageHeader>
            <Title>Editar Perfil</Title>
            <Subtitle>Atualize suas informações e personalização</Subtitle>
          </PageHeader>
          <ErrorBox>Erro ao carregar perfil. Tente novamente.</ErrorBox>
        </Container>
      </Wrap>
    );
  }

  return (
    <Wrap>
      <Container as="form" onSubmit={handleSubmit}>
        <PageHeader>
          <Title>Editar Perfil</Title>
          <Subtitle>Atualize suas informações e personalização</Subtitle>
        </PageHeader>

        {/* Mensagens */}
        {success && (
          <SuccessBox>
            Perfil atualizado com sucesso! Redirecionando...
          </SuccessBox>
        )}
        {formError && <ErrorBox>{formError}</ErrorBox>}

        <FormCard>
          {/* Foto de Perfil */}
          <PhotoSection>
            <SectionTitle>Foto de Perfil</SectionTitle>
            <PhotoUploader
              currentPhoto={profile.photo_url}
              onUploadSuccess={handlePhotoUploadSuccess}
            />
          </PhotoSection>

          {/* Informações Básicas */}
          <FormSection>
            <SectionTitle>Informações Básicas</SectionTitle>
            <FormGrid>
              <FullWidth>
                <Field>
                  <Label htmlFor="full_name">Nome Completo *</Label>
                  <Input
                    id="full_name"
                    type="text"
                    placeholder="Seu nome completo"
                    value={formData.full_name}
                    onChange={(e) =>
                      handleInputChange("full_name", e.target.value)
                    }
                    required
                  />
                </Field>
              </FullWidth>

              <Field>
                <Label htmlFor="nickname">Apelido (público)</Label>
                <Input
                  id="nickname"
                  type="text"
                  placeholder="Como você quer ser conhecido"
                  value={formData.nickname}
                  onChange={(e) =>
                    handleInputChange("nickname", e.target.value)
                  }
                  maxLength={50}
                />
              </Field>

              <Field>
                <Label htmlFor="university">Universidade</Label>
                <Input
                  id="university"
                  type="text"
                  placeholder="Ex: USP, FGV, UFMG"
                  value={formData.university}
                  onChange={(e) =>
                    handleInputChange("university", e.target.value)
                  }
                />
              </Field>

              <Field>
                <Label htmlFor="course">Curso</Label>
                <Input
                  id="course"
                  type="text"
                  placeholder="Ex: Engenharia, Administração"
                  value={formData.course}
                  onChange={(e) => handleInputChange("course", e.target.value)}
                />
              </Field>

              <Field>
                <Label htmlFor="semester">Semestre</Label>
                <Input
                  id="semester"
                  type="text"
                  placeholder="Ex: 1º, 2º, 7º"
                  value={formData.semester}
                  onChange={(e) =>
                    handleInputChange("semester", e.target.value)
                  }
                />
              </Field>
            </FormGrid>
          </FormSection>

          {/* Bio */}
          <FormSection>
            <SectionTitle>Bio / Sobre mim</SectionTitle>
            <Field>
              <TextArea
                id="bio"
                placeholder="Conte um pouco sobre você, seus interesses e objetivos..."
                value={formData.bio}
                onChange={(e) => handleInputChange("bio", e.target.value)}
                maxLength={1000}
              />
              <CharCount>{formData.bio.length}/1000</CharCount>
            </Field>
          </FormSection>

          <TwoColumnGrid>
            {/* Interesses */}
            <GridSection>
              <SectionTitle>Seus Interesses</SectionTitle>
              <InterestManager editable={true} />
            </GridSection>

            {/* Redes Sociais */}
            <GridSection>
              <SectionTitle>Redes Sociais</SectionTitle>
              <SocialLinksEditor
                values={formData}
                onChange={handleSocialChange}
                editable={true}
              />
            </GridSection>
          </TwoColumnGrid>

          {/* Botões de Ação */}
          <ButtonGroup>
            <CancelButton
              type="button"
              onClick={() => navigate("/profile")}
              disabled={updating}
            >
              Cancelar
            </CancelButton>
            <SaveButton type="submit" disabled={updating}>
              {updating ? "Salvando..." : "💾 Salvar Alterações"}
            </SaveButton>
          </ButtonGroup>
        </FormCard>
      </Container>
    </Wrap>
  );
}