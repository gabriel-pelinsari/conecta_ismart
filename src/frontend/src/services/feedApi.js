import api from "../api/axios";
import { pollApi } from "./pollApi";
import { getEventCover } from "./eventCoverStore";
import { getLocalEvents } from "./eventLocalStore";

function auth() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function normalizeThread(thread) {
  return {
    type: "thread",
    ...thread,
    tags: Array.isArray(thread.tags)
      ? thread.tags
      : typeof thread.tags === "string" && thread.tags.length
      ? thread.tags.split(",").map((tag) => tag.trim()).filter(Boolean)
      : [],
  };
}

function normalizeEvent(event) {
  const cover = event.photo_url || getEventCover(event.id);
  return {
    type: "event",
    id: event.id,
    title: event.title,
    description: event.description,
    location: event.location,
    start_datetime: event.start_datetime,
    end_datetime: event.end_datetime,
    scheduled_at: event.start_datetime,
    audience: event.university ? "faculdade" : "geral",
    university: event.university,
    confirmed_count: event.participant_count ?? 0,
    creator: { user_id: event.created_by },
    created_at: event.created_at,
    photo_url: cover,
    comment: event.comment,
    user_rsvp_status: event.user_rsvp_status || null,
  };
}

function normalizePoll(poll) {
  return {
    type: "poll",
    ...poll,
    user_vote: poll.user_vote || null,
    options: (poll.options || []).map((option) =>
      typeof option === "string"
        ? { label: option, votes_count: 0 }
        : {
            label: option.label || option.text || option.title || String(option),
            votes_count: option.votes_count ?? option.vote_count ?? 0,
          }
    ),
  };
}

function sortDate(item) {
  const candidate =
    item.created_at ||
    item.start_datetime ||
    item.scheduled_at ||
    item.end_datetime ||
    new Date().toISOString();
  return new Date(candidate).getTime();
}

export const feedApi = {
  async list({ skip = 0, limit = 20, search = "", category, university } = {}) {
    const headers = auth();
    const params = new URLSearchParams();
    params.set("skip", String(skip));
    params.set("limit", String(limit));
    if (search) params.set("search", search);
    if (category) params.set("category", category);
    if (category === "faculdade" && university) {
      params.set("university", university);
    }

    let threads = [];
    let events = [];
    let eventsLoaded = false;
    let polls = [];

    try {
      const { data } = await api.get(`/api/threads/?${params.toString()}`, {
        headers,
      });
      threads = data || [];
    } catch (error) {
      console.error("Erro ao carregar threads", error);
    }

    const includeExtras = skip === 0;
    const searchTerm = search.trim().toLowerCase();

    if (includeExtras) {
      try {
        const eventParams = new URLSearchParams();
        eventParams.set("skip", "0");
        eventParams.set("limit", "10");
        if (category === "faculdade" && university) {
          eventParams.set("university", university);
        }
        eventParams.set("include_past", "false");
        const { data } = await api.get(
          `/api/events/?${eventParams.toString()}`,
          { headers }
        );
        eventsLoaded = true;
        events = (data || []).filter((event) => {
          if (category === "faculdade" && university) {
            return event.university === university;
          }
          return true;
        });
        if (searchTerm) {
          events = events.filter((event) => {
            const text = `${event.title} ${event.description || ""}`.toLowerCase();
            return text.includes(searchTerm);
          });
        }
      } catch (error) {
        console.error("Erro ao carregar eventos", error);
      }

      try {
        const storedPolls = await pollApi.list();
        polls = storedPolls.filter((poll) => {
          const scope = (poll.audience || poll.type || "geral").toLowerCase();
          if (category === "faculdade" && scope !== "faculdade") {
            return false;
          }
          if (!searchTerm) return true;
          const text = `${poll.title} ${poll.description || ""}`.toLowerCase();
          return text.includes(searchTerm);
        });
      } catch (error) {
        console.error("Erro ao carregar enquetes locais", error);
      }
    }

    const normalizedThreads = threads.map(normalizeThread);
    let normalizedEvents =
      includeExtras && eventsLoaded ? events.map(normalizeEvent) : [];

    if (includeExtras) {
      const localEvents = getLocalEvents().map(normalizeEvent);
      const remoteIds = new Set(normalizedEvents.map((event) => event.id));
      const mergedLocal = localEvents.filter((event) => !remoteIds.has(event.id));
      normalizedEvents = [...mergedLocal, ...normalizedEvents];
    }
    const normalizedPolls = includeExtras ? polls.map(normalizePoll) : [];

    const merged = [...normalizedThreads, ...normalizedEvents, ...normalizedPolls].sort(
      (a, b) => sortDate(b) - sortDate(a)
    );

    return {
      items: merged,
      threadsCount: normalizedThreads.length,
    };
  },
};

export default feedApi;
