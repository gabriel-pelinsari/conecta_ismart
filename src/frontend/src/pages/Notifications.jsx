import { useEffect, useState } from "react";
import styled from "styled-components";
import {
  FiBell,
  FiMessageCircle,
  FiUsers,
  FiCalendar,
  FiCheckCircle,
} from "react-icons/fi";
import { notificationApi } from "../services/notificationApi";

const Page = styled.main`
  min-height: 100vh;
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const Container = styled.div`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const Header = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Title = styled.h1`
  margin: 0;
  font-size: 26px;
  letter-spacing: -0.02em;
  color: ${({ theme }) => theme.colors.text};
`;

const Subtitle = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 15px;
`;

const List = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const NotificationCard = styled.div`
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 14px;
  padding: 16px 18px;
  border-radius: ${({ theme }) => theme.radii.lg};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  box-shadow: ${({ theme }) => theme.shadows.soft};
  opacity: ${({ $read }) => ($read ? 0.8 : 1)};
`;

const IconWrapper = styled.div`
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ theme }) => theme.colors.primary}15;
  color: ${({ theme }) => theme.colors.primary};
  font-size: 22px;
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const NotificationTitle = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const NotificationDescription = styled.span`
  color: ${({ theme }) => theme.colors.text};
  font-size: 14px;
  line-height: 1.5;
`;

const Meta = styled.div`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
  text-align: right;
`;

const Status = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: ${({ theme, $read }) =>
    $read ? theme.colors.textMuted : theme.colors.primary};
`;

const EmptyState = styled.div`
  margin-top: 32px;
  padding: 36px;
  border: 1px dashed ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.lg};
  text-align: center;
  color: ${({ theme }) => theme.colors.textMuted};
`;

function getIcon(type) {
  switch (type) {
    case "thread_reply":
      return <FiMessageCircle />;
    case "event_invite":
      return <FiCalendar />;
    case "poll_result":
      return <FiBell />;
    case "friend_request":
      return <FiUsers />;
    default:
      return <FiBell />;
  }
}

function formatRelativeTime(date) {
  if (!date) return "";
  const diff = Date.now() - new Date(date).getTime();
  const minutes = Math.round(diff / (1000 * 60));
  if (minutes < 1) return "agora mesmo";
  if (minutes < 60) return `há ${minutes} min`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `há ${hours} h`;
  const days = Math.round(hours / 24);
  return `há ${days} dia${days > 1 ? "s" : ""}`;
}

export default function Notifications() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchNotifications() {
      setLoading(true);
      try {
        const data = await notificationApi.list();
        setItems(data);
      } catch (err) {
        console.error("Erro ao carregar notificações", err);
      } finally {
        setLoading(false);
      }
    }
    fetchNotifications();
  }, []);

  return (
    <Page>
      <Container>
        <Header>
          <Title>Notificações</Title>
          <Subtitle>Acompanhe convites, respostas e alertas do Conecta.</Subtitle>
        </Header>

        {loading && <EmptyState>Carregando...</EmptyState>}

        {!loading && items.length === 0 && (
          <EmptyState>Nenhuma notificação por enquanto.</EmptyState>
        )}

        {!loading && items.length > 0 && (
          <List>
            {items.map((item) => (
              <NotificationCard key={item.id} $read={item.is_read}>
                <IconWrapper aria-hidden="true">{getIcon(item.type)}</IconWrapper>
                <Content>
                  <NotificationTitle>{item.title}</NotificationTitle>
                  <NotificationDescription>{item.description}</NotificationDescription>
                </Content>
                <Meta>
                  <Status $read={item.is_read}>
                    <FiCheckCircle aria-hidden="true" />
                    {item.is_read ? "lida" : "nova"}
                  </Status>
                  <div>{formatRelativeTime(item.created_at)}</div>
                </Meta>
              </NotificationCard>
            ))}
          </List>
        )}
      </Container>
    </Page>
  );
}
