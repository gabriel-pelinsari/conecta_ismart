import styled from "styled-components";

const BadgeWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  text-align: center;
  min-width: 100px;
`;

const BadgeIcon = styled.div`
  font-size: 32px;
  filter: drop-shadow(0 2px 8px rgba(0, 113, 227, 0.3));
`;

const BadgeName = styled.span`
  font-size: 12px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const BadgeDescription = styled.span`
  font-size: 11px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

export default function Badge({ icon, name, description }) {
  return (
    <BadgeWrapper>
      <BadgeIcon>{icon || "🏆"}</BadgeIcon>
      <BadgeName>{name}</BadgeName>
      {description && <BadgeDescription>{description}</BadgeDescription>}
    </BadgeWrapper>
  );
}