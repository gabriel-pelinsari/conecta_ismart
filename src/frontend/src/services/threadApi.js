import api from "../api/axios";

function auth() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function buildQuery(params = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    searchParams.set(key, String(value));
  });
  return searchParams.toString();
}

export const threadApi = {
  async list({ skip = 0, limit = 20, search, category, university, tag } = {}) {
    const query = buildQuery({
      skip,
      limit,
      search,
      category,
      university,
      tag,
    });
    const { data } = await api.get(`/api/threads/?${query}`, {
      headers: auth(),
    });
    return data;
  },

  async create({ title, description, category, tags }) {
    const { data } = await api.post(
      "/api/threads/",
      { title, description, category, tags },
      { headers: auth() }
    );
    return data;
  },

  async vote(threadId, value) {
    const { data } = await api.post(
      `/api/threads/${threadId}/vote`,
      { value },
      { headers: auth() }
    );
    return data;
  },

  async report(threadId) {
    const { data } = await api.post(
      `/api/threads/${threadId}/report`,
      {},
      { headers: auth() }
    );
    return data;
  },

  async remove(threadId) {
    await api.delete(`/api/threads/${threadId}/`, { headers: auth() });
  },

  async comments(threadId, { skip = 0, limit = 50 } = {}) {
    const query = buildQuery({ skip, limit });
    const { data } = await api.get(
      `/api/threads/${threadId}/comments/?${query}`,
      { headers: auth() }
    );
    return data;
  },

  async addComment(threadId, content) {
    const { data } = await api.post(
      `/api/threads/${threadId}/comments/`,
      { content },
      { headers: auth() }
    );
    return data;
  },

  async voteComment(commentId, value) {
    const { data } = await api.post(
      `/api/threads/comments/${commentId}/vote`,
      { value },
      { headers: auth() }
    );
    return data;
  },
};

export default threadApi;
