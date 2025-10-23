import styled from "styled-components";
import { useInterests } from "../../hooks/useInterests";
import Tag from "../ui/Tag";
import Button from "../ui/Button";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const Section = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const SectionTitle = styled.h3`
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.textMuted};
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const TagsGrid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const AvailableInterest = styled.button`
  padding: 6px 12px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
  border-radius: ${({ theme }) => theme.radii.xs};
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    color: ${({ theme }) => theme.colors.primary};
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const EmptyState = styled.div`
  font-size: 13px;
  color: ${({ theme }) => theme.colors.textMuted};
  font-style: italic;
`;

const ErrorBox = styled.div`
  padding: 10px 12px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.sm};
  color: ${({ theme }) => theme.colors.danger};
  background: rgba(255, 59, 48, 0.08);
  font-size: 12px;
`;

export default function InterestManager({ editable = false }) {
  const {
    allInterests,
    myInterests,
    loading,
    error,
    addInterest,
    removeInterest,
  } = useInterests();

  const myInterestIds = myInterests.map((i) => i.id);
  const availableInterests = allInterests.filter(
    (i) => !myInterestIds.includes(i.id)
  );

  async function handleAddInterest(interestId) {
    try {
      await addInterest(interestId);
    } catch (err) {
      console.error("Erro ao adicionar interesse:", err);
    }
  }

  async function handleRemoveInterest(interestId) {
    try {
      await removeInterest(interestId);
    } catch (err) {
      console.error("Erro ao remover interesse:", err);
    }
  }

  if (loading) {
    return <EmptyState>Carregando interesses...</EmptyState>;
  }

  return (
    <Container>
      {/* Meus interesses */}
      <Section>
        <SectionTitle>Seus interesses</SectionTitle>
        {myInterests.length > 0 ? (
          <TagsGrid>
            {myInterests.map((interest) => (
              <Tag
                key={interest.id}
                onRemove={
                  editable
                    ? () => handleRemoveInterest(interest.id)
                    : undefined
                }
              >
                {interest.name}
              </Tag>
            ))}
          </TagsGrid>
        ) : (
          <EmptyState>Você ainda não adicionou interesses</EmptyState>
        )}
      </Section>

      {/* Adicionar interesses */}
      {editable && availableInterests.length > 0 && (
        <Section>
          <SectionTitle>Adicionar interesses</SectionTitle>
          <TagsGrid>
            {availableInterests.map((interest) => (
              <AvailableInterest
                key={interest.id}
                onClick={() => handleAddInterest(interest.id)}
              >
                + {interest.name}
              </AvailableInterest>
            ))}
          </TagsGrid>
        </Section>
      )}

      {error && <ErrorBox>{error}</ErrorBox>}
    </Container>
  );
}