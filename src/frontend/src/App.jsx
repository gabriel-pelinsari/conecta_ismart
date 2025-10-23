import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import NavBar from "./components/NavBar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Admin from "./pages/Admin";
import Profile from "./pages/Profile";
import ProfileEdit from "./pages/ProfileEdit";

/* === Função auxiliar para decodificar JWT === */
function decodeJWT(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload;
  } catch (e) {
    console.error("❌ Erro ao decodificar JWT:", e);
    return null;
  }
}

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
  const [loading, setLoading] = useState(true); // ✅ Estado de carregamento

  // ✅ useEffect que roda UMA VEZ ao abrir a página
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedRole = localStorage.getItem("role");

    console.log("🔍 App iniciando...");
    console.log(`   Token no localStorage: ${savedToken ? "✅ Sim" : "❌ Não"}`);
    console.log(`   Role no localStorage: ${savedRole || "❌ Não"}`);

    if (savedToken) {
      // ✅ Verifica se o token ainda é válido
      const payload = decodeJWT(savedToken);
      
      if (payload && payload.exp) {
        const expiresAt = payload.exp * 1000; // Converter para milissegundos
        const now = Date.now();

        if (now < expiresAt) {
          // Token ainda é válido
          console.log("✅ Token ainda válido!");
          setToken(savedToken);
          setRole(savedRole || "student");
        } else {
          // Token expirou
          console.log("⏰ Token expirado!");
          localStorage.removeItem("token");
          localStorage.removeItem("role");
        }
      } else {
        // Token inválido
        console.log("❌ Token inválido!");
        localStorage.removeItem("token");
        localStorage.removeItem("role");
      }
    }

    setLoading(false); // Marca como carregado
  }, []); // ✅ Roda apenas 1 vez ao montar

  function setAuth(t, r) {
    console.log(`🔐 Autenticando: email (no token), role=${r}`);
    setToken(t);
    setRole(r);
    localStorage.setItem("token", t);
    localStorage.setItem("role", r);
  }

  function logout() {
    console.log("🚪 Logout...");
    setToken(null);
    setRole(null);
    localStorage.removeItem("token");
    localStorage.removeItem("role");
  }

  // ✅ Enquanto carrega, não renderiza nada (evita piscar)
  if (loading) {
    return <div style={{ display: "none" }} />; // Ou um loading spinner se preferir
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