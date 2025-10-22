import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import '../styles/layouts/AdminLayout.css';

export default function AdminLayout() {
  const navigate = useNavigate();

  return (
    <div className="admin-layout">
      {/* Navbar Admin */}
      <nav className="admin-navbar">
        <div className="admin-navbar-container">
          <div 
            className="admin-navbar-brand"
            onClick={() => navigate('/admin')}
            style={{ cursor: 'pointer' }}
          >
            🔐 Admin
          </div>

          <ul className="admin-navbar-links">
            <li>
              <button 
                className="admin-nav-link"
                onClick={() => navigate('/')}
              >
                Sair do Admin
              </button>
            </li>
          </ul>
        </div>
      </nav>

      {/* Content */}
      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  );
}