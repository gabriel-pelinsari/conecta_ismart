import { useState } from "react";
import styled, { keyframes } from "styled-components";
import Button from "../ui/Button";
import { Field, Input, Label } from "../ui/TextField";

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

const Actions = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;

const ErrorText = styled.p`
  color: ${({ theme }) => theme.colors.danger};
  font-size: 13px;
  margin: 8px 0 0 0;
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px solid ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
`;

const FileLabel = styled.label`
  width: 100%;
  padding: 12px 14px;
  border-radius: ${({ theme }) => theme.radii.sm};
  border: 1px dashed ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.textMuted};
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
`;

const HiddenInput = styled.input`
  display: none;
`;

export default function EventModal({ onClose, onCreate }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [audience, setAudience] = useState("geral");
  const [comment, setComment] = useState("");
  const [photo, setPhoto] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function close() {
    onClose?.();
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (file) {
      setPhoto(file);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (title.trim().length < 4) return setError("Informe um título para o evento.");
    if (!scheduledAt) return setError("Informe data e horário.");
    if (!location.trim()) return setError("Informe o local do evento.");

    setSubmitting(true);
    try {
      await onCreate?.({
        title,
        description,
        location,
        scheduled_at: scheduledAt,
        audience,
        comment,
        photo,
      });
      close();
    } catch (err) {
      console.error(err);
      setError("Não foi possível criar o evento.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Overlay onClick={close}>
      <Modal onClick={(e) => e.stopPropagation()}>
        <Header>
          <Title>Novo evento</Title>
          <CloseBtn onClick={close}>×</CloseBtn>
        </Header>

        <form onSubmit={handleSubmit}>
          <Field>
            <Label>Título</Label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Nome do evento"
            />
          </Field>

          <Field style={{ marginTop: 10 }}>
            <Label>Descrição</Label>
            <TextArea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Conte sobre o evento e deixe o convite interessante."
            />
          </Field>

          <Actions style={{ marginTop: 10 }}>
            <Field style={{ flex: 1, minWidth: 220 }}>
              <Label>Data e horário</Label>
              <Input
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
              />
            </Field>
            <Field style={{ flex: 1, minWidth: 220 }}>
              <Label>Local</Label>
              <Input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Auditório... / campus..."
              />
            </Field>
          </Actions>

          <Field style={{ marginTop: 10 }}>
            <Label>Categoria</Label>
            <Select value={audience} onChange={(e) => setAudience(e.target.value)}>
              <option value="geral">Geral</option>
              <option value="faculdade">Faculdade específica</option>
            </Select>
          </Field>

          <Field style={{ marginTop: 10 }}>
            <Label>Comentário / instruções</Label>
            <Input
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Observações para os participantes (opcional)"
            />
          </Field>

          <Field style={{ marginTop: 10 }}>
            <Label>Imagem do evento</Label>
            <FileLabel>
              {photo ? photo.name : "Clique para selecionar a foto (JPEG/PNG)"}
              <HiddenInput type="file" accept="image/*" onChange={handleFileChange} />
            </FileLabel>
          </Field>

          {error && <ErrorText>{error}</ErrorText>}

          <Button type="submit" disabled={submitting} style={{ marginTop: 14 }}>
            {submitting ? "Publicando..." : "Publicar evento"}
          </Button>
        </form>
      </Modal>
    </Overlay>
  );
}
