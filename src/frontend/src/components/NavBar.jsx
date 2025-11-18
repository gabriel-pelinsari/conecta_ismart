import { useState } from "react";
import styled from "styled-components";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  FiHome,
  FiUser,
  FiBell,
  FiLogOut,
  FiMoon,
  FiSun,
  FiSearch,
  FiShield,
  FiPieChart,
} from "react-icons/fi";
import ProfileSearchModal from "./ProfileSearchModal";

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

const IconButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 28px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: color 0.15s ease, transform 0.1s ease;

  &:hover {
    transform: translateY(-1px);
  }
`;

const ThemeToggleButton = styled(IconButton)`
  border-left: 1px solid ${({ theme }) => theme.colors.outline};
  padding-left: 24px;
  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const SearchButton = styled(IconButton)`
  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const LogoutButton = styled(IconButton)`
  &:hover {
    color: ${({ theme }) => theme.colors.danger};
  }
`;

export default function NavBar({ role, logout, themeName = "dark", onToggleTheme }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [searchOpen, setSearchOpen] = useState(false);

  function handleProfileSelect(userId) {
    if (!userId) return;
    navigate(`/profile/${userId}`);
  }

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
          to="/notifications"
          title="Notificações"
          aria-label="Notificações"
          $active={pathname === "/notifications"}
        >
          <FiBell />
        </StyledLink>

        <StyledLink
          to="/profile"
          title="Perfil"
          aria-label="Perfil"
          $active={pathname === "/profile"}
        >
          <FiUser />
        </StyledLink>

        {role === "admin" && (
          <>
            <StyledLink
              to="/admin/dashboard"
              title="Dashboard administrativo"
              aria-label="Dashboard administrativo"
              $active={pathname === "/admin/dashboard"}
            >
              <FiPieChart />
            </StyledLink>
            <StyledLink
              to="/admin"
              title="Admin"
              aria-label="Admin"
              $active={pathname === "/admin"}
            >
              <FiShield />
            </StyledLink>
          </>
        )}


        <SearchButton
          type="button"
          onClick={() => setSearchOpen(true)}
          title="Buscar perfis por nickname"
          aria-label="Buscar perfis por nickname"
        >
          <FiSearch />
        </SearchButton>

        {onToggleTheme && (
          <ThemeToggleButton
            type="button"
            onClick={onToggleTheme}
            title={themeName === "light" ? "Ativar modo escuro" : "Ativar modo claro"}
            aria-label={themeName === "light" ? "Ativar modo escuro" : "Ativar modo claro"}
          >
            {themeName === "light" ? <FiMoon /> : <FiSun />}
          </ThemeToggleButton>
        )}

        <LogoutButton onClick={logout} title="Sair" aria-label="Sair">
          <FiLogOut />
        </LogoutButton>
      </NavLinks>

      {searchOpen && (
        <ProfileSearchModal
          onClose={() => setSearchOpen(false)}
          onSelectProfile={handleProfileSelect}
        />
      )}
    </Bar>
  );
}
