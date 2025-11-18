import { useState } from "react";
import styled from "styled-components";
import { FiMapPin, FiCalendar, FiUsers } from "react-icons/fi";
import Card from "../ui/Card";
import Button from "../ui/Button";

const Wrap = styled(Card)`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  margin: 0 auto 12px auto;
  padding: 20px 22px;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
`;

const Title = styled.h3`
  margin: 0;
  font-size: 18px;
  color: ${({ theme }) => theme.colors.text};
`;

const Cover = styled.div`
  width: 100%;
  border-radius: ${({ theme }) => theme.radii.md};
  overflow: hidden;
  margin: 14px 0;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surfaceAlt || theme.colors.surface};
  max-height: 260px;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const MetaRow = styled.div`
  display: grid;
  gap: 10px;
  margin-top: 6px;

  @media (min-width: 520px) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text};

  svg {
    color: ${({ theme }) => theme.colors.textMuted};
  }
`;

const Description = styled.p`
  margin: 12px 0 0 0;
  color: ${({ theme }) => theme.colors.text};
  line-height: 1.5;
`;

const Badge = styled.span`
  padding: 4px 10px;
  border-radius: ${({ theme }) => theme.radii.xs};
  background: ${({ theme }) => theme.colors.primary}22;
  color: ${({ theme }) => theme.colors.primary};
  font-size: 12px;
  font-weight: 600;
`;

const Creator = styled.p`
  margin: 6px 0 0 0;
  font-size: 13px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const RSVPRow = styled.div`
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const RSVPButton = styled(Button)`
  flex: 1;
  min-width: 140px;
  justify-content: center;
`;

const RSVPStatus = styled.span`
  display: block;
  margin-top: 6px;
  font-size: 13px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

export default function EventCard({ event, onRsvp }) {
  const [pending, setPending] = useState(false);
  if (!event) return null;

  const {
    title,
    description,
    location,
    scheduled_at,
    date,
    datetime,
    audience,
    type,
    creator,
    confirmed_people,
    confirmed_users,
    confirmed_count,
    comment,
    photo_url,
    photo,
    user_rsvp_status,
  } = event;

  const coverImage = photo_url || photo;
  const eventDate = scheduled_at || datetime || date;
  const formattedDate = eventDate
    ? new Date(eventDate).toLocaleString("pt-BR", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "Data a definir";
  const scopeLabel = (audience || type || "").toLowerCase() === "faculdade"
    ? "Faculdade específica"
    : "Geral";
  const confirmed =
    confirmed_count ??
    confirmed_people?.length ??
    confirmed_users?.length ??
    0;
  const creatorName =
    creator?.nickname || creator?.full_name || creator?.name || "Organizador";

  async function handleRsvp(status) {
    if (!onRsvp || pending) return;
    setPending(true);
    try {
      await onRsvp(event.id, status);
    } catch (e) {
      console.error(e);
    } finally {
      setPending(false);
    }
  }

  return (
    <Wrap>
      <Header>
        <Title>{title}</Title>
        <Badge>{scopeLabel}</Badge>
      </Header>

      {coverImage && (
        <Cover>
          <img src={coverImage} alt={`Imagem do evento ${title}`} />
        </Cover>
      )}

      <MetaRow>
        <MetaItem>
          <FiCalendar aria-hidden="true" />
          {formattedDate}
        </MetaItem>
        <MetaItem>
          <FiMapPin aria-hidden="true" />
          {location || "Local a definir"}
        </MetaItem>
        <MetaItem>
          <FiUsers aria-hidden="true" />
          {confirmed} confirmado{confirmed === 1 ? "" : "s"}
        </MetaItem>
      </MetaRow>

      {description && <Description>{description}</Description>}
      {comment && (
        <Description style={{ color: "inherit", opacity: 0.8 }}>
          <strong>Observação:</strong> {comment}
        </Description>
      )}

      <Creator>Organizado por {creatorName}</Creator>

      <RSVPRow>
        <RSVPButton
          type="button"
          onClick={() => handleRsvp("confirmed")}
          disabled={pending}
          style={
            user_rsvp_status === "confirmed"
              ? { background: "rgba(0,113,227,0.2)", borderColor: "#0071e3" }
              : undefined
          }
        >
          Confirmar presença
        </RSVPButton>
        <RSVPButton
          type="button"
          onClick={() => handleRsvp("maybe")}
          disabled={pending}
          style={
            user_rsvp_status === "maybe"
              ? { background: "rgba(255,159,10,0.2)", borderColor: "#ff9f0a" }
              : undefined
          }
        >
          Talvez
        </RSVPButton>
        <RSVPButton
          type="button"
          onClick={() => handleRsvp("declined")}
          disabled={pending}
        >
          Cancelar
        </RSVPButton>
      </RSVPRow>
      {user_rsvp_status && (
        <RSVPStatus>Você respondeu: {user_rsvp_status}</RSVPStatus>
      )}
    </Wrap>
  );
}
