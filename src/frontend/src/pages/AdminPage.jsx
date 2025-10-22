import React, { useState } from 'react';
import UploadEmailsModal from '../components/UploadEmailsModal';
import '../styles/pages/AdminPage.css';

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('emails');

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div className="admin-container">
          <h1>Painel de Administração</h1>
          <p>Gerencie os usuários e configurações da plataforma</p>
        </div>
      </header>

      <div className="admin-container">
        {/* Tabs */}
        <div className="admin-tabs">
          <button 
            className={`tab ${activeTab === 'emails' ? 'active' : ''}`}
            onClick={() => setActiveTab('emails')}
          >
            📧 Emails
          </button>
          <button 
            className={`tab ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            👥 Usuários
          </button>
          <button 
            className={`tab ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            🚨 Denúncias
          </button>
        </div>

        {/* Content */}
        <div className="admin-content">
          {activeTab === 'emails' && (
            <div className="tab-content">
              <h2>Gerenciar Emails</h2>
              <p>Faça upload de novos emails para enviar convites</p>
              <UploadEmailsModal />
            </div>
          )}

          {activeTab === 'users' && (
            <div className="tab-content">
              <h2>Gerenciar Usuários</h2>
              <p>Lista e configurações de usuários (em desenvolvimento)</p>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="tab-content">
              <h2>Denúncias</h2>
              <p>Visualize e modere denúncias de usuários (em desenvolvimento)</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}