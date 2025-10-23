import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styled from "styled-components";
import api from "../api/axios";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import { Field, Label, Input } from "../components/ui/TextField";

/* === Regras de senha (ajuste aqui, se quiser) === */
const MIN_LEN = 8;
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

const SuccessBox = styled.div`
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.sm};
  color: ${({ theme }) => theme.colors.success};
  background: rgba(52, 199, 89, 0.08);
`;

const Checklist = styled.ul`
  list-style: none;
  padding: 0;
  margin: 4px 0 0 0;
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
  li { margin-top: 2px; }
  .ok { color: ${({ theme }) => theme.colors.success}; }
`;

export default function Register() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  const hasUpper = /[A-Z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasLen = password.length >= MIN_LEN;
  const allowedChars = ALLOWED.test(password) || password.length === 0;

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

  function validateBeforeSubmit() {
    if (!email) return "Informe um email válido.";
    if (!verificationCode || verificationCode.trim().length !== 6)
      return "Informe o código de verificação (6 dígitos).";
    if (!hasLen) return `A senha deve ter pelo menos ${MIN_LEN} caracteres.`;
    if (!hasUpper) return "A senha deve conter ao menos 1 letra maiúscula.";
    if (!hasDigit) return "A senha deve conter ao menos 1 número.";
    if (!allowedChars)
      return "A senha contém caracteres não permitidos.";
    return "";
  }

  async function handleRegister(e) {
    e.preventDefault();
    setError("");
    setOk("");

    const errMsg = validateBeforeSubmit();
    if (errMsg) {
      setError(errMsg);
      return;
    }

    setSubmitting(true);
    try {
      await api.post("/auth/register", {
        email,
        password,
        verification_code: verificationCode.trim(),
      });
      setOk("Cadastro concluído! Redirecionando para o login...");
      // Limpa campos rapidamente (opcional)
      setEmail("");
      setVerificationCode("");
      setPassword("");

      // Redireciona após pequeno delay para UX suave
      setTimeout(() => navigate("/login"), 900);
    } catch (err) {
      const apiMsg =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        "Erro ao cadastrar. Verifique os dados e tente novamente.";
      setError(apiMsg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Wrap>
      <Card as="section" aria-label="Criar conta no ISMART Conecta">
        <Header>
          <Title>Criar conta</Title>
          <Subtitle>Use o e-mail pré-cadastrado e o código enviado</Subtitle>
        </Header>

        <Form onSubmit={handleRegister} noValidate>
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
            <Label htmlFor="code">Código de verificação</Label>
            <Input
              id="code"
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              placeholder="000000"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              required
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
              autoComplete="new-password"
              required
            />
            <Checklist aria-live="polite">
              <li className={hasLen ? "ok" : ""}>• Mínimo de {MIN_LEN} caracteres</li>
              <li className={hasUpper ? "ok" : ""}>• Ao menos 1 letra maiúscula</li>
              <li className={hasDigit ? "ok" : ""}>• Ao menos 1 número</li>
              <li className={allowedChars ? "ok" : ""}>• Sem caracteres perigosos (&lt; &gt; {`{ } [ ] ( ) " ' \` / \\`})</li>
            </Checklist>
          </Field>

          <Button type="submit" disabled={submitting}>
            {submitting ? "Criando..." : "Criar conta"}
          </Button>

          <HintRow>
            <Link to="/login">Já tenho conta</Link>
            <span>Sem o código? Fale com o admin.</span>
          </HintRow>

          {error && <ErrorBox role="alert">{error}</ErrorBox>}
          {ok && <SuccessBox role="status">{ok}</SuccessBox>}
        </Form>
      </Card>
    </Wrap>
  );
}
