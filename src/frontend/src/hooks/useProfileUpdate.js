import { useState } from "react";
import { profileApi } from "../services/profileApi";

export function useProfileUpdate() {
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);

  async function updateProfile(data) {
    try {
      setUpdating(true);
      setError(null);

      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Token não encontrado");
      }

      const result = await profileApi.updateProfile(token, data);
      return result;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || "Erro ao atualizar perfil";
      setError(errorMsg);
      throw err;
    } finally {
      setUpdating(false);
    }
  }

  return { updateProfile, updating, error };
}

export default useProfileUpdate;