import { useEffect, useState, useCallback } from "react";
import { threadApi } from "../services/threadApi";
import { profileApi } from "../services/profileApi";

// pega universidade do perfil salvo em memória? por simplicidade,
// lemos do token e deixamos o componente decidir passar `university` quando precisar.
function decodeJWT(token) {
  try { return JSON.parse(atob(token.split(".")[1])); } catch { return null; }
}

export default function useThreads() {
  const [items, setItems] = useState([]);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("geral"); // "geral" | "faculdade"
  const [error, setError] = useState("");
  const [userUniversity, setUserUniversity] = useState(null);
  const [universityLoaded, setUniversityLoaded] = useState(false);
  const pageSize = 20;

  const currentUser = (() => {
    const t = localStorage.getItem("token");
    return t ? decodeJWT(t) : null;
  })();

  const load = useCallback(async (reset = false) => {
    if (loading) return;

    const facultyScope = category === "faculdade";

    // Aguarda saber a universidade do usuário antes de filtrar por faculdade
    if (facultyScope && !universityLoaded) {
      if (reset) {
        setItems([]);
        setSkip(0);
        setHasMore(false);
      }
      return;
    }

    // Se já carregamos o perfil e não há universidade, não há threads para mostrar
    if (facultyScope && universityLoaded && !userUniversity) {
      setItems([]);
      setSkip(0);
      setHasMore(false);
      setError("Complete seu perfil com a universidade para ver postagens da sua faculdade.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const filters = {
        skip: reset ? 0 : skip,
        limit: pageSize,
        search,
      };

      if (!facultyScope) {
        filters.category = category;
      }

      if (facultyScope && userUniversity) {
        filters.university = userUniversity;
      }

      const res = await threadApi.list(filters);

      const nextItems = reset ? res : [...items, ...res];
      setItems(nextItems);
      setSkip(reset ? res.length : skip + res.length);
      setHasMore(res.length === pageSize);
    } catch (e) {
      console.error(e);
      setError("Erro ao carregar threads");
    } finally {
      setLoading(false);
    }
  }, [category, search, skip, items, loading, userUniversity, universityLoaded]);

  // Carrega universidade do usuário logado (para filtro "faculdade")
  useEffect(() => {
    let active = true;
    async function fetchUniversity() {
      const token = localStorage.getItem("token");
      if (!token) {
        if (active) setUniversityLoaded(true);
        return;
      }
      try {
        const profile = await profileApi.getMyProfile(token);
        if (active) {
          setUserUniversity(profile?.university || null);
        }
      } catch (e) {
        console.error("Erro ao buscar universidade do usuário", e);
      } finally {
        if (active) setUniversityLoaded(true);
      }
    }
    fetchUniversity();
    return () => {
      active = false;
    };
  }, []);

  // trocar filtros / busca → recarrega
  useEffect(() => {
    load(true);
  }, [category, search, userUniversity, universityLoaded]);

  // criar
  async function createThread(payload) {
    const created = await threadApi.create(payload);
    // prepend no feed
    setItems((prev) => [created, ...prev]);
    return created;
  }

  // votar
  async function vote(threadId, value) {
    setItems((prev) =>
      prev.map((t) => {
        if (t.id !== threadId) return t;

        const previous = t.user_vote ?? 0; // voto anterior do usuário
        let newUp = t.upvotes ?? 0;
        let newDown = t.downvotes ?? 0;
        let newUserVote = value;

        if (previous === value) {
          // clicou novamente no mesmo → remove voto
          if (value === 1) newUp -= 1;
          else if (value === -1) newDown -= 1;
          newUserVote = 0;
        } else {
          // remove o anterior e adiciona o novo
          if (previous === 1) newUp -= 1;
          else if (previous === -1) newDown -= 1;

          if (value === 1) newUp += 1;
          else if (value === -1) newDown += 1;
        }

        return {
          ...t,
          upvotes: newUp,
          downvotes: newDown,
          user_vote: newUserVote,
        };
      })
    );

    // Envia pro backend (o backend já alterna também)
    try {
      await threadApi.vote(threadId, value);
    } catch (e) {
      console.error(e);
    }
  }


  async function report(threadId) {
    await threadApi.report(threadId);
    setItems((prev) =>
      prev.map((t) => (t.id === threadId ? { ...t, is_reported: true } : t))
    );
  }

  // comentários
  async function fetchComments(threadId) {
    return await threadApi.comments(threadId, { skip: 0, limit: 200 });
  }

  async function addComment(threadId, content) {
    const comment = await threadApi.addComment(threadId, content);
    // devolve para o componente anexar localmente
    return comment;
  }

  return {
    items,
    hasMore,
    loading,
    error,
    search, setSearch,
    category, setCategory,
    loadMore: () => load(false),
    reload: () => load(true),
    createThread,
    vote,
    report,
    fetchComments,
    addComment,
    currentUser,
    userUniversity,
    universityLoaded,
  };
}
