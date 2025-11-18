import api from "../api/axios";

function auth() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const eventApi = {
  async list({
    skip = 0,
    limit = 10,
    university,
    includePast = false,
  } = {}) {
    const params = new URLSearchParams();
    params.set("skip", String(skip));
    params.set("limit", String(limit));
    if (university) params.set("university", university);
    if (includePast) params.set("include_past", "true");

    const { data } = await api.get(`/api/events/?${params.toString()}`, {
      headers: auth(),
    });
    return data;
  },

  async create(payload) {
    const { data } = await api.post("/api/events/", payload, {
      headers: {
        ...auth(),
        "Content-Type": "application/json",
      },
    });
    return data;
  },

  async rsvp(eventId, status) {
    const { data } = await api.post(
      `/api/events/${eventId}/rsvp`,
      { status },
      {
        headers: {
          ...auth(),
          "Content-Type": "application/json",
        },
      }
    );
    return data;
  },
};

export default eventApi;
