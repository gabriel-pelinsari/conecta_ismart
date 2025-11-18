import api from "../api/axios";
import mockProfiles from "../mocks/profiles";

export const profileApi = {
  /**
   * Busca o perfil do usuário logado
   */
  getMyProfile: async (token) => {
    const response = await api.get("/profiles/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  /**
   * Busca perfil de outro usuário
   */
  getProfile: async (userId, token) => {
    const response = await api.get(`/profiles/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  /**
   * Atualiza o perfil do usuário logado
   */
  updateProfile: async (token, data) => {
    const response = await api.put("/profiles/me", data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  /**
   * Faz upload de foto de perfil
   */
  uploadPhoto: async (token, file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/profiles/me/photo", formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  /**
   * Lista todos os interesses disponíveis
   */
  getAllInterests: async (token) => {
    const response = await api.get("/interests/", {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  /**
   * Lista interesses do usuário logado
   */
  getMyInterests: async (token) => {
    const response = await api.get("/interests/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  /**
   * Adiciona um interesse ao usuário
   */
  addInterest: async (token, interestId) => {
    const response = await api.post(`/interests/me/${interestId}`, {}, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  /**
   * Remove um interesse do usuário
   */
  removeInterest: async (token, interestId) => {
    await api.delete(`/interests/me/${interestId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  addFriend: async (token, userId) => {
    const response = await api.post(
      `/profiles/${userId}/friendship`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  },

  respondFriend: async (token, userId, accept) => {
    const response = await api.post(
      `/profiles/${userId}/friendship/respond`,
      {},
      {
        headers: { Authorization: `Bearer ${token}` },
        params: { accept },
      }
    );
    return response.data;
  },

  listUsers: async (token) => {
    const response = await api.get("/profiles/users", {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  createUser: async (token, payload) => {
    const response = await api.post("/profiles/users", payload, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  updateUser: async (token, userId, payload) => {
    const response = await api.put(`/profiles/users/${userId}`, payload, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  deleteUser: async (token, userId) => {
    await api.delete(`/profiles/users/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  searchByNickname: async (nickname) => {
    if (!nickname) return [];
    const term = nickname.toLowerCase();
    const results = mockProfiles.filter((profile) =>
      profile.nickname.toLowerCase().includes(term)
    );

    return new Promise((resolve) => {
      setTimeout(() => resolve(results), 200);
    });
  },
};
