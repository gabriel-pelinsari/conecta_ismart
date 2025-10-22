import React, { useState } from 'react';
import { uploadEmailsCsv } from '../services/emailService';
import './UploadEmailsModal.css';

export default function UploadEmailsModal() {
  // Estados do modal
  const [isOpen, setIsOpen] = useState(false);

  // Estados do upload
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  /**
   * Abre/fecha o modal
   */
  const openModal = () => {
    setIsOpen(true);
  };

  const closeModal = () => {
    setIsOpen(false);
    resetForm();
  };

  /**
   * Reseta o formulário
   */
  const resetForm = () => {
    setFile(null);
    setResponse(null);
    setError(null);
  };

  /**
   * Manipula a seleção de arquivo
   */
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    // Validação: apenas CSV
    if (selectedFile && !selectedFile.name.endsWith('.csv')) {
      setError('Por favor, selecione um arquivo CSV');
      setFile(null);
      return;
    }

    // Validação: tamanho máximo 5MB
    if (selectedFile && selectedFile.size > 5 * 1024 * 1024) {
      setError('Arquivo muito grande. Máximo 5MB');
      setFile(null);
      return;
    }

    setError(null);
    setFile(selectedFile);
  };

  /**
   * Manipula o envio do arquivo
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Selecione um arquivo CSV');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await uploadEmailsCsv(file);
      setResponse(result);
      setFile(null);
    } catch (err) {
      setError(err.detail || 'Erro ao fazer upload');
      console.error('Erro:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Botão Minimalista */}
      <button onClick={openModal} className="upload-trigger-btn">
        📤 Upload de Emails
      </button>

      {/* Modal */}
      {isOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="modal-header">
              <h2>📤 Upload de Emails</h2>
              <button
                className="modal-close-btn"
                onClick={closeModal}
                aria-label="Fechar modal"
              >
                ✕
              </button>
            </div>

            {/* Body */}
            <div className="modal-body">
              {!response ? (
                <form onSubmit={handleSubmit} className="upload-form">
                  <p className="subtitle">Faça upload de um arquivo CSV com os emails dos alunos</p>

                  {/* Input de arquivo */}
                  <div className="file-input-wrapper">
                    <input
                      type="file"
                      accept=".csv"
                      onChange={handleFileChange}
                      id="csvFile"
                      className="file-input"
                      disabled={loading}
                    />
                    <label htmlFor="csvFile" className="file-label">
                      {file ? `✓ ${file.name}` : '📁 Clique para selecionar arquivo CSV'}
                    </label>
                  </div>

                  {/* Exemplo de formato */}
                  <div className="format-example">
                    <p className="example-title">Formato esperado:</p>
                    <pre>email
usuario1@example.com
usuario2@example.com</pre>
                  </div>

                  {/* Erro */}
                  {error && (
                    <div className="alert alert-error">
                      ❌ {error}
                    </div>
                  )}

                  {/* Botão de envio */}
                  <button
                    type="submit"
                    disabled={!file || loading}
                    className="submit-button"
                  >
                    {loading ? '⏳ Enviando...' : '🚀 Enviar CSV'}
                  </button>
                </form>
              ) : (
                response && (
                  <div className="response-container">
                    <div className="alert alert-success">
                      ✅ {response.message}
                    </div>

                    <div className="email-sent-notice">
                      📧 Todos os emails foram enviados com o código de verificação!
                    </div>

                    <div className="stats">
                      <div className="stat-item success">
                        <span className="stat-label">Enviados</span>
                        <span className="stat-value">{response.success_count}</span>
                      </div>
                      <div className="stat-item error">
                        <span className="stat-label">Erros</span>
                        <span className="stat-value">{response.error_count}</span>
                      </div>
                    </div>

                    {/* Lista de erros */}
                    {response.errors && response.errors.length > 0 && (
                      <div className="errors-list">
                        <h4>Detalhes dos erros:</h4>
                        <ul>
                          {response.errors.map((err, index) => (
                            <li key={index}>
                              <strong>{err.email}</strong>: {err.reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Botões de ação */}
                    <div className="response-actions">
                      <button
                        className="btn-primary"
                        onClick={() => {
                          resetForm();
                          closeModal();
                        }}
                      >
                        Fechar
                      </button>
                      <button
                        className="btn-secondary"
                        onClick={() => resetForm()}
                      >
                        Fazer outro upload
                      </button>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}