import api from "../api/axios";

function auth() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const eventApi = {
  async create({
    title,
    description,
    location,
    scheduled_at,
    audience = "geral",
    comment,
    photo,
  }) {
    const payload = new FormData();
    if (title) payload.append("title", title);
    if (description) payload.append("description", description);
    if (location) payload.append("location", location);
    if (scheduled_at) payload.append("scheduled_at", scheduled_at);
    if (audience) payload.append("audience", audience);
    if (comment) payload.append("comment", comment);
    if (photo) payload.append("photo", photo);

    const { data } = await api.post("/events/", payload, {
      headers: auth(),
    });
    return data;
  },
};

export default eventApi;
