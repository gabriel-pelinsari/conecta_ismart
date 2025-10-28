import { useEffect, useState } from "react";
import styled from "styled-components";
import Button from "../ui/Button";
import { Input } from "../ui/TextField";

const CommentsWrap = styled.div`
  margin-top: 8px;
  padding-left: 18px;
  border-left: 2px solid ${({ theme }) => theme.colors.outline};
`;

const CommentItem = styled.div`
  padding: 10px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  &:not(:last-child) {
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
`;

const HeaderRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Avatar = styled.img`
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  background: ${({ theme }) => theme.colors.outline};
`;

const Name = styled.span`
  font-size: 13px;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.text};
`;

const Meta = styled.div`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const Content = styled.div`
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text};
  line-height: 1.5;
  white-space: pre-line;
`;

const NewComment = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
  align-items: center;
`;

export default function CommentSection({ threadId, initialTop = [], api }) {
  const [comments, setComments] = useState(initialTop || []);
  const [loading, setLoading] = useState(false);
  const [newContent, setNewContent] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const full = await api.fetchComments(threadId);
        setComments(full);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, [threadId]);

  async function submit() {
    if (newContent.trim().length < 3) return setError("Comentário muito curto.");
    try {
      const created = await api.addComment(threadId, newContent.trim());
      setComments((prev) => [created, ...prev]);
      setNewContent("");
      setError("");
    } catch (e) {
      setError("Falha ao comentar.");
    }
  }

  return (
    <CommentsWrap>
      {loading ? (
        <Meta>Carregando comentários…</Meta>
      ) : comments.length === 0 ? (
        <Meta>Seja o primeiro a comentar!</Meta>
      ) : (
        comments.map((c) => {
          const author = c.author || {};
          const displayName =
            author.nickname || author.full_name || "Usuário";
          const photoUrl = author.photo_url
            ? author.photo_url.startsWith("/media")
              ? `http://localhost:8000${author.photo_url}`
              : author.photo_url
            : "https://ui-avatars.com/api/?name=" +
              encodeURIComponent(displayName);

          return (
            <CommentItem key={c.id}>
              <HeaderRow>
                <Avatar src={photoUrl} alt={displayName} />
                <div>
                  <Name>{displayName}</Name>
                  <Meta>{author.email || `usuário #${c.user_id}`}</Meta>
                </div>
              </HeaderRow>
              <Content>{c.content}</Content>
            </CommentItem>
          );
        })
      )}

      <NewComment>
        <Input
          placeholder="Escreva um comentário..."
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
        />
        <Button type="button" onClick={submit}>Responder</Button>
      </NewComment>

      {error && <Meta style={{ color: "#FF3B30" }}>{error}</Meta>}
    </CommentsWrap>
  );
}
