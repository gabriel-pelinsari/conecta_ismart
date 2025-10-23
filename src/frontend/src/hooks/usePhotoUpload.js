import { useState } from "react";
import { profileApi } from "../services/profileApi";

const ALLOWED_MIMES = ["image/jpeg", "image/png"];
const MAX_BYTES = 2 * 1024 * 1024; // 2MB

export function usePhotoUpload() {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);

  function validateFile(file) {
    if (!file) return "Selecione um arquivo";

    if (!ALLOWED_MIMES.includes(file.type)) {
      return "Apenas JPG e PNG são permitidos";
    }

    if (file.size > MAX_BYTES) {
      return "Arquivo muito grande (máximo 2MB)";
    }

    return null;
  }

  function generatePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
    };
    reader.readAsDataURL(file);
  }

  async function uploadPhoto(file) {
    try {
      setError(null);
      
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        throw new Error(validationError);
      }

      generatePreview(file);
      setUploading(true);

      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Token não encontrado");
      }

      const result = await profileApi.uploadPhoto(token, file);
      return result;
    } catch (err) {
      const errorMsg = err.message || "Erro ao fazer upload de foto";
      setError(errorMsg);
      throw err;
    } finally {
      setUploading(false);
    }
  }

  return { uploadPhoto, uploading, error, preview, setPreview };
}