import styled from "styled-components";

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 24px 0;
`;

const StatCard = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  padding: 16px;
  text-align: center;

  @media (max-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: 4px;
  }

  @media (max-width: ${({ theme }) => theme.breakpoints.mobile}) {
    padding: 4px;
  }
`;

const StatValue = styled.div`
  font-size: 28px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.primary};
  margin-bottom: 4px;

  @media (max-width: ${({ theme }) => theme.breakpoints.tablet}) {
    font-size: 22px;
  }

  @media (max-width: ${({ theme }) => theme.breakpoints.mobile}) {
    font-size: 22px;
  }
`;

const StatLabel = styled.div`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

export default function ProfileStats({ stats }) {
  return (
    <StatsGrid>
      <StatCard>
        <StatValue>{stats?.threads_count || 0}</StatValue>
        <StatLabel>Threads</StatLabel>
      </StatCard>
      <StatCard>
        <StatValue>{stats?.comments_count || 0}</StatValue>
        <StatLabel>Comentários</StatLabel>
      </StatCard>
      <StatCard>
        <StatValue>{stats?.events_count || 0}</StatValue>
        <StatLabel>Eventos</StatLabel>
      </StatCard>
    </StatsGrid>
  );
}