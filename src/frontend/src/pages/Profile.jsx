import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import styled from "styled-components";
import api from "../api/axios";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Tag from "../components/ui/Tag";
import Badge from "../components/ui/Badge";
import ProfileStats from "../components/ProfileStats";
import { useProfile } from "../hooks/useProfile";

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

const ProfileCard = styled(Card)`
  display: flex;
  flex-direction: column;
  gap: 32px;
  margin-bottom: 24px;
`;

const Header = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding-bottom: 28px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.outline};
`;

const Avatar = styled.div`
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: ${({ $url, theme }) =>
    $url ? `url(${$url})` : theme.colors.outline};
  background-size: cover;
  background-position: center;
  border: 3px solid ${({ theme }) => theme.colors.outline};
  flex-shrink: 0;
`;

const Info = styled.div`
  text-align: center;
  width: 100%;
`;

const Name = styled.h2`
  margin: 0 0 6px 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
`;

const Nickname = styled.span`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 16px;
`;

const Meta = styled.div`
  margin-top: 12px;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textMuted};
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const Section = styled.div`
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

const SectionTitle = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
  letter-spacing: -0.01em;
`;

const Bio = styled.p`
  margin: 0;
  line-height: 1.6;
  color: ${({ theme }) => theme.colors.text};
  font-size: 15px;
`;

const TagsGrid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const BadgesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
`;

const SocialLinks = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 14px;
`;

const SocialLink = styled.a`
  color: ${({ theme }) => theme.colors.primary};
  text-decoration: none;
  word-break: break-all;

  &:hover {
    text-decoration: underline;
  }
`;

const SocialText = styled.div`
  color: ${({ theme }) => theme.colors.text};
  word-break: break-all;
`;

const EditButton = styled(Button)`
  width: 100%;
  padding: 14px 24px;
  background: ${({ theme }) => theme.colors.primary};
  color: white;
  border: none;
  font-weight: 600;
  font-size: 15px;

  &:hover {
    opacity: 0.9;
  }
`;

const EmptyState = styled.div`
  padding: 40px 24px;
  text-align: center;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 15px;
`;

const LoadingState = styled(EmptyState)`
  font-size: 16px;
`;

const TwoColumnGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;

  @media (max-width: ${({ theme }) => theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
  }
`;

const GridSection = styled(Section)``;

export default function Profile() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { profile, loading, error, refetch } = useProfile(userId ? parseInt(userId) : null);
  const [isOwnProfile, setIsOwnProfile] = useState(false);
  const [currentUserId, setCurrentUserId] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      // Decodificar user_id do token JWT (simples decodificação)
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        setCurrentUserId(payload.sub); // ou user_id dependendo do backend
      } catch (e) {
        console.log("Não foi possível decodificar token");
      }
    }
  }, []);

  useEffect(() => {
    if (profile && currentUserId) {
      setIsOwnProfile(profile.user_id === currentUserId);
    }
  }, [profile, currentUserId]);

  if (loading) {
    return (
      <Wrap>
        <Container>
          <PageHeader>
            <Title>Perfil</Title>
          </PageHeader>
          <LoadingState>Carregando perfil...</LoadingState>
        </Container>
      </Wrap>
    );
  }

  if (error || !profile) {
    return (
      <Wrap>
        <Container>
          <PageHeader>
            <Title>Perfil</Title>
          </PageHeader>
          <EmptyState>Perfil não encontrado</EmptyState>
        </Container>
      </Wrap>
    );
  }

  const photoUrl = profile.photo_url?.startsWith("/media")
    ? `http://localhost:8000${profile.photo_url}`
    : profile.photo_url;

  return (
    <Wrap>
      <Container>
        <PageHeader>
          <Title>
            {isOwnProfile ? "Seu Perfil" : "Perfil"}
          </Title>
          <Subtitle>
            {isOwnProfile
              ? "Visualize e gerencie suas informações"
              : "Conheça melhor este membro"}
          </Subtitle>
        </PageHeader>

        <ProfileCard>
          {/* Header com Avatar e Nome */}
          <Header>
            <Avatar $url={photoUrl} />
            <Info>
              <Name>
                {profile.full_name}
                {profile.nickname && (
                  <>
                    <br />
                    <Nickname>@{profile.nickname}</Nickname>
                  </>
                )}
              </Name>
              <Meta>
                {profile.university && <div>🎓 {profile.university}</div>}
                {profile.course && <div>📚 {profile.course}</div>}
                {profile.semester && <div>📅 {profile.semester}</div>}
              </Meta>
            </Info>
          </Header>

          {/* Bio */}
          {profile.bio && (
            <Section>
              <SectionTitle>Sobre</SectionTitle>
              <Bio>{profile.bio}</Bio>
            </Section>
          )}

          {/* Stats */}
          <Section>
            <SectionTitle>Estatísticas</SectionTitle>
            <ProfileStats stats={profile.stats} />
          </Section>

          <TwoColumnGrid>
            {/* Interesses */}
            {profile.interests && profile.interests.length > 0 && (
              <GridSection>
                <SectionTitle>Interesses</SectionTitle>
                <TagsGrid>
                  {profile.interests.map((interest) => (
                    <Tag key={interest.id}>{interest.name}</Tag>
                  ))}
                </TagsGrid>
              </GridSection>
            )}

            {/* Badges */}
            {profile.badges && profile.badges.length > 0 && (
              <GridSection>
                <SectionTitle>Conquistas</SectionTitle>
                <BadgesGrid>
                  {profile.badges.map((badge) => (
                    <Badge
                      key={badge.key}
                      icon={badge.icon_url}
                      name={badge.name}
                    />
                  ))}
                </BadgesGrid>
              </GridSection>
            )}
          </TwoColumnGrid>

          {/* Redes Sociais */}
          {(profile.linkedin ||
            profile.instagram ||
            (profile.whatsapp && profile.show_whatsapp)) && (
              <Section>
                <SectionTitle>Contato</SectionTitle>
                <SocialLinks>
                  {profile.linkedin && (
                    <SocialLink href={profile.linkedin} target="_blank" rel="noopener noreferrer">
                      🔗 LinkedIn
                    </SocialLink>
                  )}
                  {profile.instagram && (
                    <SocialText>📸 Instagram: {profile.instagram}</SocialText>
                  )}
                  {profile.whatsapp && profile.show_whatsapp && (
                    <SocialText>📱 WhatsApp: {profile.whatsapp}</SocialText>
                  )}
                </SocialLinks>
              </Section>
            )}

          {isOwnProfile && (
            <EditButton onClick={() => navigate("/profile/edit")}>
              ✏️ Editar Perfil
            </EditButton>
          )}

          {/* Botão Editar (se for seu perfil) */}
          {isOwnProfile && (
            <EditButton onClick={() => navigate("/profile/edit")}>
              ✏️ Editar Perfil
            </EditButton>
          )}
        </ProfileCard>
      </Container>
    </Wrap>
  );
}