import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/pages/NotFoundPage.css';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="not-found-page">
      <div className="not-found-container">
        <h1>404</h1>
        <h2>Página não encontrada</h2>
        <p>A página que você procura não existe.</p>
        
        <button 
          className="btn btn-primary"
          onClick={() => navigate('/')}
        >
          Voltar para Home
        </button>
      </div>
    </div>
  );
}