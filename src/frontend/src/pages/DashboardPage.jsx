import React from 'react';
import '../styles/pages/DashboardPage.css';

export default function DashboardPage() {
  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="dashboard-container">
          <h1>Dashboard</h1>
          <p>Bem-vindo ao ISMART Conecta</p>
        </div>
      </header>

      <div className="dashboard-container">
        <div className="dashboard-content">
          <div className="welcome-card">
            <h2>👋 Bem-vindo!</h2>
            <p>Esta é a página do dashboard. Aqui você terá acesso a:</p>
            <ul>
              <li>Seu perfil pessoal</li>
              <li>Seus amigos e conexões</li>
              <li>Threads e discussões</li>
              <li>Eventos disponíveis</li>
              <li>Seu histórico de pontos e badges</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}