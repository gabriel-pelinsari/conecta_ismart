import styled from "styled-components";

const Button = styled.button`
  width: 100%;
  padding: 12px 14px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
  border-radius: ${({ theme }) => theme.radii.sm};
  cursor: pointer;
  transition: transform .06s ease, border-color .15s ease, background .15s ease;
  will-change: transform;

  &:hover {
    border-color: ${({ theme }) => theme.colors.textMuted};
  }
  &:active {
    transform: translateY(1px);
  }
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

export default Button;
