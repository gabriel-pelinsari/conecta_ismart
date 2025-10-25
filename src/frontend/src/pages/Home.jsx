import { useEffect, useState, useCallback } from "react";
import styled from "styled-components";
import ThreadComposeBar from "../components/Threads/ThreadComposeBar";
import ThreadCard from "../components/Threads/ThreadCard";
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

  const handleCreate = useCallback(async (data) => {
    await api.createThread(data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [api]);

  return (
    <Page>
      <ThreadComposeBar onSearch={setSearch} onCreate={handleCreate} />
      <Feed>
        {api.items.length === 0 && !api.loading && (
          <LoadingText>Nenhuma thread encontrada.</LoadingText>
        )}

        {api.items.map((t) => (
          <ThreadCard key={t.id} thread={t} api={api} />
        ))}

        {api.loading && <LoadingText>Carregando...</LoadingText>}
        {!api.hasMore && api.items.length > 0 && (
          <LoadingText>— Fim do feed —</LoadingText>
        )}
      </Feed>
    </Page>
  );
}
