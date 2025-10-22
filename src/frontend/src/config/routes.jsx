import React from 'react';
import { Routes, Route } from 'react-router-dom';

// Layouts
import MainLayout from '../layouts/MainLayout';
import AdminLayout from '../layouts/AdminLayout';

// Páginas Principais
import HomePage from '../pages/HomePage';
import DashboardPage from '../pages/DashboardPage';
import AdminPage from '../pages/AdminPage';
import NotFoundPage from '../pages/NotFoundPage';

/**
 * Componente que define todas as rotas da aplicação
 * 
 * Estrutura:
 * /                    - Home
 * /dashboard           - Dashboard do usuário
 * /admin               - Painel de administração
 * /*                   - 404
 */
export default function AppRoutes() {
  return (
    <Routes>
      {/* Rotas com MainLayout */}
      <Route element={<MainLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Route>

      {/* Rotas com AdminLayout */}
      <Route element={<AdminLayout />}>
        <Route path="/admin" element={<AdminPage />} />
      </Route>

      {/* 404 - Deve ser a última rota */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}