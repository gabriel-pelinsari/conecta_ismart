import { useState } from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";
import { FiTrash2 } from "react-icons/fi";
import Card from "../ui/Card";
import Tag from "../ui/Tag";
import Button from "../ui/Button";
import CommentSection from "./CommentSection";

const Wrap = styled(Card)`
  width: 100%;
  max-width: ${({ theme }) => theme.sizes.containerMedium};
  margin: 0 auto 12px auto;
  padding: 18px 22px 20px 22px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.outline};
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
`;

const AvatarButton = styled.button`
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid ${({ theme }) => theme.colors.outline};
  background: ${({ $url, theme }) =>
    $url ? `url(${$url}) center/cover no-repeat` : theme.colors.outline};
  flex-shrink: 0;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
`;

const HeaderInfo = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
`;

const AuthorName = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const Meta = styled.div`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const Title = styled.h3`
  margin: 4px 0 6px 0;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
`;

const Desc = styled.p`
  margin: 0 0 10px 0;
  color: ${({ theme }) => theme.colors.text};
  line-height: 1.6;
`;

const Row = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 6px;
`;

const Actions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;

  button {
    width: auto;
    padding: 8px 10px;
    font-size: 14px;
  }
`;

const DeleteButton = styled(Button)`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-color: ${({ theme }) => theme.colors.danger};
  color: ${({ theme }) => theme.colors.danger};

  &:hover {
    border-color: ${({ theme }) => theme.colors.danger};
    background: ${({ theme }) => theme.colors.danger}11;
  }
`;

export default function ThreadCard({ thread, api, onTagClick }) {
  const [expanded, setExpanded] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  const tags = thread.tags || [];
  const up = thread.upvotes || 0;
  const down = thread.downvotes || 0;

  async function doVote(value) {
    await api.vote(thread.id, value);
  }

  async function doReport() {
    await api.report(thread.id);
  }

  async function handleDelete() {
    if (deleting) return;
    const confirmDelete = window.confirm("Deseja realmente excluir esta thread?");
    if (!confirmDelete) return;
    setDeleting(true);
    try {
      await api.deleteThread(thread.id);
    } catch (e) {
      console.error(e);
      alert("Não foi possível excluir a thread. Tente novamente.");
    } finally {
      setDeleting(false);
    }
  }

  // 🧠 monta URL da foto de perfil do autor
  var photoUrl = thread.author.photo_url?.startsWith("/media")
    ? `http://localhost:8000${thread.author.photo_url}`
    : thread.author.photo_url;

  const currentUserId = api.currentUser?.user_id;
  const canDelete = currentUserId && thread.user_id === currentUserId;


  return (
    <Wrap>
      <Header>
        <AvatarButton
          type="button"
          $url={photoUrl}
          onClick={() => navigate(`/profile/${thread.user_id}`)}
          aria-label="Ver perfil do autor"
        />
        <HeaderInfo>
          <AuthorName>
            {thread.author?.nickname || thread.author?.full_name || "Usuário"}
          </AuthorName>
          <Meta>
            {thread.category === "faculdade" ? "Faculdade" : "Geral"}
          </Meta>
        </HeaderInfo>
      </Header>

      <Title>{thread.title}</Title>
      <Desc>{thread.description}</Desc>

      {!!tags.length && (
        <Row>
          {tags.map((t, i) => (
            <Tag
              key={i}
              style={{ cursor: "pointer" }}
              onClick={() => onTagClick?.(t)}
            >
              #{t}
            </Tag>
          ))}
        </Row>
      )}

      <Actions>
        <Button
          type="button"
          onClick={() => api.vote(thread.id, 1)}
          style={{
            background:
              thread.user_vote === 1
                ? "rgba(0,113,227,0.15)"
                : "transparent",
          }}
        >
          👍 {up}
        </Button>

        <Button
          type="button"
          onClick={() => api.vote(thread.id, -1)}
          style={{
            background:
              thread.user_vote === -1
                ? "rgba(255,59,48,0.15)"
                : "transparent",
          }}
        >
          👎 {down}
        </Button>

        <Button type="button" onClick={() => setExpanded((v) => !v)}>
          {expanded ? "Ocultar comentários" : "Ver comentários"}
        </Button>
        <Button type="button" onClick={doReport} disabled={thread.is_reported}>
          {thread.is_reported ? "Denunciada" : "🚩 Denunciar"}
        </Button>
        {canDelete && (
          <DeleteButton
            type="button"
            onClick={handleDelete}
            disabled={deleting}
            title="Excluir esta thread"
            aria-label="Excluir esta thread"
          >
            <FiTrash2 aria-hidden="true" />
            {deleting ? "Excluindo..." : "Excluir"}
          </DeleteButton>
        )}
      </Actions>

      {expanded && (
        <CommentSection
          threadId={thread.id}
          initialTop={thread.top_comments || []}
          api={api}
        />
      )}
    </Wrap>
  );
}
