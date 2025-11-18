import { useState } from "react";
import styled, { keyframes } from "styled-components";
import Button from "../ui/Button";
import { Field, Input, Label } from "../ui/TextField";
import Tag from "../ui/Tag";

const fadeIn = keyframes`
  from { opacity: 0; transform: scale(0.98) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
`;

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const Modal = styled.div`
  width: 100%;
  max-width: 620px;
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radii.lg};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  box-shadow: ${({ theme }) => theme.shadows.soft};
  padding: 28px;
  animation: ${fadeIn} 0.2s ease;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
`;

const Title = styled.h3`
  margin: 0;
  font-size: 18px;
`;

const CloseBtn = styled.button`
  border: none;
  background: transparent;
  font-size: 22px;
  color: ${({ theme }) => theme.colors.textMuted};
  cursor: pointer;
  &:hover {
    color: ${({ theme }) => theme.colors.text};
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 110px;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
  resize: vertical;
  outline: none;

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
  }
`;

const OptionsRow = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
`;

const ErrorText = styled.p`
  color: ${({ theme }) => theme.colors.danger};
  font-size: 13px;
  margin: 8px 0 0 0;
`;

export default function PollModal({ onClose, onCreate }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [audience, setAudience] = useState("geral");
  const [optionInput, setOptionInput] = useState("");
  const [options, setOptions] = useState([]);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function close() {
    onClose?.();
  }

  function addOption() {
    const value = optionInput.trim();
    if (!value) return;
    if (options.includes(value)) return setError("Opção já adicionada.");
    setOptions([...options, value]);
    setOptionInput("");
    setError("");
  }

  function removeOption(option) {
    setOptions((prev) => prev.filter((item) => item !== option));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!title.trim()) return setError("Informe um título.");
    if (options.length < 2) return setError("Adicione pelo menos duas opções.");

    setSubmitting(true);
    try {
      await onCreate?.({
        title,
        description,
        audience,
        options,
      });
      close();
    } catch (err) {
      console.error(err);
      setError("Não foi possível criar a enquete.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Overlay onClick={close}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <Header>
          <Title>Nova enquete</Title>
          <CloseBtn onClick={close}>×</CloseBtn>
        </Header>

        <form onSubmit={handleSubmit}>
          <Field>
            <Label>Título</Label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Como você chamará essa pergunta?"
            />
          </Field>

          <Field style={{ marginTop: 10 }}>
            <Label>Descrição</Label>
            <TextArea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Contexto para quem vai responder (opcional)"
            />
          </Field>

          <Field style={{ marginTop: 10 }}>
            <Label>Opções</Label>
            <div style={{ display: "flex", gap: 8 }}>
              <Input
                value={optionInput}
                onChange={(e) => setOptionInput(e.target.value)}
                placeholder="Digite a opção e pressione Enter"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addOption();
                  }
                }}
              />
              <Button type="button" onClick={addOption}>
                + Adicionar
              </Button>
            </div>
            <OptionsRow>
              {options.map((option) => (
                <Tag key={option} onRemove={() => removeOption(option)}>
                  {option}
                </Tag>
              ))}
            </OptionsRow>
          </Field>

          <Field style={{ marginTop: 10 }}>
            <Label>Categoria</Label>
            <Select value={audience} onChange={(e) => setAudience(e.target.value)}>
              <option value="geral">Geral</option>
              <option value="faculdade">Faculdade específica</option>
            </Select>
          </Field>

          {error && <ErrorText>{error}</ErrorText>}

          <Button type="submit" disabled={submitting} style={{ marginTop: 14 }}>
            {submitting ? "Publicando..." : "Publicar enquete"}
          </Button>
        </form>
      </Modal>
    </Overlay>
  );
}
