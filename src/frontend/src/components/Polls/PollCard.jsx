import { useState } from "react";
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

const Option = styled.button`
  width: 100%;
  padding: 10px 12px;
  border-radius: ${({ theme }) => theme.radii.md};
  border: 1px solid
    ${({ theme, $selected }) => ($selected ? theme.colors.primary : theme.colors.outline)};
  background: ${({ theme, $selected }) =>
    $selected ? `${theme.colors.primary}22` : theme.colors.surfaceAlt || theme.colors.surface};
  text-align: left;
  cursor: pointer;
  opacity: ${({ disabled }) => (disabled ? 0.6 : 1)};
  transition: border-color 0.15s ease, background 0.15s ease;
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

const VoteNote = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.primary};
`;

export default function PollCard({ poll, onVote }) {
  const [pending, setPending] = useState(false);
  if (!poll) return null;

  const {
    title,
    description,
    options = [],
    audience,
    type,
    creator,
    votes,
    user_vote,
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

  async function handleVote(optionLabel) {
    if (!onVote || pending) return;
    const nextChoice = user_vote === optionLabel ? null : optionLabel;
    setPending(true);
    try {
      await onVote(poll.id, nextChoice);
    } finally {
      setPending(false);
    }
  }

  return (
    <Wrap>
      <Title>{title}</Title>
      {description && <Description>{description}</Description>}

      <OptionsList>
        {normalizedOptions.map((option) => {
          const percentage = totalVotes
            ? Math.round((option.votes / totalVotes) * 100)
            : 0;
          const selected = user_vote === option.label;
          return (
            <Option
              key={option.label}
              type="button"
              onClick={() => handleVote(option.label)}
              disabled={pending || !onVote}
              $selected={selected}
              aria-pressed={selected}
            >
              <OptionLabel>
                <span>{option.label}</span>
                <span>
                  {option.votes} voto{option.votes === 1 ? "" : "s"}
                </span>
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
          {totalVotes} voto{totalVotes === 1 ? "" : "s"} — Criado por {creatorName}
          {user_vote && (
            <>
              {" "}
              • <VoteNote>Seu voto: {user_vote}</VoteNote>
            </>
          )}
        </span>
        <Badge>{scopeLabel}</Badge>
      </Footer>
    </Wrap>
  );
}
