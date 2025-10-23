import styled from "styled-components";
import { Field, Label, Input } from "../ui/TextField";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const CheckboxField = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const CheckboxInput = styled.input`
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: ${({ theme }) => theme.colors.primary};
`;

const CheckboxLabel = styled.label`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text};
  cursor: pointer;
`;

const FieldsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
`;

export default function SocialLinksEditor({
  values,
  onChange,
  editable = false,
}) {
  if (!editable) {
    return null;
  }

  function handleChange(field, value) {
    onChange({ ...values, [field]: value });
  }

  function handleCheckboxChange(field, checked) {
    onChange({ ...values, [field]: checked });
  }

  return (
    <Container>
      <FieldsGrid>
        <Field>
          <Label htmlFor="linkedin">LinkedIn URL</Label>
          <Input
            id="linkedin"
            type="url"
            placeholder="https://linkedin.com/in/seu-perfil"
            value={values.linkedin || ""}
            onChange={(e) => handleChange("linkedin", e.target.value)}
          />
        </Field>

        <Field>
          <Label htmlFor="instagram">Instagram</Label>
          <Input
            id="instagram"
            type="text"
            placeholder="@seu_usuario"
            value={values.instagram || ""}
            onChange={(e) => handleChange("instagram", e.target.value)}
          />
        </Field>

        <Field>
          <Label htmlFor="whatsapp">WhatsApp</Label>
          <Input
            id="whatsapp"
            type="tel"
            placeholder="(11) 9XXXX-XXXX"
            value={values.whatsapp || ""}
            onChange={(e) => handleChange("whatsapp", e.target.value)}
          />
        </Field>
      </FieldsGrid>

      <CheckboxField>
        <CheckboxInput
          id="show-whatsapp"
          type="checkbox"
          checked={values.show_whatsapp || false}
          onChange={(e) => handleCheckboxChange("show_whatsapp", e.target.checked)}
        />
        <CheckboxLabel htmlFor="show-whatsapp">
          Permitir que amigos vejam meu WhatsApp
        </CheckboxLabel>
      </CheckboxField>
    </Container>
  );
}