## LISTA DE REQUISITOS

### REQUISITOS FUNCIONAIS (RF)

#### MÓDULO 1: AUTENTICAÇÃO E CADASTRO

* RF001 - Upload de CSV com emails dos alunos pelo administrador
* RF002 - Envio automático de email com código único de cadastro
* RF003 - Tela de registro com validação de código de cadastro
* RF004 - Sistema de login com email e senha
* RF005 - Recuperação de senha via email
* RF006 - Validação de dados obrigatórios no cadastro
* RF007 - Prevenção de cadastros duplicados
* RF008 - Criptografia de senha no banco de dados
* RF009 - Logout de usuário

#### MÓDULO 2: PERFIL DE USUÁRIO

* RF010 - Visualização de perfil próprio
* RF011 - Visualização de perfil de outros usuários
* RF012 - Edição de informações básicas (nome, foto, universidade, curso, semestre)
* RF013 - Edição de bio/sobre mim (texto livre)
* RF014 - Adição e remoção de tags de hobbies/interesses
* RF015 - Visualização de badges conquistadas no perfil
* RF016 - Visualização de estatísticas públicas (threads, comentários, eventos)
* RF017 - Adição de redes sociais (WhatsApp, Instagram, LinkedIn)
* RF018 - Ocultação de redes sociais para não-amigos
* RF019 - Liberação automática de redes sociais após aceite de amizade
* RF020 - Upload de foto de perfil
* RF021 - Validação de tamanho máximo de foto

#### MÓDULO 3: THREADS E FÓRUM

* RF022 - Criar nova thread (título, descrição, categoria, tags)
* RF023 - Editar thread própria
* RF024 - Deletar thread própria
* RF025 - Visualizar lista de threads
* RF026 - Visualizar detalhes de uma thread
* RF027 - Comentar em threads
* RF028 - Editar comentário próprio
* RF029 - Deletar comentário próprio
* RF030 - Sistema de upvote em threads
* RF031 - Sistema de downvote em threads
* RF032 - Sistema de upvote em comentários
* RF033 - Sistema de downvote em comentários
* RF034 - Limitar 1 voto por usuário por thread/comentário
* RF035 - Marcar thread como "Resolvida/Útil"
* RF036 - Busca de threads por palavra-chave
* RF037 - Filtro de threads por universidade
* RF038 - Filtro de threads por categoria
* RF039 - Filtro de threads por tags
* RF040 - Filtro de threads por popularidade (upvotes)
* RF041 - Ordenação por mais recentes
* RF042 - Ordenação por mais populares
* RF043 - Ordenação por mais comentadas
* RF044 - Notificação de novos comentários em threads que participou
* RF045 - Paginação de threads
* RF046 - Paginação de comentários

#### MÓDULO 4: DESCOBERTA E AGRUPAMENTO

* RF047 - Página "Explorar" com lista de alunos
* RF048 - Filtro de alunos por universidade
* RF049 - Filtro de alunos por curso
* RF050 - Filtro de alunos por interesses comuns
* RF051 - Sugestões de conexão baseadas em vetorização de interesses
* RF052 - Grupos automáticos por universidade
* RF053 - Página dedicada por universidade listando todos os alunos
* RF054 - Busca de alunos por nome
* RF055 - Filtros combinados (múltiplos critérios simultâneos)

#### MÓDULO 5: SISTEMA DE AMIZADES

* RF056 - Botão "Adicionar amigo" em perfis
* RF057 - Envio de solicitação de amizade
* RF058 - Notificação de solicitação de amizade recebida
* RF059 - Aceitar solicitação de amizade
* RF060 - Recusar solicitação de amizade
* RF061 - Visualizar lista de amigos
* RF062 - Visualizar solicitações pendentes (enviadas)
* RF063 - Visualizar solicitações pendentes (recebidas)
* RF064 - Remover amizade
* RF065 - Busca na lista de amigos
* RF066 - Prevenir envio de múltiplas solicitações para mesma pessoa
* RF067 - Liberação automática de contatos após aceite mútuo

#### MÓDULO 6: SISTEMA DE MENTORIA

* RF068 - Identificação automática de mentores elegíveis (4º semestre ou mais)
* RF069 - Matching automático de mentor-mentorado por vetorização de interesses
* RF070 - Limite de 3 mentorados por mentor
* RF071 - Liberação automática de WhatsApp do mentorado para mentor
* RF072 - Envio de mensagem automática de apresentação mentor-mentorado
* RF073 - Página "Minha Mentoria" para visualizar mentor
* RF074 - Página "Minha Mentoria" para visualizar mentorados (mentores)
* RF075 - Fila de espera para mentorados sem match
* RF076 - Notificação ao mentor quando recebe novo mentorado
* RF077 - Badge especial para mentores ativos
* RF078 - Histórico de mentorias



#### MÓDULO 7: SISTEMA DE EVENTOS

