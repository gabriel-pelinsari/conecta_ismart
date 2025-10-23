import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import NavBar from "./components/NavBar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Admin from "./pages/Admin";
import Profile from "./pages/Profile";
import ProfileEdit from "./pages/ProfileEdit";

/* === Protected Routes === */
function ProtectedRoute({ token, children }) {
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function AdminRoute({ token, role, children }) {
  if (!token) return <Navigate to="/login" replace />;
  if (role !== "admin") return <Navigate to="/home" replace />;
  return children;
}

/* === App === */
export default function App() {
  const [token, setToken] = useState(null);
  const [role, setRole] = useState(null);

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedRole = localStorage.getItem("role");
    if (savedToken) setToken(savedToken);
    if (savedRole) setRole(savedRole);
  }, []);

  function setAuth(t, r) {
    setToken(t);
    setRole(r);
    localStorage.setItem("token", t);
    localStorage.setItem("role", r);
  }

  function logout() {
    setToken(null);
    setRole(null);
    localStorage.removeItem("token");
    localStorage.removeItem("role");
  }

  return (
    <BrowserRouter>
      {token && <NavBar role={role} logout={logout} />}
      <Routes>
        <Route path="/" element={<Navigate to={token ? "/home" : "/login"} />} />

        <Route path="/login" element={<Login setAuth={setAuth} />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/home"
          element={
            <ProtectedRoute token={token}>
              <Home />
            </ProtectedRoute>
          }
        />

        {/* ADICIONAR ESTAS ROTAS */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute token={token}>
              <Profile />
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile/:userId"
          element={
            <ProtectedRoute token={token}>
              <Profile />
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile/edit"
          element={
            <ProtectedRoute token={token}>
              <ProfileEdit />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <AdminRoute token={token} role={role}>
              <Admin token={token} />
            </AdminRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}