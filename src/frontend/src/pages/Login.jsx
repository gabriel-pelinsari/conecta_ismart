import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styled from "styled-components";
import api from "../api/axios";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import { Field, Label, Input } from "../components/ui/TextField";

/* === Regras iguais ao Register === */
const ALLOWED = /^[A-Za-z0-9@#$%^&*_\-+=.!?]+$/; // sem < > { } [ ] ( ) " ' ` / \
const SANITIZE = /[^A-Za-z0-9@#$%^&*_\-+=.!?]/g;

const Wrap = styled.main`
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 18px;
`;

const Title = styled.h1`
  margin: 0 0 6px 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
`;

const Subtitle = styled.p`
  margin: 0;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const Form = styled.form`
  display: grid;
  gap: 14px;
  margin-top: 12px;
`;

const HintRow = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: ${({ theme }) => theme.colors.textMuted};
  a { text-decoration: underline; text-underline-offset: 2px; }
`;

const ErrorBox = styled.div`
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.sm};
  color: ${({ theme }) => theme.colors.danger};
  background: rgba(255, 59, 48, 0.08);
`;

export default function Login({ setAuth }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function handlePasswordChange(e) {
    const raw = e.target.value;
    const sanitized = raw.replace(SANITIZE, "");
    setPassword(sanitized);
    if (raw !== sanitized) {
      setError("Sua senha contém caracteres não permitidos e foram removidos.");
    } else {
      setError("");
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const res = await api.post("/auth/token", null, {
        params: { email, password },
      });
      const token = res.data.access_token;

      // Regra simples para admin padrão (ajuste depois para vir do backend)
      const role =
        email === "admin@ismart.com" && password === "admin"
          ? "admin"
          : "student";

      setAuth(token, role);
      navigate("/"); // redireciona sem recarregar
    } catch (err) {
      const apiMsg =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        "Falha no login. Verifique suas credenciais.";
      setError(apiMsg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Wrap>
      <Card as="section" aria-label="Acesso à plataforma ISMART Conecta">
        <Header>
          <Title>Entrar</Title>
          <Subtitle>Acesse com seu e-mail e senha</Subtitle>
        </Header>

        <Form onSubmit={handleLogin} noValidate>
          <Field>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="seuemail@exemplo.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
              aria-invalid={!!error}
            />
          </Field>

          <Field>
            <Label htmlFor="password">Senha</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={handlePasswordChange}
              autoComplete="current-password"
              required
            />
          </Field>

          <Button type="submit" disabled={submitting || !email || !password}>
            {submitting ? "Entrando..." : "Entrar"}
          </Button>

          <HintRow>
            <Link to="/register">Criar conta</Link>
            <span>Precisa de ajuda?</span>
          </HintRow>

          {error && <ErrorBox role="alert">{error}</ErrorBox>}
        </Form>
      </Card>
    </Wrap>
  );
}