* RF079 - Criar novo evento (título, descrição, data/hora, local, categoria, limite de vagas)
* RF080 - Editar evento próprio
* RF081 - Cancelar evento próprio
* RF082 - Visualizar lista de eventos
* RF083 - Visualizar detalhes de evento
* RF084 - Confirmar presença em evento (RSVP)
* RF085 - Cancelar confirmação de presença
* RF086 - Visualizar lista de confirmados
* RF087 - Contador de vagas restantes
* RF088 - Impedir confirmações acima do limite de vagas
* RF089 - Filtro de eventos por data
* RF090 - Filtro de eventos por categoria
* RF091 - Filtro de eventos por universidade
* RF092 - Filtro de eventos por tipo (presencial/online)
* RF093 - Notificação de eventos próximos
* RF094 - Notificação de cancelamento de evento (para confirmados)
* RF095 - Arquivamento automático de eventos passados
* RF096 - Calendário visual de eventos



#### MÓDULO 8: GAMIFICAÇÃO

##### 8.1 Sistema de Pontos

* RF097 - Atribuir +10 pontos ao criar thread
* RF098 - Atribuir +5 pontos ao comentar
* RF099 - Atribuir +2 pontos ao receber upvote
* RF100 - Atribuir +15 pontos ao ter thread marcada como útil
* RF101 - Atribuir +20 pontos ao participar de evento
* RF102 - Atribuir +50 pontos ao completar perfil 100%
* RF103 - Dashboard pessoal de pontos acumulados
* RF104 - Histórico de pontuação

##### 8.2 Sistema de Badges

* RF105 - Criação de badges personalizadas pelo admin (nome, descrição, ícone, critério)
* RF106 - Badge automática: Primeira Conexão
* RF107 - Badge automática: Solucionador (5 threads úteis)
* RF108 - Badge automática: Mentor Ativo
* RF109 - Badge automática: Embaixador (3+ universidades)
* RF110 - Badge automática: Networker (20+ amigos)
* RF111 - Visualização de badges no perfil
* RF112 - Notificação ao conquistar badge
* RF113 - Atribuição automática de badges quando critérios são atingidos
* RF114 - Atribuição manual de badge pelo admin

##### 8.3 Níveis de Engajamento

* RF115 - Nível Novato (0-100 pontos)
* RF116 - Nível Colaborador (101-500 pontos)
* RF117 - Nível Conector (501-1000 pontos)
* RF118 - Nível Embaixador (1000+ pontos)
* RF119 - Visualização de nível atual no perfil
* RF120 - Barra de progresso para próximo nível

#### MÓDULO 9: PAINEL ADMINISTRATIVO

##### 9.1 Gestão de Usuários

* RF121 - Upload de CSV com emails dos alunos
* RF122 - Envio em massa de códigos de cadastro
* RF123 - Visualizar lista de todos os usuários
* RF124 - Buscar usuário específico
* RF125 - Visualizar detalhes de usuário
* RF126 - Desativar conta de usuário
* RF127 - Reativar conta de usuário
* RF128 - Exportar lista de usuários (CSV)

##### 9.2 Gestão de Denúncias

* RF129 - Fila de denúncias pendentes
* RF130 - Visualizar detalhes da denúncia (reportado por, motivo, data, conteúdo)
* RF131 - Aprovar denúncia
* RF132 - Rejeitar denúncia
* RF133 - Remover conteúdo denunciado (thread/comentário)
* RF134 - Advertir usuário
* RF135 - Banir usuário temporariamente
* RF136 - Banir usuário permanentemente
* RF137 - Histórico de moderações por usuário
* RF138 - Histórico completo de todas as moderações

##### 9.3 Dashboard Analítico

* RF139 - Métrica: Total de usuários cadastrados
* RF140 - Métrica: Total de usuários ativos (últimos 30 dias)
* RF141 - Métrica: Threads criadas por período
* RF142 - Métrica: Comentários por período
* RF143 - Gráfico: Engajamento por universidade
* RF144 - Top 10 usuários mais engajados
* RF145 - Métrica: Eventos criados
* RF146 - Métrica: Eventos realizados
* RF147 - Taxa de adoção da plataforma (% dos 1000 alunos)
* RF148 - Métrica: Mentorias ativas
* RF149 - Filtro de métricas por período (semanal, mensal, anual)
* RF150 - Exportação de dashboard (PDF/CSV)

##### 9.4 Gestão de Badges

* RF151 - Criar nova badge personalizada
* RF152 - Editar badge existente
* RF153 - Deletar badge
* RF154 - Definir critérios de conquista automática
* RF155 - Upload de ícone da badge
* RF156 - Atribuir badge manualmente a usuário específico
* RF157 - Visualizar badges distribuídas (estatísticas)
* RF158 - Histórico de conquistas de badges por usuário

##### 9.5 Gestão de Eventos

* RF159 - Visualizar todos os eventos (passados e futuros)
* RF160 - Destacar/fixar eventos importantes
* RF161 - Cancelar eventos inadequados
* RF162 - Editar eventos de qualquer usuário
* RF163 - Visualizar lista de confirmados por evento

##### 9.6 Gestão de Conteúdo

* RF164 - Visualizar todas as threads
* RF165 - Deletar threads inadequadas
* RF166 - Editar threads (moderação)
* RF167 - Fixar threads importantes
* RF168 - Arquivar threads antigas



