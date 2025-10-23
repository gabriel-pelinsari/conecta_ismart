import styled from "styled-components";

const Field = styled.div`
  display: grid;
  gap: 8px;
`;

const Label = styled.label`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
  outline: none;
  transition: border-color .15s ease, box-shadow .15s ease;

  &::placeholder {
    color: ${({ theme }) => theme.colors.textMuted};
  }

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(0,113,227,0.15);
  }
`;

export { Field, Label, Input };
