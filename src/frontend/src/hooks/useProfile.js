import { useState, useEffect } from "react";
import { profileApi } from "../services/profileApi";

export function useProfile(userId = null) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProfile();
  }, [userId]);

  async function loadProfile() {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Token não encontrado");
      }

      let data;
      if (userId) {
        data = await profileApi.getProfile(userId, token);
      } else {
        data = await profileApi.getMyProfile(token);
      }

      setProfile(data);
    } catch (err) {
      console.error("Erro ao carregar perfil:", err);
      setError(err.message || "Erro ao carregar perfil");
    } finally {
      setLoading(false);
    }
  }

  return { profile, loading, error, refetch: loadProfile };
}

export default useProfile;