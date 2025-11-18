import api from "../api/axios";

function auth() {
  const token = localStorage.getItem("token");
  return { Authorization: `Bearer ${token}` };
}

export const threadApi = {
  comments: async (threadId) => {
    const res = await api.get(`/threads/${threadId}/comments`);
    return res.data;
  },

  addComment: async (threadId, content) => {
    const res = await api.post(`/threads/${threadId}/comments`, { content });
    return res.data;
  },

  async list({ skip = 0, limit = 20, search = "", category, university, tag }) {
    const params = new URLSearchParams();
    params.set("skip", String(skip));
    params.set("limit", String(limit));
    if (search) params.set("search", search);
    if (category && category !== "todos") params.set("category", category);
    if (university) params.set("university", university);
    if (tag) params.set("tag", tag); 

    const { data } = await api.get(`/threads?${params.toString()}`, {
      headers: auth(),
    });
    return data;
  },

  async create({ title, description, category, tags }) {
    const { data } = await api.post(
      "/threads/",
      { title, description, category, tags },
      { headers: auth() }
    );
    return data;
  },

  async vote(threadId, value) {
    const { data } = await api.post(
      `/threads/${threadId}/vote`,
      { value },
      { headers: auth() }
    );
    return data;
  },

  async report(threadId) {
    const { data } = await api.post(
      `/threads/${threadId}/report`,
      {},
      { headers: auth() }
    );
    return data;
  },

  async comments(threadId, { skip = 0, limit = 50 } = {}) {
    const params = new URLSearchParams();
    params.set("skip", String(skip));
    params.set("limit", String(limit));
    const { data } = await api.get(
      `/threads/${threadId}/comments?${params.toString()}`,
      { headers: auth() }
    );
    return data; // CommentOut[]
  },

  async addComment(threadId, content) {
    const { data } = await api.post(
      `/threads/${threadId}/comments`,
      { content },
      { headers: auth() }
    );
    return data; // CommentOut
  },

  async remove(threadId) {
    await api.delete(`/threads/${threadId}`, { headers: auth() });
  },

  async voteComment(commentId, value) {
    const { data } = await api.post(
      `/threads/comments/${commentId}/vote`,
      { value },
      { headers: auth() }
    );
    return data;
  },
};

export default threadApi;
