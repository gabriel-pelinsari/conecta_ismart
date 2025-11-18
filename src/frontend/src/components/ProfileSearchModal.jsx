import { useEffect, useState } from "react";
import styled, { keyframes } from "styled-components";
import { FiSearch, FiX } from "react-icons/fi";
import { profileApi } from "../services/profileApi";

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
`;

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 120px;
  z-index: 1000;
`;

const Panel = styled.div`
  width: 100%;
  max-width: 460px;
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radii.lg};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  box-shadow: ${({ theme }) => theme.shadows.soft};
  padding: 18px 20px;
  animation: ${fadeIn} 0.15s ease;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
`;

const Title = styled.h3`
  margin: 0;
  font-size: 16px;
`;

const CloseButton = styled.button`
  border: none;
  background: transparent;
  color: ${({ theme }) => theme.colors.textMuted};
  cursor: pointer;
  font-size: 22px;
  padding: 2px;
  display: inline-flex;

  &:hover {
    color: ${({ theme }) => theme.colors.text};
  }
`;

const SearchInputWrapper = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  padding: 10px 12px;
  margin-bottom: 12px;
  background: ${({ theme }) => theme.colors.bg};
`;

const SearchIcon = styled.span`
  color: ${({ theme }) => theme.colors.textMuted};
  display: inline-flex;
`;

const SearchInput = styled.input`
  flex: 1;
  border: none;
  background: transparent;
  color: ${({ theme }) => theme.colors.text};
  outline: none;
  font-size: 14px;
`;

const List = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 320px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const ResultItem = styled.li`
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  padding: 10px 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: ${({ theme }) => theme.colors.surface};
  transition: border-color 0.15s ease, transform 0.08s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    transform: translateY(-1px);
  }
`;

const Nickname = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const Fullname = styled.span`
  font-size: 13px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const EmptyState = styled.p`
  margin: 0;
  padding: 16px 0;
  color: ${({ theme }) => theme.colors.textMuted};
  text-align: center;
  font-size: 14px;
`;

const ErrorText = styled.p`
  margin: 8px 0 0 0;
  color: ${({ theme }) => theme.colors.danger};
  font-size: 13px;
`;

export default function ProfileSearchModal({ onClose, onSelectProfile }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setResults([]);
    setQuery("");
    setError("");
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setLoading(false);
      setError("");
      return;
    }
    const handle = setTimeout(() => {
      fetchProfiles(query.trim());
    }, 350);
    return () => clearTimeout(handle);
  }, [query]);

  async function fetchProfiles(searchTerm) {
    setLoading(true);
    setError("");
    try {
      const data = await profileApi.searchByNickname(searchTerm);
      setResults(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error(err);
      setError("Não foi possível buscar perfis.");
    } finally {
      setLoading(false);
    }
  }

  function handleSelect(item) {
    const id = item?.user_id ?? item?.id;
    if (!id) return;
    onSelectProfile?.(id);
    onClose?.();
  }

  return (
    <Overlay onClick={onClose}>
      <Panel onClick={(e) => e.stopPropagation()}>
        <Header>
          <Title>Buscar perfis por nickname</Title>
          <CloseButton type="button" onClick={onClose} aria-label="Fechar busca">
            <FiX />
          </CloseButton>
        </Header>

        <SearchInputWrapper>
          <SearchIcon>
            <FiSearch aria-hidden="true" />
          </SearchIcon>
          <SearchInput
            autoFocus
            type="search"
            placeholder="Digite o nickname do usuário"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Buscar nickname"
          />
        </SearchInputWrapper>

        {error && <ErrorText>{error}</ErrorText>}

        {!error && (
          <>
            {loading && <EmptyState>Carregando...</EmptyState>}
            {!loading && results.length === 0 && query.trim() !== "" && (
              <EmptyState>Nenhum nickname encontrado.</EmptyState>
            )}
            {!loading && results.length === 0 && query.trim() === "" && (
              <EmptyState>Comece digitando para ver sugestões.</EmptyState>
            )}

            <List>
              {results.map((item) => {
                const nickname = item?.nickname || item?.username || item?.name;
                const fullName = item?.full_name || item?.display_name || item?.email;
                const key = `${item?.user_id ?? item?.id}-${nickname}`;
                return (
                  <ResultItem key={key} onClick={() => handleSelect(item)}>
                    <Nickname>{nickname}</Nickname>
                    {fullName && <Fullname>{fullName}</Fullname>}
                  </ResultItem>
                );
              })}
            </List>
          </>
        )}
      </Panel>
    </Overlay>
  );
}
