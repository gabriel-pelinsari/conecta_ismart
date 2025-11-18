import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styled from "styled-components";
import api from "../api/axios";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import { Field, Label, Input } from "../components/ui/TextField";

const SANITIZE = /[^A-Za-z0-9@#$%^&*_\-+=.!?]/g;

const Wrap = styled.main`
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: ${({ theme }) => theme.colors.bg};
`;

const Container = styled.div`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerSmall};
  margin: 0 auto;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 24px;
`;

const Title = styled.h1`
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: ${({ theme }) => theme.colors.text};
`;

const Subtitle = styled.p`
  margin: 0;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const Form = styled.form`
  display: grid;
  gap: 16px;
  margin-top: 24px;
`;

const HintRow = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: ${({ theme }) => theme.colors.textMuted};
  margin-top: 12px;

  a {
    color: ${({ theme }) => theme.colors.primary};
    text-decoration: none;

    &:hover {
      text-decoration: underline;
      text-underline-offset: 2px;
    }
  }
`;

const ErrorBox = styled.div`
  padding: 12px 14px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.sm};
  color: ${({ theme }) => theme.colors.danger};
  background: rgba(255, 59, 48, 0.08);
  font-size: 13px;
  font-weight: 500;
`;

const SubmitButton = styled(Button)`
  padding: 14px 16px;
  background: ${({ theme }) => theme.colors.primary};
  color: white;
  border: none;
  font-weight: 600;
  font-size: 15px;
  margin-top: 8px;

  &:hover:not(:disabled) {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

// ✅ FUNÇÃO PARA DECODIFICAR JWT
function decodeJWT(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload;
  } catch (e) {
    console.error("Erro ao decodificar JWT:", e);
    return null;
  }
}

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

  function extractErrorMessage(err) {
    if (err?.response?.data?.detail) {
      const detail = err.response.data.detail;

      if (Array.isArray(detail)) {
        return detail.map((e) => e.msg).join(". ");
      }

      if (typeof detail === "string") {
        return detail;
      }
    }

    return "Falha no login. Verifique suas credenciais.";
  }

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const formData = new FormData();
      formData.append("email", email);
      formData.append("password", password);

      const res = await api.post("/auth/token", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const token = res.data.access_token;

      // ✅ DECODIFICAR TOKEN PARA PEGAR ROLE
      const payload = decodeJWT(token);
      const isAdmin = payload?.role === "admin" || payload?.is_admin === true;
      const role = isAdmin ? "admin" : "student";

      console.log(`✅ Login bem-sucedido: role=${role}`);

      setAuth(token, role); // ← USA ROLE DO TOKEN
      navigate("/home");
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Wrap>
      <Container>
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

            <SubmitButton
              type="submit"
              disabled={submitting || !email || !password}
            >
              {submitting ? "Entrando..." : "Entrar"}
            </SubmitButton>

            <HintRow>
              <Link to="/register">Criar conta</Link>
              <span>Precisa de ajuda?</span>
            </HintRow>

            {error && <ErrorBox role="alert">{error}</ErrorBox>}
          </Form>
        </Card>
      </Container>
    </Wrap>
  );
}
