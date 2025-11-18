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
  FiMenu,
  FiX,
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

  @media (max-width: 768px) {
    padding: 12px 16px;
  }
`;

const Logo = styled(Link)`
  font-weight: 600;
  font-size: 17px;
  color: ${({ theme }) => theme.colors.text};
  letter-spacing: -0.01em;
  &:hover {
    opacity: 0.8;
  }

  @media (max-width: 768px) {
    font-size: 16px;
  }
`;

const NavLinks = styled.div`
  display: flex;
  align-items: center;
  gap: 28px;

  @media (max-width: 768px) {
    display: none;
  }
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

const MobileMenuButton = styled(IconButton)`
  display: none;

  @media (max-width: 768px) {
    display: flex;
    font-size: 24px;
  }

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const MobileMenu = styled.div`
  display: none;

  @media (max-width: 768px) {
    display: ${({ $isOpen }) => ($isOpen ? "flex" : "none")};
    position: fixed;
    top: 57px;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${({ theme }) => theme.colors.surface};
    flex-direction: column;
    padding: 20px;
    gap: 24px;
    z-index: 9;
    border-top: 1px solid ${({ theme }) => theme.colors.outline};
    animation: slideDown 0.2s ease-out;

    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  }
`;

const MobileNavItem = styled(Link)`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 16px;
  transition: all 0.15s ease;

  svg {
    font-size: 24px;
  }

  &:hover {
    background: ${({ theme }) => theme.colors.outline};
    color: ${({ theme }) => theme.colors.text};
  }

  ${({ $active, theme }) =>
    $active &&
    `
    color: ${theme.colors.primary};
    background: ${theme.colors.outline};
  `}
`;

const MobileButton = styled.button`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 16px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;

  svg {
    font-size: 24px;
  }

  &:hover {
    background: ${({ theme }) => theme.colors.outline};
    color: ${({ theme }) => theme.colors.text};
  }
`;

const MobileDivider = styled.div`
  height: 1px;
  background: ${({ theme }) => theme.colors.outline};
  margin: 8px 0;
`;

export default function NavBar({ role, logout, themeName = "dark", onToggleTheme }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [searchOpen, setSearchOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  function handleProfileSelect(userId) {
    if (!userId) return;
    navigate(`/profile/${userId}`);
    setMobileMenuOpen(false);
  }

  function handleMobileNavClick() {
    setMobileMenuOpen(false);
  }

  return (
    <Bar>
      <Logo to="/home">Conecta</Logo>

      <MobileMenuButton
        type="button"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        aria-label={mobileMenuOpen ? "Fechar menu" : "Abrir menu"}
      >
        {mobileMenuOpen ? <FiX /> : <FiMenu />}
      </MobileMenuButton>

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

      <MobileMenu $isOpen={mobileMenuOpen}>
        <MobileNavItem
          to="/home"
          $active={pathname === "/home"}
          onClick={handleMobileNavClick}
        >
          <FiHome />
          <span>Início</span>
        </MobileNavItem>

        <MobileNavItem
          to="/notifications"
          $active={pathname === "/notifications"}
          onClick={handleMobileNavClick}
        >
          <FiBell />
          <span>Notificações</span>
        </MobileNavItem>

        <MobileNavItem
          to="/profile"
          $active={pathname === "/profile"}
          onClick={handleMobileNavClick}
        >
          <FiUser />
          <span>Perfil</span>
        </MobileNavItem>

        {role === "admin" && (
          <>
            <MobileNavItem
              to="/admin/dashboard"
              $active={pathname === "/admin/dashboard"}
              onClick={handleMobileNavClick}
            >
              <FiPieChart />
              <span>Dashboard</span>
            </MobileNavItem>

            <MobileNavItem
              to="/admin"
              $active={pathname === "/admin"}
              onClick={handleMobileNavClick}
            >
              <FiShield />
              <span>Admin</span>
            </MobileNavItem>
          </>
        )}

        <MobileDivider />

        <MobileButton
          type="button"
          onClick={() => {
            setSearchOpen(true);
            setMobileMenuOpen(false);
          }}
        >
          <FiSearch />
          <span>Buscar perfis</span>
        </MobileButton>

        {onToggleTheme && (
          <MobileButton
            type="button"
            onClick={() => {
              onToggleTheme();
              setMobileMenuOpen(false);
            }}
          >
            {themeName === "light" ? <FiMoon /> : <FiSun />}
            <span>{themeName === "light" ? "Modo escuro" : "Modo claro"}</span>
          </MobileButton>
        )}

        <MobileButton
          onClick={() => {
            logout();
            setMobileMenuOpen(false);
          }}
        >
          <FiLogOut />
          <span>Sair</span>
        </MobileButton>
      </MobileMenu>

      {searchOpen && (
        <ProfileSearchModal
          onClose={() => setSearchOpen(false)}
          onSelectProfile={handleProfileSelect}
        />
      )}
    </Bar>
  );
}
