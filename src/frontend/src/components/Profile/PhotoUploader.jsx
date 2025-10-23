import { useState } from "react";
import styled from "styled-components";
import Button from "../ui/Button";
import { usePhotoUpload } from "../../hooks/usePhotoUpload";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
`;

const AvatarContainer = styled.div`
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 3px solid ${({ theme }) => theme.colors.outline};
  overflow: hidden;
  background: ${({ theme }) => theme.colors.surface};
`;

const Avatar = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const AvatarPlaceholder = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const FileInput = styled.input`
  display: none;
`;

const FileLabel = styled.label`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
`;

const UploadButton = styled.button`
  width: 100%;
  padding: 12px 14px;
  border: 1px dashed ${({ theme }) => theme.colors.outline};
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
  border-radius: ${({ theme }) => theme.radii.sm};
  cursor: pointer;
  transition: all 0.15s ease;
  font-size: 14px;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    color: ${({ theme }) => theme.colors.primary};
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const Helper = styled.div`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
  text-align: center;
`;

const ErrorBox = styled.div`
  padding: 10px 12px;
  border: 1px solid ${({ theme }) => theme.colors.outline};
  border-radius: ${({ theme }) => theme.radii.sm};
  color: ${({ theme }) => theme.colors.danger};
  background: rgba(255, 59, 48, 0.08);
  font-size: 12px;
`;

export default function PhotoUploader({ currentPhoto, onUploadSuccess }) {
  const { uploadPhoto, uploading, error, preview, setPreview } = usePhotoUpload();
  const [selectedFile, setSelectedFile] = useState(null);

  const displayPhoto = preview || currentPhoto;

  async function handleFileSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);

    try {
      const result = await uploadPhoto(file);
      if (onUploadSuccess) {
        onUploadSuccess(result.photo_url);
      }
      setSelectedFile(null);
    } catch (err) {
      console.error("Upload failed:", err);
    }
  }

  return (
    <Container>
      <AvatarContainer>
        {displayPhoto ? (
          <Avatar
            src={
              displayPhoto.startsWith("/media")
                ? `http://localhost:8000${displayPhoto}`
                : displayPhoto
            }
            alt="Avatar"
          />
        ) : (
          <AvatarPlaceholder>👤</AvatarPlaceholder>
        )}
      </AvatarContainer>

      <FileLabel>
        <FileInput
          type="file"
          id="photo-input"
          accept="image/jpeg,image/png"
          onChange={handleFileSelect}
          disabled={uploading}
        />
        <UploadButton as="span" disabled={uploading}>
          {uploading ? "Enviando..." : "📸 Trocar foto"}
        </UploadButton>
      </FileLabel>

      <Helper>JPG ou PNG, máximo 2MB</Helper>

      {error && <ErrorBox>{error}</ErrorBox>}
    </Container>
  );
}