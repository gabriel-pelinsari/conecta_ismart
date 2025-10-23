import styled from "styled-components";
import { Link, useLocation } from "react-router-dom";

const Bar = styled.nav`
  position: sticky;
  top: 0;
  width: 100%;
  background: ${({ theme }) => theme.colors.surface};
  border-bottom: 1px solid ${({ theme }) => theme.colors.outline};
  padding: 10px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 10;
`;

const Logo = styled(Link)`
  font-weight: 600;
  font-size: 17px;
  color: ${({ theme }) => theme.colors.text};
  letter-spacing: -0.01em;
  &:hover {
    opacity: 0.8;
  }
`;

const NavLinks = styled.div`
  display: flex;
  align-items: center;
  gap: 22px;
`;

const StyledLink = styled(Link)`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 15px;
  position: relative;
  transition: color 0.15s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.text};
  }

  ${({ $active, theme }) =>
    $active &&
    `
    color: ${theme.colors.text};
    &::after {
      content: '';
      position: absolute;
      bottom: -5px;
      left: 0;
      right: 0;
      height: 2px;
      border-radius: 1px;
      background: ${theme.colors.primary};
    }
  `}
`;

const LogoutButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 15px;
  cursor: pointer;
  transition: color 0.15s ease, opacity 0.15s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.text};
    opacity: 0.8;
  }
`;

export default function NavBar({ role, logout }) {
  const { pathname } = useLocation();

  return (
    <Bar>
      <Logo to="/home">ISMART Conecta</Logo>

      <NavLinks>
        <StyledLink to="/home" $active={pathname === "/home"}>
          Início
        </StyledLink>

        {role === "admin" && (
          <StyledLink to="/admin" $active={pathname === "/admin"}>
            Admin
          </StyledLink>
        )}

        <LogoutButton onClick={logout}>Sair</LogoutButton>
      </NavLinks>
    </Bar>
  );
}
