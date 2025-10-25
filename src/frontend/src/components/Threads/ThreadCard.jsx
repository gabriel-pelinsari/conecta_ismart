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
  padding: 22px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.outline};
`;

const Title = styled.h3`
  margin: 0 0 6px 0; font-size: 18px; letter-spacing: -0.01em;
`;

const Meta = styled.div`
  font-size: 12px; color: ${({ theme }) => theme.colors.textMuted};
`;

const Desc = styled.p`
  margin: 10px 0 12px 0; color: ${({ theme }) => theme.colors.text}; line-height: 1.6;
`;

const Row = styled.div`
  display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 8px;
`;

const Actions = styled.div`
  display: flex; gap: 8px; margin-top: 10px;
  button { width: auto; padding: 8px 10px; font-size: 14px; }
`;

const Count = styled.span`
  font-size: 12px; color: ${({ theme }) => theme.colors.textMuted};
`;

export default function ThreadCard({ thread, api }) {
  const [expanded, setExpanded] = useState(false);

  const tags = thread.tags || [];
  const up = thread.upvotes || 0;
  const down = thread.downvotes || 0;

  async function doVote(value) {
    await api.vote(thread.id, value);
    // UI otimista ajustada no hook
  }

  async function doReport() {
    await api.report(thread.id);
    // UI otimista no hook (is_reported: true)
  }

  return (
    <Wrap>
      <Title>{thread.title}</Title>
      <Meta>
        por {thread.author?.email || `usuário #${thread.user_id}`} •{" "}
        {thread.category === "faculdade" ? "🎓 Faculdade" : "🌐 Geral"}
      </Meta>

      <Desc>{thread.description}</Desc>

      {!!tags.length && (
        <Row>
          {tags.map((t, i) => <Tag key={i}>{t}</Tag>)}
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
          👍 {thread.upvotes ?? 0}
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
          👎 {thread.downvotes ?? 0}
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
