import { useMemo } from "react";
import styled from "styled-components";
import Card from "../components/ui/Card";

const Page = styled.main`
  min-height: 100vh;
  padding: 48px 24px 80px;
  display: flex;
  justify-content: center;
  background: radial-gradient(circle at top, rgba(63, 81, 181, 0.15), transparent 45%),
    ${({ theme }) => theme.colors.pageBg || "#f4f6fb"};
`;

const Container = styled.div`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerLarge || theme.sizes.containerMedium};
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Header = styled.header`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const Title = styled.h1`
  margin: 0;
  font-size: 32px;
  letter-spacing: -0.03em;
`;

const Subtitle = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 15px;
`;

const SectionTitle = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const DashboardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
`;

const SurfaceCard = styled(Card)`
  border: none;
  background: ${({ theme }) => theme.colors.surface};
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
  transition: transform 0.25s ease, box-shadow 0.25s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.1);
  }
`;

const BigNumberCard = styled(SurfaceCard)`
  padding: 24px 26px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const BigNumberLabel = styled.span`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const BigNumberValue = styled.span`
  font-size: 40px;
  font-weight: 700;
  letter-spacing: -0.03em;
`;

const DeltaPill = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: ${({ $positive }) => ($positive ? "rgba(34,197,94,.15)" : "rgba(239,68,68,.12)")};
  color: ${({ $positive, theme }) =>
    $positive ? theme.colors.success || "#22c55e" : theme.colors.danger};
`;

const ChartsRow = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
`;

const ChartCard = styled(SurfaceCard)`
  padding: 26px 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
`;

const ChartTitle = styled.h3`
  margin: 0;
  font-size: 18px;
`;

const BarList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const BarRow = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: transform 0.2s ease;

  &:hover {
    transform: translateX(4px);
  }
`;

const BarLabel = styled.span`
  min-width: 90px;
  font-size: 13px;
`;

const BarTrack = styled.div`
  flex: 1;
  height: 12px;
  border-radius: 999px;
  background: ${({ theme }) => theme.colors.outline};
  overflow: hidden;
`;

const BarFill = styled.span`
  display: block;
  height: 100%;
  border-radius: inherit;
  background: ${({ theme }) => theme.colors.primary};
  width: ${({ $value }) => Math.min(100, Math.max(0, $value))}%;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease;

  ${BarRow}:hover & {
    box-shadow: 0 0 0 2px ${({ theme }) => theme.colors.surface}, 0 0 0 4px rgba(255, 255, 255, 0.7);
  }
`;

const BarValue = styled.span`
  min-width: 40px;
  text-align: right;
  font-weight: 600;
`;

const TrendList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const TrendRow = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text};
  padding: 8px 10px;
  border-radius: ${({ theme }) => theme.radii.sm};
  transition: background 0.2s ease;

  &:hover {
    background: ${({ theme }) => theme.colors.surfaceAlt || "rgba(15,23,42,0.04)"};
  }
`;

const TrendDelta = styled.span`
  color: ${({ $positive, theme }) =>
    $positive ? theme.colors.success || "#32D74B" : theme.colors.danger};
  font-weight: 700;
`;

const SparklineWrapper = styled.div`
  width: 100%;
  height: 80px;
  cursor: crosshair;
  transition: filter 0.3s ease;

  &:hover {
    filter: drop-shadow(0 8px 16px rgba(15, 23, 42, 0.25));
  }
`;

const SparklineSvg = styled.svg`
  width: 100%;
  height: 100%;
  stroke: ${({ theme }) => theme.colors.primary};
  fill: ${({ theme }) => theme.colors.primary}2E;
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
`;

