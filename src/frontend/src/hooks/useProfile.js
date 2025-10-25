import { useState, useEffect } from "react";
import { profileApi } from "../services/profileApi";

export function useProfile(userId = null) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProfile();
  }, [userId]); // ✅ Recarrega quando userId muda

  async function loadProfile() {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Token não encontrado - Por favor, faça login");
      }

      console.log(`📋 Carregando perfil... (userId: ${userId || "meu perfil"})`);

      let data;
      if (userId) {
        // ✅ Busca perfil de outro usuário
        console.log(`🔍 Buscando perfil do usuário ${userId}...`);
        data = await profileApi.getProfile(userId, token);
        console.log(`✅ Perfil de outro usuário carregado:`, data);
      } else {
        // ✅ Busca seu próprio perfil
        console.log(`👤 Buscando meu perfil...`);
        data = await profileApi.getMyProfile(token);
        console.log(`✅ Meu perfil carregado:`, data);
      }

      setProfile(data);
    } catch (err) {
      console.error("❌ Erro ao carregar perfil:", err);
      setError(err.message || "Erro ao carregar perfil");
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }

  return { profile, loading, error, refetch: loadProfile };
}

export default useProfile;