# ISMART Conecta — Frontend

Aplicação web desenvolvida em **React + Vite** para o ecossistema ISMART Conecta. Ela oferece o painel completo para alunos, mentores e administradores interagirem com threads, perfis e amizades, consumindo as APIs FastAPI do backend.

## Principais recursos disponíveis

- **Autenticação completa**: registro com código, login via email/senha e persistência do token JWT.
- **Feed de threads**: criação, listagem infinita com busca, votos positivos/negativos, denúncia, comentários em tempo real e destaque para os mais votados.
- **Filtro por categoria**: chips “Geral” e “Minha faculdade” — o segundo filtra automaticamente os posts (de qualquer categoria) feitos por colegas da mesma universidade.
- **Comentários enriquecidos**: avatar clicável leva ao perfil do autor, exibe faculdade/curso quando preenchidos e permite respostas rápidas.
- **Perfis públicos e privados**: visualização de informações acadêmicas, bio, interesses, conquistas e contatos; modo edição com upload de avatar e gerenciamento de redes sociais.
- **Interesses e gamificação**: integração com o backend para listar badges e interesses individuais.
- **Sistema de amizades**: convites com dois estágios (enviar, aceitar/recusar). Botões do perfil refletem os estados `pending`, `incoming` e `friends`.
- **Importação administrativa**: página `/admin` para upload de CSVs com e-mails que pré-cadastram usuários no backend.

## Tecnologias e arquitetura

- **React 18** + **Vite** (HMR) — ES modules modernos.
- **styled-components** para estilização e temas responsivos.
- **Axios** centralizado (`src/api/axios.js`) apontando para `http://localhost:8000` (backend FastAPI).
- **Hooks personalizados** (`src/hooks/`) para threads, perfis, interesses e upload de fotos.
- **Componentização**: pastas por domínio (`components/Threads`, `components/Profile`, `components/ui`) facilitando reuso.

## Pré-requisitos

- Node.js **18+** (recomendado) e npm.
- Backend FastAPI rodando em `http://localhost:8000` (ajuste `src/api/axios.js` se necessário).
- Tokens JWT persistidos em `localStorage` (`token` e `role`) após login.

## Como executar

```bash
cd src/frontend
npm install          # instala dependências
npm run dev          # inicia em http://localhost:5173
```

Scripts adicionais:

- `npm run build` — gera a build de produção.
- `npm run preview` — testa a build localmente.
- `npm run lint` — roda a verificação do ESLint (quando configurado).

## Fluxos principais

| Área | Descrição |
|------|-----------|
| **Autenticação** | `Login.jsx` e `Register.jsx` chamam `/auth/token` e `/auth/register`, salvando token/role no `localStorage`. |
| **Feed** | `Home.jsx` consome `useThreads`, suporta busca debounced, rolagem infinita e filtro por faculdade. |
| **Threads** | `ThreadCard` + `CommentSection` exibem autor, tags, votos, comentários e denúncia. |
| **Perfis** | `Profile.jsx` reutiliza `useProfile` para buscar dados próprios (`/profiles/me`) ou de terceiros (`/profiles/{id}`); suporta convites de amizade. |
| **Amizades** | Estados `none`, `pending`, `incoming` e `friends` determinam os botões exibidos. A API usa `POST /profiles/{id}/friendship` (convidar/cancelar) e `POST /profiles/{id}/friendship/respond?accept=` (aceitar/recusar/remover). |
| **Admin** | `Admin.jsx` realiza upload de CSV assincronamente para `/auth/upload-csv` e apresenta o retorno no painel. |

## Estrutura de pastas (resumo)

```
src/frontend/
├── src/
│   ├── api/axios.js
│   ├── components/
│   │   ├── Threads/…
│   │   ├── Profile/…
│   │   └── ui/…
│   ├── hooks/
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Profile.jsx
│   │   ├── Admin.jsx
│   │   └── …
│   ├── services/ (profileApi, threadApi)
│   ├── styles/ (tema global)
│   └── main.jsx / App.jsx
├── package.json
└── vite.config.js
```

## Próximos passos sugeridos

- Integrar notificações para convites de amizade pendentes.
- Exibir contadores de amizades e interesses em `ProfileStats`.
- Tornar `baseURL` do Axios configurável via variáveis de ambiente `.env` do Vite.
- Adicionar testes de componentes (React Testing Library) para fluxos críticos como amizade e criação de threads.

---

Para dúvidas ou melhorias, abra uma issue ou ajuste diretamente os componentes correspondentes. Boas contribuições! 🎓🤝
