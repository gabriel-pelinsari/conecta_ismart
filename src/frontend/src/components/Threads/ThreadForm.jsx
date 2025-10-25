import { useState } from "react";
import styled from "styled-components";
import Card from "../ui/Card";
import Button from "../ui/Button";
import { Field, Label, Input } from "../ui/TextField";
import Tag from "../ui/Tag";

const Wrap = styled.form`
  width: ${({ theme }) => theme.sizes.containerWidthDesktop};
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  margin: 0 auto;
  padding: 20px 22px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.outline};
`;


const Row = styled.div`
  display: grid;
  grid-template-columns: 1fr 180px;
  gap: 12px;

  @media (max-width: ${({ theme }) => theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
  font-family: inherit;
  font-size: 14px;
  outline: none;
  transition: border-color .15s ease, box-shadow .15s ease;
  min-height: 90px;
  resize: vertical;

  &::placeholder { color: ${({ theme }) => theme.colors.textMuted}; }
  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(0,113,227,0.15);
  }
`;

const TagsRow = styled.div`
  display: flex; flex-wrap: wrap; gap: 8px;
`;

const Small = styled.div`
  font-size: 12px; color: ${({ theme }) => theme.colors.textMuted};
`;

export default function ThreadForm({ onCreate }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("geral"); // geral | faculdade
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function addTagFromInput() {
    const v = tagInput.trim();
    if (!v) return;
    if (tags.includes(v)) return;
    setTags([...tags, v]);
    setTagInput("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (title.trim().length < 5) return setError("Título precisa de ao menos 5 caracteres.");
    if (description.trim().length < 10) return setError("Descrição precisa de ao menos 10 caracteres.");

    setSubmitting(true);
    try {
      await onCreate({ title, description, category, tags });
      setTitle(""); setDescription(""); setTags([]); setCategory("geral");
    } catch (err) {
      console.error(err);
      setError("Falha ao criar thread.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Wrap as="form" onSubmit={handleSubmit} aria-label="Criar nova thread">
      <Row>
        <Field>
          <Label>Título</Label>
          <Input
            placeholder="O que você quer discutir?"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </Field>

        <Field>
          <Label>Categoria</Label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            style={{
              width: "100%",
              padding: "12px 14px",
              borderRadius: "10px",
              border: `1px solid var(--outline, #2C2C2E)`,
              background: "transparent",
              color: "inherit",
            }}
          >
            <option value="geral">Geral</option>
            <option value="faculdade">Faculdade</option>
          </select>
        </Field>
      </Row>

      <Field style={{ marginTop: 12 }}>
        <Label>Descrição</Label>
        <TextArea
          placeholder="Descreva sua dúvida, contexto, links, etc."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </Field>

      <Field style={{ marginTop: 12 }}>
        <Label>Tags</Label>
        <Row style={{ gridTemplateColumns: "1fr 120px" }}>
          <Input
            placeholder="Digite e pressione Enter"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") { e.preventDefault(); addTagFromInput(); }
            }}
          />
          <Button type="button" onClick={addTagFromInput}>+ Adicionar</Button>
        </Row>
        <TagsRow style={{ marginTop: 8 }}>
          {tags.map((t) => (
            <Tag key={t} onRemove={() => setTags(tags.filter((x) => x !== t))}>{t}</Tag>
          ))}
        </TagsRow>
        <Small>Use 2–5 tags curtas. Ex: “intercâmbio”, “estudos”.</Small>
      </Field>

      {error && (
        <div
          style={{
            marginTop: 12, padding: "10px 12px",
            border: "1px solid var(--outline, #2C2C2E)",
            color: "var(--danger, #FF3B30)", background: "rgba(255,59,48,0.08)",
            borderRadius: 10, fontSize: 13,
          }}
          role="alert"
        >
          {error}
        </div>
      )}

      <Button type="submit" disabled={submitting} style={{ marginTop: 14 }}>
        {submitting ? "Publicando..." : "Publicar thread"}
      </Button>
    </Wrap>
  );
}
