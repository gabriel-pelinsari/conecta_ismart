const now = new Date();

const mockNotifications = [
  {
    id: 1,
    type: "thread_reply",
    title: "Nova resposta na sua thread",
    description: "Marina comentou na thread \"Processo seletivo internacional\".",
    created_at: new Date(now.getTime() - 1000 * 60 * 15).toISOString(),
    is_read: false,
    related_id: 2,
  },
  {
    id: 2,
    type: "event_invite",
    title: "Convite para evento",
    description: "Você foi convidado para \"Encontro de mentores e mentorados\".",
    created_at: new Date(now.getTime() - 1000 * 60 * 60 * 2).toISOString(),
    is_read: false,
    related_id: 101,
  },
  {
    id: 3,
    type: "poll_result",
    title: "Nova enquete criada",
    description: "Lucas abriu a enquete \"Workshops do próximo ciclo\".",
    created_at: new Date(now.getTime() - 1000 * 60 * 60 * 5).toISOString(),
    is_read: true,
    related_id: 301,
  },
  {
    id: 4,
    type: "friend_request",
    title: "Novo pedido de amizade",
    description: "João Victor quer conectar com você.",
    created_at: new Date(now.getTime() - 1000 * 60 * 60 * 24).toISOString(),
    is_read: false,
    related_id: 78,
  },
];

export default mockNotifications;
