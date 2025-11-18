const now = new Date();
const oneDay = 24 * 60 * 60 * 1000;

const mockFeed = [
  {
    type: "thread",
    id: 1,
    user_id: 11,
    title: "Dúvida sobre bolsas em universidades particulares",
    description:
      "Alguém já conseguiu conciliar bolsa parcial com estágio? Queria entender melhor como fica a carga horária.",
    category: "geral",
    tags: ["bolsas", "estágio"],
    upvotes: 14,
    downvotes: 1,
    user_vote: 0,
    is_reported: false,
    author: {
      nickname: "mentee_julia",
      full_name: "Júlia Souza",
      photo_url: "",
    },
    top_comments: [],
  },
  {
    type: "event",
    id: 101,
    title: "Encontro de mentores e mentorados",
    description:
      "Vamos compartilhar experiências e montar grupos de estudo para o próximo semestre.",
    location: "Auditório do Campus Central",
    scheduled_at: new Date(now.getTime() + oneDay * 3).toISOString(),
    audience: "geral",
    creator: {
      nickname: "mentor_rafa",
      full_name: "Rafael Lima",
    },
    confirmed_count: 32,
    comment: "Tragam suas dúvidas e materiais!",
    photo_url:
      "https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?w=800",
  },
  {
    type: "thread",
    id: 2,
    user_id: 22,
    title: "Processo seletivo internacional",
    description:
      "Quem já participou de intercâmbio pode dizer como funciona a validação de histórico escolar?",
    category: "faculdade",
    tags: ["intercâmbio", "documentação"],
    upvotes: 7,
    downvotes: 0,
    user_vote: 1,
    is_reported: false,
    author: {
      nickname: "ana_global",
      full_name: "Ana Carolina",
      photo_url: "",
    },
    top_comments: [],
  },
  {
    type: "poll",
    id: 301,
    title: "Qual trilha de workshops você prefere para o próximo ciclo?",
    description:
      "Vamos organizar os próximos workshops com base no interesse da comunidade.",
    audience: "geral",
    creator: {
      nickname: "coordenador_lucas",
      full_name: "Lucas Mendes",
    },
    options: [
      { label: "Carreiras em tecnologia", votes_count: 18 },
      { label: "Preparação para entrevistas", votes_count: 11 },
      { label: "Produtividade e organização", votes_count: 7 },
    ],
  },
  {
    type: "event",
    id: 102,
    title: "Visita guiada à faculdade parceira",
    description:
      "Tour completo pelo campus e bate-papo com coordenadores de curso.",
    location: "Pontifícia Universidade Parceira",
    scheduled_at: new Date(now.getTime() + oneDay * 10).toISOString(),
    audience: "faculdade",
    creator: {
      nickname: "mentor_clara",
      full_name: "Clara Nogueira",
    },
    confirmed_count: 18,
    comment: "Vagas limitadas!",
    photo_url:
      "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800",
  },
  {
    type: "thread",
    id: 3,
    user_id: 33,
    title: "Como melhorar meu networking?",
    description:
      "Estou entrando no penúltimo ano e gostaria de ideias práticas para criar conexões com profissionais.",
    category: "geral",
    tags: ["networking"],
    upvotes: 22,
    downvotes: 2,
    user_vote: 0,
    is_reported: false,
    author: {
      nickname: "pedro_dev",
      full_name: "Pedro Henrique",
      photo_url: "",
    },
    top_comments: [],
  },
];

export default mockFeed;
