import { useState } from "react";
import styled, { keyframes } from "styled-components";
import Button from "../ui/Button";
import { Input, Field, Label } from "../ui/TextField";
import Tag from "../ui/Tag";

const fadeIn = keyframes`
  from { opacity: 0; transform: scale(0.97) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
`;

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
`;

const Modal = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radii.lg};
  width: 100%;
  max-width: 600px;
  padding: 28px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  animation: ${fadeIn} 0.2s ease;
  box-shadow: ${({ theme }) => theme.shadows.soft};
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`;

const Title = styled.h3`
  margin: 0;
  font-size: 18px;
  color: ${({ theme }) => theme.colors.text};
`;

const CloseBtn = styled.button`
  background: transparent;
  border: none;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 22px;
  cursor: pointer;
  &:hover { color: ${({ theme }) => theme.colors.text}; }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.bg};
  color: ${({ theme }) => theme.colors.text};
  font-family: inherit;
  font-size: 14px;
  min-height: 120px;
  resize: vertical;
  outline: none;
  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(0,113,227,0.15);
  }
`;

const TagsRow = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
`;

export default function ThreadModal({ initialDescription = "", onClose, onCreate }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState(initialDescription);
  const [audience, setAudience] = useState("geral");
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState([]);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function addTag() {
    const t = tagInput.trim();
    if (!t || tags.includes(t)) return;
    setTags([...tags, t]);
    setTagInput("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (title.trim().length < 5) return setError("Título muito curto.");
    if (description.trim().length < 10) return setError("Descrição muito curta.");

    setSubmitting(true);
    try {
      await onCreate({ title, description, category: audience, tags });
      onClose();
    } catch {
      setError("Falha ao criar thread.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Overlay onClick={onClose}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <Header>
          <Title>Nova conversa</Title>
          <CloseBtn onClick={onClose}>×</CloseBtn>
        </Header>

        <form onSubmit={handleSubmit}>
          <Field>
            <Label>Título</Label>
            <Input
              placeholder="Resumo da sua dúvida ou ideia..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </Field>

          <Field style={{ marginTop: 10 }}>
            <Label>Descrição</Label>
            <TextArea
              placeholder="Conte mais detalhes sobre sua dúvida ou assunto..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Field>

          <Field style={{ marginTop: 10 }}>
            <Label>Tipo de postagem</Label>
            <select
              value={audience}
              onChange={(e) => setAudience(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: "10px",
                background: "transparent",
                color: "inherit",
                border: `1px solid var(--outline, #2C2C2E)`
              }}
            >
              <option value="geral">Geral</option>
              <option value="faculdade">Faculdade específica</option>
            </select>
          </Field>

          <Field style={{ marginTop: 10 }}>
            <Label>Tags</Label>
            <div style={{ display: "flex", gap: 8 }}>
              <Input
                placeholder="Digite e pressione Enter"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") { e.preventDefault(); addTag(); }
                }}
              />
              <Button type="button" onClick={addTag}>+ Tag</Button>
            </div>
            <TagsRow>
              {tags.map((t) => (
                <Tag key={t} onRemove={() => setTags(tags.filter((x) => x !== t))}>
                  {t}
                </Tag>
              ))}
            </TagsRow>
          </Field>

          {error && (
            <div style={{ color: "#FF3B30", marginTop: 8, fontSize: 13 }}>{error}</div>
          )}

          <Button type="submit" disabled={submitting} style={{ marginTop: 14 }}>
            {submitting ? "Publicando..." : "Publicar thread"}
          </Button>
        </form>
      </Modal>
    </Overlay>
  );
}
