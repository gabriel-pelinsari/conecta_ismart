import styled from "styled-components";
import Card from "../ui/Card";

const Wrap = styled(Card)`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  margin: 0 auto 12px auto;
  padding: 20px 22px;
`;

const Title = styled.h3`
  margin: 0;
  font-size: 18px;
  color: ${({ theme }) => theme.colors.text};
`;

const Description = styled.p`
  margin: 8px 0 16px 0;
  color: ${({ theme }) => theme.colors.text};
  line-height: 1.5;
`;

const OptionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const Option = styled.div`
  background: ${({ theme }) => theme.colors.surfaceAlt || theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  padding: 10px 12px;
`;

const OptionLabel = styled.div`
  display: flex;
  justify-content: space-between;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
  margin-bottom: 6px;
`;

const Progress = styled.div`
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: ${({ theme }) => theme.colors.outline};
  overflow: hidden;
`;

const ProgressFill = styled.span`
  display: block;
  height: 100%;
  background: ${({ theme }) => theme.colors.primary};
  width: ${({ $value }) => $value}%;
`;

const Footer = styled.div`
  margin-top: 12px;
  font-size: 13px;
  color: ${({ theme }) => theme.colors.textMuted};
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 6px;
`;

const Badge = styled.span`
  padding: 4px 10px;
  border-radius: ${({ theme }) => theme.radii.xs};
  background: ${({ theme }) => theme.colors.primary}22;
  color: ${({ theme }) => theme.colors.primary};
  font-size: 12px;
  font-weight: 600;
`;

export default function PollCard({ poll }) {
  if (!poll) return null;

  const {
    title,
    description,
    options = [],
    audience,
    type,
    creator,
    votes,
  } = poll;

  const normalizedOptions = options.map((option) => {
    if (typeof option === "string") {
      const voteCount = votes?.filter((v) => v === option)?.length ?? 0;
      return { label: option, votes: voteCount };
    }
    return {
      label: option.label || option.text || option.title,
      votes:
        option.votes_count ??
        option.vote_count ??
        option.votes?.length ??
        0,
    };
  });

  const totalVotes =
    normalizedOptions.reduce((acc, option) => acc + (option.votes || 0), 0) || 0;
  const creatorName =
    creator?.nickname || creator?.full_name || creator?.name || "Criador";
  const scopeLabel =
    (audience || type || "").toLowerCase() === "faculdade"
      ? "Faculdade específica"
      : "Geral";

  return (
    <Wrap>
      <Title>{title}</Title>
      {description && <Description>{description}</Description>}

      <OptionsList>
        {normalizedOptions.map((option) => {
          const percentage = totalVotes
            ? Math.round((option.votes / totalVotes) * 100)
            : 0;
          return (
            <Option key={option.label}>
              <OptionLabel>
                <span>{option.label}</span>
                <span>{option.votes} voto{option.votes === 1 ? "" : "s"}</span>
              </OptionLabel>
              <Progress aria-hidden="true">
                <ProgressFill $value={percentage} />
              </Progress>
            </Option>
          );
        })}
      </OptionsList>

      <Footer>
        <span>
          {totalVotes} voto{totalVotes === 1 ? "" : "s"} • Criado por {creatorName}
        </span>
        <Badge>{scopeLabel}</Badge>
      </Footer>
    </Wrap>
  );
}
