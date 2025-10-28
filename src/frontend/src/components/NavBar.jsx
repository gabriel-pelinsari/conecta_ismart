import styled from "styled-components";
import { Link, useLocation } from "react-router-dom";
import { FiHome, FiUser, FiBell, FiLogOut } from "react-icons/fi";

const Bar = styled.nav`
  position: sticky;
  top: 0;
  width: 100%;
  background: ${({ theme }) => theme.colors.surface};
  border-bottom: 1px solid ${({ theme }) => theme.colors.outline};
  padding: 14px 24px;
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
  gap: 28px;
`;

const StyledLink = styled(Link)`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 28px;
  position: relative;
  transition: color 0.15s ease, transform 0.1s ease;
  display: flex;
  align-items: center;

  &:hover {
    color: ${({ theme }) => theme.colors.text};
    transform: translateY(-1px);
  }

  ${({ $active, theme }) =>
    $active &&
    `
    color: ${theme.colors.primary};
  `}
`;

const LogoutButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 28px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: color 0.15s ease, transform 0.1s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.danger};
    transform: translateY(-1px);
  }
`;

export default function NavBar({ role, logout }) {
  const { pathname } = useLocation();

  return (
    <Bar>
      <Logo to="/home">Conecta</Logo>

      <NavLinks>
        <StyledLink
          to="/home"
          title="Início"
          aria-label="Início"
          $active={pathname === "/home"}
        >
          <FiHome />
        </StyledLink>

        <StyledLink
          to="/profile"
          title="Perfil"
          aria-label="Perfil"
          $active={pathname === "/profile"}
        >
          <FiUser />
        </StyledLink>

        <StyledLink
          to="/notifications"
          title="Notificações"
          aria-label="Notificações"
          $active={pathname === "/notifications"}
        >
          <FiBell />
        </StyledLink>

        {role === "admin" && (
          <StyledLink
            to="/admin"
            title="Admin"
            aria-label="Admin"
            $active={pathname === "/admin"}
          >
            🛠
          </StyledLink>
        )}

        <LogoutButton onClick={logout} title="Sair" aria-label="Sair">
          <FiLogOut />
        </LogoutButton>
      </NavLinks>
    </Bar>
  );
}
