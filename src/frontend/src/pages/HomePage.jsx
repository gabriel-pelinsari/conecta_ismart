import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/pages/HomePage.css';

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <header className="home-header">
        <div className="home-container">
          <h1>ISMART Conecta</h1>
          <p>Plataforma de Conexão entre Alunos Universitários</p>
          
          <div className="home-buttons">
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/login')}
            >
              Login
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => navigate('/register')}
            >
              Registrar
            </button>
          </div>
        </div>
      </header>

      <section className="home-features">
        <div className="home-container">
          <h2>Por que ISMART Conecta?</h2>
          
          <div className="features-grid">
            <div className="feature-card">
              <span className="feature-icon">👥</span>
              <h3>Conecte-se</h3>
              <p>Encontre alunos com interesses similares na sua universidade</p>
            </div>

            <div className="feature-card">
              <span className="feature-icon">💬</span>
              <h3>Compartilhe</h3>
              <p>Crie threads, faça perguntas e ajude outros alunos</p>
            </div>

            <div className="feature-card">
              <span className="feature-icon">🎓</span>
              <h3>Aprenda</h3>
              <p>Receba mentoria de alunos mais experientes</p>
            </div>

            <div className="feature-card">
              <span className="feature-icon">🎉</span>
              <h3>Participe</h3>
              <p>Conheça novos eventos e atividades da comunidade</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}