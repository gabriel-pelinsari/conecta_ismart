import axios from 'axios';

// Configurar base URL da API
const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Faz upload de um arquivo CSV com emails
 * @param {File} file - Arquivo CSV
 * @returns {Promise} Resposta da API
 */
export const uploadEmailsCsv = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/emails/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

/**
 * Obtém a lista de emails pendentes
 * @returns {Promise} Lista de emails
 */
export const getPendingEmails = async () => {
  try {
    const response = await api.get('/emails/pending');
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export default api;