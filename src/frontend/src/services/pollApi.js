import api from "../api/axios";

function auth() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const pollApi = {
  async create({ title, description, options = [], audience = "geral" }) {
    const { data } = await api.post(
      "/polls/",
      { title, description, options, audience },
      { headers: auth() }
    );
    return data;
  },
};

export default pollApi;
