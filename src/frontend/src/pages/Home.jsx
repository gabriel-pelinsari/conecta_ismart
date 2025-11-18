import { useEffect, useState, useCallback } from "react";
import styled from "styled-components";
import ThreadComposeBar from "../components/Threads/ThreadComposeBar";
import ThreadCard from "../components/Threads/ThreadCard";
import EventCard from "../components/Events/EventCard";
import PollCard from "../components/Polls/PollCard";
import useThreads from "../hooks/useThreads";

const Page = styled.main`
  min-height: 100vh;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const Feed = styled.div`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const FiltersRow = styled.div`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 0 auto 12px auto;
`;

const FilterChip = styled.button`
  padding: 6px 14px;
  border-radius: ${({ theme }) => theme.radii.xs};
  border: 1px solid
    ${({ theme, $active }) =>
      $active ? theme.colors.primary : theme.colors.outline};
  background: ${({ theme, $active }) =>
    $active ? theme.colors.primary : theme.colors.surface};
  color: ${({ theme, $active }) =>
    $active ? theme.colors.bg : theme.colors.text};
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  opacity: ${({ disabled }) => (disabled ? 0.5 : 1)};
  pointer-events: ${({ disabled }) => (disabled ? "none" : "auto")};

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
  }
`;

const LoadingText = styled.p`
  text-align: center;
  color: ${({ theme }) => theme.colors.textMuted};
  margin: 24px 0;
`;

export default function Home() {
  const api = useThreads();
  const [search, setSearch] = useState("");
  const [debounced, setDebounced] = useState("");

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search), 400);
    return () => clearTimeout(t);
  }, [search]);

  useEffect(() => {
    api.setSearch(debounced);
  }, [debounced]);

  useEffect(() => {
    api.reload();
  }, []);

  useEffect(() => {
    function onScroll() {
      const nearBottom =
        window.innerHeight + document.documentElement.scrollTop + 200 >=
        document.documentElement.offsetHeight;
      if (nearBottom && api.hasMore && !api.loading) api.loadMore();
    }
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, [api.hasMore, api.loading]);

  const handleCreateThread = useCallback(async (data) => {
    await api.createThread(data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [api]);

  const handleCreateEvent = useCallback(async (data) => {
    await api.createEvent(data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [api]);

  const handleCreatePoll = useCallback(async (data) => {
    await api.createPoll(data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [api]);

  const renderFeedItem = (item, index) => {
    if (!item) return null;
    const baseKey =
      item.id ??
      item.uuid ??
      item.slug ??
      `${item.title || "item"}-${index}`;
    const key = `${item.type || "thread"}-${baseKey}`;

    switch (item.type) {
      case "event":
        return <EventCard key={key} event={item} />;
      case "poll":
        return <PollCard key={key} poll={item} />;
      default:
        return <ThreadCard key={key} thread={item} api={api} />;
    }
  };

  return (
    <Page>
      <ThreadComposeBar
        onSearch={setSearch}
        onCreateThread={handleCreateThread}
        onCreateEvent={handleCreateEvent}
        onCreatePoll={handleCreatePoll}
      />

      <FiltersRow>
        <FilterChip
          type="button"
          $active={api.category === "geral"}
          onClick={() => api.setCategory("geral")}
          aria-pressed={api.category === "geral"}
        >
          Geral
        </FilterChip>
        <FilterChip
          type="button"
          $active={api.category === "faculdade"}
          onClick={() => api.setCategory("faculdade")}
          aria-pressed={api.category === "faculdade"}
          disabled={api.universityLoaded && !api.userUniversity}
          title={
            api.universityLoaded && !api.userUniversity
              ? "Complete seu perfil com a universidade para usar este filtro"
              : undefined
          }
        >
          Minha faculdade
        </FilterChip>
      </FiltersRow>

      <Feed>
        {api.category === "faculdade" && !api.universityLoaded && (
          <LoadingText>Carregando sua faculdade…</LoadingText>
        )}

        {api.error && <LoadingText>{api.error}</LoadingText>}

        {api.items.length === 0 && !api.loading && !api.error && (
          <LoadingText>Nenhuma thread encontrada.</LoadingText>
        )}

        {api.items.map((item, index) => renderFeedItem(item, index))}

        {api.loading && <LoadingText>Carregando...</LoadingText>}
        {!api.hasMore && api.items.length > 0 && (
          <LoadingText>— Fim do feed —</LoadingText>
        )}
      </Feed>
    </Page>
  );
}
