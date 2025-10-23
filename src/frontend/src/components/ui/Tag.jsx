import styled from "styled-components";

const TagWrapper = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.xs};
  font-size: 13px;
  color: ${({ theme }) => theme.colors.text};
  transition: all 0.15s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.textMuted};
  }
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.textMuted};
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  font-size: 16px;
  transition: color 0.15s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.danger};
  }
`;

export default function Tag({ children, onRemove }) {
  return (
    <TagWrapper>
      {children}
      {onRemove && (
        <RemoveButton onClick={onRemove} type="button">
          ×
        </RemoveButton>
      )}
    </TagWrapper>
  );
}