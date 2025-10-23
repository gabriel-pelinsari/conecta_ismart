import { useState } from "react";
import styled from "styled-components";
import api from "../api/axios";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import { Field, Label, Input } from "../components/ui/TextField";

const Wrap = styled.main`
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
`;

const Header = styled.header`
  text-align: left;
  margin-bottom: 18px;
`;

const Title = styled.h1`
  margin: 0 0 6px 0;
  font-size: 24px;
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
  gap: 16px;
  margin-top: 16px;
`;

const FileRow = styled.div`
  display: grid;
  gap: 10px;
`;

const FilePicker = styled.label`
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.textMuted};
  cursor: pointer;
  transition: border-color .15s ease, color .15s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.text};
    border-color: ${({ theme }) => theme.colors.textMuted};
  }
`;

const HiddenInput = styled.input`
  display: none;
`;

const FileName = styled.div`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text};
`;

const Helper = styled.div`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const ResultBox = styled.pre`
  margin-top: 8px;
  max-height: 300px;
  overflow: auto;
  padding: 12px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
`;

const ErrorBox = styled.div`
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.sm};
  color: ${({ theme }) => theme.colors.danger};
  background: rgba(255, 59, 48, 0.08);
  font-size: 14px;
`;

export default function Admin({ token }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  async function handleUpload(e) {
    e.preventDefault();
    setError("");
    setResult("");

    if (!file) {
      setError("Selecione um arquivo .csv antes de enviar.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const res = await api.post("/auth/upload-csv", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });
      setResult(JSON.stringify(res.data, null, 2));
    } catch (err) {
      setError("Erro ao enviar CSV. Verifique o arquivo e suas permissões.");
    } finally {
      setUploading(false);
    }
  }

  function handleFileChange(e) {
    const f = e.target.files?.[0];
    if (!f) {
      setFile(null);
      return;
    }
    if (!f.name.endsWith(".csv")) {
      setError("O arquivo deve ter extensão .csv");
      setFile(null);
      return;
    }
    setError("");
    setFile(f);
  }

  return (
    <Wrap>
      <Card as="section" aria-label="Administração - Upload de CSV" style={{ maxWidth: 720 }}>
        <Header>
          <Title>Admin — Upload CSV</Title>
          <Subtitle>Envie uma lista com a coluna <code>email</code> para pré-cadastrar alunos.</Subtitle>
        </Header>

        <Form onSubmit={handleUpload} noValidate>
          <FileRow>
            <Label>Arquivo CSV</Label>

            <FilePicker htmlFor="csv">
              <span>{file ? "Trocar arquivo" : "Selecionar arquivo"}</span>
              <FileName>{file ? file.name : "Nenhum arquivo selecionado"}</FileName>
            </FilePicker>

            <HiddenInput
              id="csv"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
            />

            <Helper>Formato esperado: uma coluna chamada <code>email</code>.</Helper>
          </FileRow>

          <Button type="submit" disabled={!file || uploading}>
            {uploading ? "Enviando..." : "Enviar CSV"}
          </Button>

          {error && <ErrorBox role="alert">{error}</ErrorBox>}
          {result && <ResultBox aria-live="polite">{result}</ResultBox>}
        </Form>
      </Card>
    </Wrap>
  );
}
