import api from "../api/axios";

function auth() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function buildParams(params = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    searchParams.set(key, String(value));
  });
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

export const pollApi = {
  async list({ audience, skip = 0, limit = 20 } = {}) {
    const query = buildParams({ audience, skip, limit });
    const { data } = await api.get(`/api/polls/${query}`, {
      headers: auth(),
    });
    return data;
  },

  async create({ title, description, audience = "geral", options = [] }) {
    const payload = {
      title,
      description,
      audience,
      options,
    };
    const { data } = await api.post("/api/polls/", payload, {
      headers: {
        ...auth(),
        "Content-Type": "application/json",
      },
    });
    return data;
  },

  async vote(pollId, optionLabel) {
    const { data } = await api.post(
      `/api/polls/${pollId}/vote`,
      { option_label: optionLabel },
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

export default pollApi;
