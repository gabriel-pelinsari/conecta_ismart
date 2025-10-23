import styled from "styled-components";
import Card from "../components/ui/Card";

const Wrap = styled.main`
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
`;

const Content = styled(Card)`
  text-align: center;
  padding: 48px 32px;
  max-width: 600px;
`;

const Title = styled.h1`
  margin: 0 0 12px 0;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.02em;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: ${({ theme }) => theme.colors.textMuted};
  line-height: 1.6;
  margin: 0;
`;

const ComingSoon = styled.div`
  margin-top: 28px;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textMuted};
  opacity: 0.8;
`;

export default function Home() {
  return (
    <Wrap>
      <Content>
        <Title>Bem-vindo ao ISMART Conecta!</Title>
        <Subtitle>
          Um espaço criado para fortalecer conexões, trocar experiências e
          crescer junto com a comunidade ISMART.
        </Subtitle>

        <ComingSoon>
          🚧 Em breve: feed, conexões, eventos e muito mais.
        </ComingSoon>
      </Content>
    </Wrap>
  );
}
