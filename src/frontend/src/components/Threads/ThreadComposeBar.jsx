import { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import ThreadModal from "./ThreadModal";

const Bar = styled.div`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  margin: 8px auto 16px auto;
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.lg};
  padding: 12px;
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 12px;

  @media (max-width: ${({ theme }) => theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
  }
`;

const ComposerInput = styled.input`
  width: 100%;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.md};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.bg};
  color: ${({ theme }) => theme.colors.text};
  outline: none;
  transition: border-color .15s ease, box-shadow .15s ease;

  &::placeholder { color: ${({ theme }) => theme.colors.textMuted}; }
  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(0,113,227,0.15);
  }
`;

const SearchBox = styled.label`
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.md};
  padding: 0 12px;
  background: ${({ theme }) => theme.colors.bg};
`;

const SearchIcon = styled.span`
  display: inline-flex;
  width: 16px;
  height: 16px;
  color: ${({ theme }) => theme.colors.textMuted};
  & > svg { width: 16px; height: 16px; }
`;

const SearchInput = styled.input`
  flex: 1;
  height: 40px;
  border: none;
  outline: none;
  background: transparent;
  color: ${({ theme }) => theme.colors.text};
  font-size: 14px;
`;

export default function ThreadComposeBar({ onSearch, onCreate }) {
  const [isOpen, setIsOpen] = useState(false);
  const [draft, setDraft] = useState("");

  // abre o modal ao pressionar Enter no composer
  function handleComposerKeyDown(e) {
    if (e.key === "Enter" && draft.trim().length > 0) {
      e.preventDefault();
      setIsOpen(true);
    }
  }

  function handleSearch(e) {
    onSearch?.(e.target.value);
  }

  // foca o textarea do modal ao abrir
  const firstOpenRef = useRef(false);
  useEffect(() => {
    if (isOpen && !firstOpenRef.current) firstOpenRef.current = true;
  }, [isOpen]);

  return (
    <>
      <Bar>
        <ComposerInput
          placeholder="Compartilhe uma dúvida ou comece uma conversa…"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleComposerKeyDown}
          aria-label="Criar nova thread"
        />

        <SearchBox aria-label="Buscar threads">
          <SearchIcon>
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M21 21l-4.2-4.2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </SearchIcon>
          <SearchInput
            type="search"
            placeholder="Buscar por título…"
            onChange={handleSearch}
          />
        </SearchBox>
      </Bar>

      {isOpen && (
        <ThreadModal
          initialDescription={draft}
          onClose={() => setIsOpen(false)}
          onCreate={async (payload) => {
            await onCreate?.(payload);
            setDraft("");
          }}
        />
      )}
    </>
  );
}
