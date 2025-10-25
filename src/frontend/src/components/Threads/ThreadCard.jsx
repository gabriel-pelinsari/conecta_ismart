import { useState } from "react";
import styled from "styled-components";
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

const Avatar = styled.div`
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: ${({ $url, theme }) =>
    $url ? `url(${$url})` : theme.colors.outline};
  background-size: cover;
  background-position: center;
  border: 2px solid ${({ theme }) => theme.colors.outline};
  flex-shrink: 0;
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

export default function ThreadCard({ thread, api }) {
  const [expanded, setExpanded] = useState(false);

  const tags = thread.tags || [];
  const up = thread.upvotes || 0;
  const down = thread.downvotes || 0;

  async function doVote(value) {
    await api.vote(thread.id, value);
  }

  async function doReport() {
    await api.report(thread.id);
  }

  // 🧠 monta URL da foto de perfil do autor
  var photoUrl = thread.author.photo_url?.startsWith("/media")
  ? `http://localhost:8000${thread.author.photo_url}`
  : thread.author.photo_url;


  return (
    <Wrap>
      <Header>
        <Avatar $url={photoUrl} />
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
            <Tag key={i}>{t}</Tag>
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