#### MÓDULO 10: NOTIFICAÇÕES

* RF169 - Notificação de novo comentário em thread que participou
* RF170 - Notificação de solicitação de amizade recebida
* RF171 - Notificação de amizade aceita
* RF172 - Notificação de novo mentorado (para mentores)
* RF173 - Notificação de mentor atribuído (para mentorados)
* RF174 - Notificação de evento próximo (24h antes)
* RF175 - Notificação de cancelamento de evento
* RF176 - Notificação de conquista de badge
* RF177 - Notificação de upvote em thread/comentário próprio
* RF178 - Notificação de menção em comentário
* RF179 - Central de notificações
* RF180 - Marcar notificação como lida
* RF181 - Marcar todas como lidas
* RF182 - Configurações de notificações (ativar/desativar por tipo)

#### MÓDULO 11: DENÚNCIAS (Usuário)

* RF183 - Denunciar thread inadequada
* RF184 - Denunciar comentário inadequado
* RF185 - Denunciar perfil/usuário
* RF186 - Selecionar motivo da denúncia (lista predefinida)
* RF187 - Adicionar descrição opcional à denúncia
* RF188 - Confirmação de envio de denúncia
* RF189 - Prevenir múltiplas denúncias do mesmo conteúdo pelo mesmo usuário

### REQUISITOS NÃO-FUNCIONAIS (RNF)

#### PERFORMANCE

* RNF001 - Tempo de resposta de APIs ≤2 segundos para 95% das requisições
* RNF002 - Suportar 1000 usuários simultâneos sem degradação
* RNF003 - Paginação obrigatória em listagens com mais de 20 itens
* RNF004 - Lazy loading de imagens
* RNF005 - Cache de queries frequentes (TTL configurável)
* RNF006 - Otimização de consultas ao banco de dados (índices adequados)



#### SEGURANÇA

* RNF007 - Senhas criptografadas com algoritmo bcrypt ou superior
* RNF008 - Autenticação via JWT com expiração de 24h
* RNF009 - Refresh tokens para renovação de sessão
* RNF010 - Validação de entrada em todos os endpoints (prevenção de SQL Injection)
* RNF011 - Sanitização de HTML em campos de texto livre (prevenção de XSS)
* RNF012 - Rate limiting em endpoints sensíveis (login, cadastro, envio de email)
* RNF013 - HTTPS obrigatório em produção
* RNF014 - Logs não devem conter informações sensíveis (senhas, tokens)
* RNF015 - Conformidade com LGPD (dados sensíveis criptografados)
* RNF016 - Validação de tipos de arquivo em uploads (apenas imagens permitidas)
* RNF017 - Tamanho máximo de upload: 5MB por arquivo



#### USABILIDADE

* RNF018 - Interface responsiva (mobile, tablet, desktop)
* RNF019 - Compatibilidade com navegadores modernos (Chrome, Firefox, Safari, Edge)
* RNF020 - Feedback visual em todas as ações do usuário (loading, sucesso, erro)
* RNF021 - Mensagens de erro claras e orientativas
* RNF022 - Formulários com validação em tempo real
* RNF023 - Acessibilidade básica (contraste de cores, navegação por teclado)
* RNF024 - Tempo de carregamento inicial da página ≤3 segundos



#### CONFIABILIDADE

* RNF025 - Sistema de logs estruturados para debugging
* RNF026 - Tratamento de erros em todas as operações críticas
* RNF027 - Rollback automático em transações de banco de dados com falha
* RNF028 - Backup diário do banco de dados (produção)
* RNF029 - Monitoramento de uptime (meta: 99% em produção)



#### MANUTENIBILIDADE

* RNF030 - Código versionado em Git com commits semânticos
* RNF031 - Cobertura de testes ≥60% em funcionalidades críticas
* RNF032 - Documentação técnica completa (README, arquitetura, APIs)
* RNF033 - API documentada com OpenAPI/Swagger
* RNF034 - Código seguindo padrões de estilo (PEP8 para Python, ESLint para JS)
* RNF035 - Migrations versionadas para banco de dados
* RNF036 - Variáveis de ambiente para configurações sensíveis



#### ESCALABILIDADE

* RNF037 - Arquitetura preparada para containerização (Docker)
* RNF038 - Separação clara entre frontend e backend (APIs RESTful)
* RNF039 - Banco de dados preparado para crescimento (índices, normalização)
* RNF040 - Assets estáticos servidos via CDN (futuro)



#### DISPONIBILIDADE

* RNF041 - Ambiente de desenvolvimento local funcionando via Docker Compose
* RNF042 - Configuração de CI/CD básica (GitHub Actions)
* RNF043 - Scripts automatizados para deploy
* RNF044 - Documentação de rollback em caso de falha



### 📊 RESUMO QUANTITATIVO

| Categoria | Quantidade |
|-----------|-----------|
| Requisitos Funcionais (RF) | 189 |
| Requisitos Não-Funcionais (RNF) | 44 |
| TOTAL | 233 |