export default function AdminDashboard() {
  const summary = useMemo(
    () => [
      { label: "Usuários ativos", value: "1.254", delta: "+12% vs semana passada", positive: true },
      { label: "Threads criadas", value: "342", delta: "+5% vs semana passada", positive: true },
      { label: "Eventos agendados", value: "18", delta: "-2% vs semana passada", positive: false },
      { label: "Enquetes ativas", value: "9", delta: "+3% vs semana passada", positive: true },
    ],
    []
  );

  const distribution = useMemo(
    () => [
      { label: "Privadas", value: 45 },
      { label: "Públicas", value: 32 },
      { label: "Intercâmbio", value: 23 },
    ],
    []
  );

  const growth = useMemo(
    () => [
      { label: "Jan", value: 80 },
      { label: "Fev", value: 68 },
      { label: "Mar", value: 90 },
      { label: "Abr", value: 120 },
      { label: "Mai", value: 140 },
      { label: "Jun", value: 155 },
    ],
    []
  );

  const highlights = useMemo(
    () => [
      { label: "Entrega de bolsas", value: "78 confirmações", delta: "+18%" },
      { label: "Mentorias concluídas", value: "54 sessões", delta: "+9%" },
      { label: "Novos grupos", value: "12 grupos", delta: "+3%" },
    ],
    []
  );

  const growthMax = Math.max(...growth.map((item) => item.value));
  const normalizedPoints =
    growth.length > 1
      ? growth
          .map((item, index) => {
            const x = (index / (growth.length - 1)) * 100;
            const y = 100 - (item.value / growthMax) * 100;
            return `${x},${y}`;
          })
          .join(" ")
      : "0,100 100,100";
  const areaPoints = `0,100 ${normalizedPoints} 100,100`;

  return (
    <Page>
      <Container>
        <Header>
          <Title>Visão geral</Title>
          <Subtitle>Indicadores-chave da comunidade, com dados mockados por enquanto.</Subtitle>
        </Header>

        <DashboardGrid>
          {summary.map((item) => (
            <BigNumberCard key={item.label} role="presentation">
              <BigNumberLabel>{item.label}</BigNumberLabel>
              <BigNumberValue>{item.value}</BigNumberValue>
              <DeltaPill $positive={item.positive}>
                {item.positive ? "↑" : "↓"} {item.delta}
              </DeltaPill>
            </BigNumberCard>
          ))}
        </DashboardGrid>

        <ChartsRow>
          <ChartCard>
            <SectionTitle>
              <ChartTitle>Distribuição por categoria</ChartTitle>
              <span>Base: 1.254 perfis</span>
            </SectionTitle>
            <BarList>
              {distribution.map((item) => (
                <BarRow key={item.label}>
                  <BarLabel>{item.label}</BarLabel>
                  <BarTrack>
                    <BarFill $value={item.value} />
                  </BarTrack>
                  <BarValue>{item.value}%</BarValue>
                </BarRow>
              ))}
            </BarList>
          </ChartCard>

          <ChartCard>
            <SectionTitle>
              <ChartTitle>Novos usuários por mês</ChartTitle>
              <span>Últimos 6 meses</span>
            </SectionTitle>
            <SparklineWrapper>
              <SparklineSvg viewBox="0 0 100 100" preserveAspectRatio="none">
                <polygon points={areaPoints} opacity="0.18" />
                <polyline points={normalizedPoints} fill="none" />
              </SparklineSvg>
            </SparklineWrapper>
            <BarList>
              {growth.map((item) => (
                <BarRow key={item.label}>
                  <BarLabel>{item.label}</BarLabel>
                  <BarTrack>
                    <BarFill $value={(item.value / growthMax) * 100} />
                  </BarTrack>
                  <BarValue>{item.value}</BarValue>
                </BarRow>
              ))}
            </BarList>
          </ChartCard>

          <ChartCard>
            <SectionTitle>
              <ChartTitle>Atividades em destaque</ChartTitle>
              <span>Comparativo semanal</span>
            </SectionTitle>
            <TrendList>
              {highlights.map((item) => (
                <TrendRow key={item.label}>
                  <span>
                    <strong>{item.label}</strong> — {item.value}
                  </span>
                  <TrendDelta $positive={!item.delta.includes("-")}>
                    {item.delta.includes("-") ? "↓" : "↑"} {item.delta}
                  </TrendDelta>
                </TrendRow>
              ))}
            </TrendList>
          </ChartCard>
        </ChartsRow>
      </Container>
    </Page>
  );
}
