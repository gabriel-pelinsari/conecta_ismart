import { useEffect, useState, useCallback } from "react";
import { threadApi } from "../services/threadApi";
import { profileApi } from "../services/profileApi";
import { feedApi } from "../services/feedApi";
import { eventApi } from "../services/eventApi";
import { pollApi } from "../services/pollApi";
import { saveEventCover } from "../services/eventCoverStore";
import { saveLocalEvent } from "../services/eventLocalStore";

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
        category,
        university: facultyScope ? userUniversity : undefined,
      };

      const response = await feedApi.list(filters);
      const normalized = response.items.map(normalizeFeedItem);
      const threadsCount =
        typeof response.threadsCount === "number"
          ? response.threadsCount
          : normalized.filter((item) => item.type === "thread").length;

      const nextItems = reset ? normalized : [...items, ...normalized];
      setItems(nextItems);
      setSkip(reset ? threadsCount : skip + threadsCount);
      setHasMore(threadsCount === pageSize);
    } catch (e) {
      console.error(e);
      setError("Erro ao carregar publica��es");
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
    const normalized = normalizeFeedItem({ type: "thread", ...created });
    // prepend no feed
    setItems((prev) => [normalized, ...prev]);
    return normalized;
  }

  async function createEvent(payload) {
    if (!payload?.scheduled_at) {
      throw new Error("Informe a data e o horário do evento.");
    }
    const wantsFacultyScope = payload.audience === "faculdade";
    if (wantsFacultyScope && !userUniversity) {
      throw new Error(
        "Atualize seu perfil com a universidade para criar eventos da sua faculdade."
      );
    }

    const startDate = new Date(payload.scheduled_at);
    if (Number.isNaN(startDate.getTime())) {
      throw new Error("Data do evento inválida.");
    }

    const endDate = payload.end_datetime
      ? new Date(payload.end_datetime)
      : new Date(startDate.getTime() + (payload.duration_hours || 2) * 60 * 60 * 1000);

    const description = payload.comment
      ? [payload.description, `Observação: ${payload.comment}`]
          .filter(Boolean)
          .join("\n\n")
      : payload.description;

    const requestBody = {
      title: payload.title,
      description,
      event_type: payload.event_type || "meetup",
      start_datetime: startDate.toISOString(),
      end_datetime: endDate.toISOString(),
      location: payload.location,
      is_online: Boolean(payload.is_online) || false,
      online_link: payload.online_link || null,
      university: wantsFacultyScope ? userUniversity : payload.university || null,
      max_participants: payload.max_participants
        ? Number(payload.max_participants)
        : undefined,
    };

    const created = await eventApi.create(requestBody);
    if (payload.photo_data_url) {
      saveEventCover(created.id, payload.photo_data_url);
      created.photo_url = payload.photo_data_url;
    }
    saveLocalEvent({
      ...created,
      photo_url: created.photo_url || payload.photo_data_url || null,
    });
    const normalized = normalizeFeedItem({ type: "event", ...created });
    setItems((prev) => [normalized, ...prev]);
    return normalized;
  }

  async function createPoll(payload) {
    const created = await pollApi.create(payload);
    const normalized = normalizeFeedItem({ type: "poll", ...created });
    setItems((prev) => [normalized, ...prev]);
    return normalized;
  }

  // votar
  async function vote(threadId, value) {
    setItems((prev) =>
      prev.map((t) => {
        if (t.type !== "thread" || t.id !== threadId) return t;

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
      prev.map((t) =>
        t.type === "thread" && t.id === threadId ? { ...t, is_reported: true } : t
      )
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

  async function deleteThread(threadId) {
    try {
      await threadApi.remove(threadId);
      setItems((prev) =>
        prev.filter((t) => !(t.type === "thread" && t.id === threadId))
      );
    } catch (e) {
      console.error("Erro ao excluir thread", e);
      throw e;
    }
  }

  async function rsvpEvent(eventId, status) {
    if (!eventId || !status) return;
    let previousStatus = null;
    setItems((prev) =>
      prev.map((item) => {
        if (item.type !== "event" || item.id !== eventId) return item;
        previousStatus = item.user_rsvp_status || null;
        let confirmed = item.confirmed_count || 0;
        if (previousStatus === "confirmed" && status !== "confirmed") {
          confirmed = Math.max(0, confirmed - 1);
        } else if (status === "confirmed" && previousStatus !== "confirmed") {
          confirmed += 1;
        }
        return {
          ...item,
          user_rsvp_status: status,
          confirmed_count: confirmed,
        };
      })
    );

    try {
      await eventApi.rsvp(eventId, status);
    } catch (e) {
      console.error(e);
      // revert optimistic update
      setItems((prev) =>
        prev.map((item) => {
          if (item.type !== "event" || item.id !== eventId) return item;
          let confirmed = item.confirmed_count || 0;
          if (item.user_rsvp_status === "confirmed" && previousStatus !== "confirmed") {
            confirmed = Math.max(0, confirmed - 1);
          } else if (
            previousStatus === "confirmed" &&
            item.user_rsvp_status !== "confirmed"
          ) {
            confirmed += 1;
          }
          return {
            ...item,
            user_rsvp_status: previousStatus,
            confirmed_count: confirmed,
          };
        })
      );
      throw e;
    }
  }

  async function votePoll(pollId, optionLabel) {
    if (!pollId) return null;
    const updated = await pollApi.vote(pollId, optionLabel);
    const normalized = normalizeFeedItem({ type: "poll", ...updated });
    setItems((prev) =>
      prev.map((item) =>
        item.type === "poll" && item.id === pollId ? normalized : item
      )
    );
    return normalized;
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
    createEvent,
    createPoll,
    vote,
    report,
    fetchComments,
    addComment,
    deleteThread,
    rsvpEvent,
    votePoll,
    currentUser,
    userUniversity,
    universityLoaded,
  };
}

function normalizeFeedItem(item) {
  if (!item) return item;
  const type =
    item.type ||
    (item.thread ? "thread" : item.event ? "event" : item.poll ? "poll" : "thread");

  const payload = item[type] ? item[type] : { ...item };

  if (type === "thread") {
    const tags = Array.isArray(payload.tags)
      ? payload.tags
      : typeof payload.tags === "string" && payload.tags.length
      ? payload.tags.split(",").map((tag) => tag.trim()).filter(Boolean)
      : [];

    return {
      type: "thread",
      ...payload,
      tags,
      author: payload.author || payload.user || {},
      top_comments: (payload.top_comments || []).map((comment) => ({
        ...comment,
        author: comment.author || {},
      })),
    };
  }

  if (type === "event") {
    return {
      type: "event",
      id: payload.id,
      title: payload.title,
      description: payload.description,
      location: payload.location,
      scheduled_at: payload.scheduled_at || payload.start_datetime,
      start_datetime: payload.start_datetime || payload.scheduled_at,
      end_datetime: payload.end_datetime,
      audience:
        payload.university || payload.audience === "faculdade"
          ? "faculdade"
          : payload.audience || "geral",
      university: payload.university,
      confirmed_count:
        payload.confirmed_count ??
        payload.participant_count ??
        payload.confirmed_people?.length ??
        payload.confirmed_users?.length ??
        0,
      creator: payload.creator || { user_id: payload.created_by },
      created_at: payload.created_at,
      comment: payload.comment,
      photo_url: payload.photo_url || payload.photo,
      user_rsvp_status: payload.user_rsvp_status || null,
    };
  }

  if (type === "poll") {
    return {
      type: "poll",
      id: payload.id,
      title: payload.title,
      description: payload.description,
      audience: payload.audience || payload.type || "geral",
      options: (payload.options || []).map((option) =>
        typeof option === "string"
          ? { label: option, votes_count: 0 }
          : {
              label: option.label || option.text || option.title || String(option),
              votes_count:
                option.votes_count ??
                option.vote_count ??
                option.votes?.length ??
                0,
            }
      ),
      creator: payload.creator || {},
      votes: payload.votes,
      created_at: payload.created_at,
      user_vote: payload.user_vote || null,
    };
  }

  return { type, ...payload };
}
