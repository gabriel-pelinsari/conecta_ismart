import { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import ThreadModal from "./ThreadModal";
import EventModal from "../Events/EventModal";
import PollModal from "../Polls/PollModal";

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
  transition: border-color 0.15s ease, box-shadow 0.15s ease;

  &::placeholder {
    color: ${({ theme }) => theme.colors.textMuted};
  }
  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
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
  & > svg {
    width: 16px;
    height: 16px;
  }
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

const ComposerColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;

const ActionButton = styled.button`
  flex: 1;
  min-width: 120px;
  padding: 10px 12px;
  border-radius: ${({ theme }) => theme.radii.md};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.bg};
  color: ${({ theme }) => theme.colors.text};
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.08s ease;

  &:hover {
    background: ${({ theme }) => theme.colors.surface};
  }

  &:active {
    transform: translateY(1px);
  }
`;

const PrimaryAction = styled(ActionButton)`
  background: ${({ theme }) => theme.colors.primary};
  border-color: ${({ theme }) => theme.colors.primary};
  color: ${({ theme }) => theme.colors.bg};
  font-size: 14px;

  &:hover {
    filter: brightness(1.05);
  }
`;

export default function ThreadComposeBar({
  onSearch,
  onCreate,
  onCreateThread,
  onCreateEvent,
  onCreatePoll,
}) {
  const [activeModal, setActiveModal] = useState(null);
  const [draft, setDraft] = useState("");

  // abre o modal ao pressionar Enter no composer
  function handleComposerKeyDown(e) {
    if (e.key === "Enter" && draft.trim().length > 0) {
      e.preventDefault();
      setActiveModal("thread");
    }
  }

  function handleSearch(e) {
    onSearch?.(e.target.value);
  }

  // foca o textarea do modal ao abrir
  const firstOpenRef = useRef(false);
  useEffect(() => {
    if (activeModal && !firstOpenRef.current) firstOpenRef.current = true;
  }, [activeModal]);

  const createThreadHandler = onCreateThread ?? onCreate;
  const closeModal = () => setActiveModal(null);

  return (
    <>
      <Bar>
        <ComposerColumn>
          <ActionButtons aria-label="Tipos de publicações disponíveis">
            <PrimaryAction type="button" onClick={() => setActiveModal("thread")}>
              + Thread
            </PrimaryAction>
            <ActionButton type="button" onClick={() => setActiveModal("event")}>
              + Evento
            </ActionButton>
            <ActionButton type="button" onClick={() => setActiveModal("poll")}>
              + Enquete
            </ActionButton>
          </ActionButtons>
        </ComposerColumn>

        <SearchBox aria-label="Buscar postagem">
          <SearchIcon>
            <svg viewBox="0 0 24 24" fill="none">
              <path
                d="M21 21l-4.2-4.2"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
              <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
            </svg>
          </SearchIcon>
          <SearchInput
            type="search"
            placeholder="Buscar por título..."
            onChange={handleSearch}
          />
        </SearchBox>
      </Bar>

      {activeModal === "thread" && (
        <ThreadModal
          initialDescription={draft}
          onClose={closeModal}
          onCreate={async (payload) => {
            await createThreadHandler?.(payload);
            setDraft("");
          }}
        />
      )}

      {activeModal === "event" && (
        <EventModal
          onClose={closeModal}
          onCreate={async (payload) => {
            await onCreateEvent?.(payload);
          }}
        />
      )}

      {activeModal === "poll" && (
        <PollModal
          onClose={closeModal}
          onCreate={async (payload) => {
            await onCreatePoll?.(payload);
          }}
        />
      )}
    </>
  );
}
