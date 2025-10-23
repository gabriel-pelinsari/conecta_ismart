import { useState, useEffect } from "react";
import { profileApi } from "../services/profileApi";

export function useInterests() {
  const [allInterests, setAllInterests] = useState([]);
  const [myInterests, setMyInterests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInterests();
  }, []);

  async function loadInterests() {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Token não encontrado");
      }

      const [all, mine] = await Promise.all([
        profileApi.getAllInterests(token),
        profileApi.getMyInterests(token),
      ]);

      setAllInterests(all);
      setMyInterests(mine.interests || []);
    } catch (err) {
      console.error("Erro ao carregar interesses:", err);
      setError(err.message || "Erro ao carregar interesses");
    } finally {
      setLoading(false);
    }
  }

  async function addInterest(interestId) {
    try {
      setError(null);

      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Token não encontrado");
      }

      await profileApi.addInterest(token, interestId);

      // Atualizar lista local
      const interest = allInterests.find((i) => i.id === interestId);
      if (interest && !myInterests.find((i) => i.id === interestId)) {
        setMyInterests([...myInterests, interest]);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message;
      setError(errorMsg);
      throw err;
    }
  }

  async function removeInterest(interestId) {
    try {
      setError(null);

      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Token não encontrado");
      }

      await profileApi.removeInterest(token, interestId);

      // Atualizar lista local
      setMyInterests(myInterests.filter((i) => i.id !== interestId));
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message;
      setError(errorMsg);
      throw err;
    }
  }

  return {
    allInterests,
    myInterests,
    loading,
    error,
    addInterest,
    removeInterest,
    refetch: loadInterests,
  };
}

export default useInterests;