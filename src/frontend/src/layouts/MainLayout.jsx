import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import '../styles/layouts/MainLayout.css';

export default function MainLayout() {
  const navigate = useNavigate();

  return (
    <div className="main-layout">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-container">
          <div 
            className="navbar-brand"
            onClick={() => navigate('/')}
            style={{ cursor: 'pointer' }}
          >
            🚀 ISMART Conecta
          </div>

          <ul className="navbar-links">
            <li>
              <button 
                className="nav-link"
                onClick={() => navigate('/')}
              >
                Home
              </button>
            </li>
            <li>
              <button 
                className="nav-link"
                onClick={() => navigate('/dashboard')}
              >
                Dashboard
              </button>
            </li>
            <li>
              <button 
                className="nav-link"
                onClick={() => navigate('/admin')}
              >
                Admin
              </button>
            </li>
          </ul>

          <div className="navbar-actions">
            <button 
              className="btn btn-small"
              onClick={() => navigate('/login')}
            >
              Login
            </button>
          </div>
        </div>
      </nav>

      {/* Outlet para páginas */}
      <main className="main-content">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <p>&copy; 2025 ISMART Conecta. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
}