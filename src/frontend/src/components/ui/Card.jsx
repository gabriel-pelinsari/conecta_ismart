import styled from "styled-components";

const Card = styled.div`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.container};
  margin: 0 auto;
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.lg};
  box-shadow: ${({ theme }) => theme.shadows.soft};
  padding: 28px;
`;

export default Card;
