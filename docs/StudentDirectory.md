# Diretório de Alunos

## Visão Geral

O **Diretório de Alunos** é uma funcionalidade completa que permite aos usuários visualizar, filtrar e descobrir outros alunos cadastrados na plataforma Conecta ISMART.

## Funcionalidades

### 📋 Listagem de Alunos

- Exibição em grid responsivo com cards de alunos
- Informações exibidas em cada card:
  - Foto de perfil
  - Nome completo
  - Universidade
  - Curso
  - Semestre
- Paginação (12 alunos por página)
- Ordenação inicial: aleatória, priorizando alunos da mesma universidade

### 🔍 Filtros

- **Busca por nome**: Campo de texto para buscar alunos pelo nome (mínimo 2 caracteres)
- **Filtro por Faculdade**: Dropdown com todas as universidades cadastradas
- **Filtro por Curso**: Dropdown com todos os cursos disponíveis
- Filtros podem ser combinados
- Chips visuais mostrando filtros ativos com opção de remoção individual

### 📊 Paginação

- Navegação entre páginas com botões "Anterior" e "Próxima"
- Indicador de página atual e total de páginas
- Informação de total de resultados encontrados
- Botões desabilitados quando não há mais páginas

### 👤 Modal de Detalhes

- Ao clicar em um card de aluno, abre um modal com informações públicas:
  - Foto de perfil ampliada
  - Nome completo e nickname
  - Bio (se disponível)
  - Informações acadêmicas (universidade, curso, semestre)
  - Tags de interesses (se disponível)
  - Botão para visualizar perfil completo

### 🎨 Design

- Interface moderna e responsiva
- Animações suaves em hover
- Estados de loading e empty state
- Compatível com tema dark/light (via styled-components)

## Rotas

### Frontend

- **URL**: `/students`
- **Componente**: `StudentDirectory.jsx`
- **Acesso**: Requer autenticação
- **Navegação**: Ícone de usuários (FiUsers) na navbar

### Backend

#### GET `/api/students/explore`

Lista alunos com filtros e paginação.

**Query Params:**

```
- search_name: string (opcional, mín. 2 caracteres)
- universities: array[string] (opcional)
- courses: array[string] (opcional)
- interests: array[string] (opcional)
- semesters: array[string] (opcional)
- order_by: string (opcional, default: "random")
- offset: int (opcional, default: 0)
- limit: int (opcional, default: 20, max: 100)
```

**Resposta:**

```json
{
  "students": [
    {
      "id": 123,
      "full_name": "João Silva",
      "nickname": "joao",
      "university": "USP",
      "course": "Engenharia",
      "semester": "5º Semestre",
      "photo_url": "/media/avatars/...",
      "interests": ["Python", "IA", "Música"],
      "friendship_status": "not_friends",
      "compatibility_score": null
    }
  ],
  "total": 45,
  "offset": 0,
  "limit": 12,
  "has_more": true
}
```

#### GET `/api/students/explore/facets`

Retorna contadores para filtros disponíveis.

**Resposta:**

```json
{
  "universities": [
    {"value": "USP", "count": 30},
    {"value": "UNICAMP", "count": 25}
  ],
  "courses": [
    {"value": "Engenharia", "count": 20},
    {"value": "Medicina", "count": 15}
  ],
  "interests": [...],
  "semesters": [...]
}
```

#### GET `/profiles/public/{user_id}`

Retorna perfil público de um aluno específico.

**Resposta:**

```json
{
  "user_id": 123,
  "full_name": "João Silva",
  "nickname": "joao",
  "university": "USP",
  "course": "Engenharia",
  "semester": "5º Semestre",
  "bio": "Apaixonado por tecnologia...",
  "photo_url": "/media/avatars/...",
  "interests": [
    {"id": 1, "name": "Python"},
    {"id": 2, "name": "IA"}
  ],
  "stats": {...},
  "badges": [...]
}
```

## Requisitos Funcionais Atendidos

- **RF047**: Página "Explorar" com lista de alunos
- **RF048**: Filtro por universidade (múltipla seleção)
- **RF049**: Filtro por curso (múltipla seleção)
- **RF050**: Filtro por interesses comuns
- **RF054**: Busca por nome (mínimo 2 caracteres)
- **RF055**: Filtros combinados (múltiplos critérios simultâneos)

## Regras de Negócio

1. **RN001**: Apenas alunos com perfil público são exibidos
2. **RN002**: O usuário atual não aparece na listagem
3. **RN003**: Alunos inativos não são exibidos
4. **RN004**: Ordem padrão é aleatória para incentivar descoberta
5. **RN005**: Busca por nome requer mínimo 2 caracteres
6. **RN006**: Filtros podem ser combinados (operação AND)
7. **RN007**: Dentro de cada filtro, valores são combinados com OR
8. **RN008**: Paginação máxima: 100 alunos por página

## Estrutura de Arquivos

```
src/
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── StudentDirectory.jsx  # Página principal
│       ├── components/
│       │   └── NavBar.jsx            # Link adicionado
│       └── App.jsx                   # Rota configurada
│
└── backend/
    └── app/
        ├── api/
        │   ├── student_directory.py  # Endpoints existentes
        │   └── profiles.py           # Endpoint /public/{id} adicionado
        ├── services/
        │   └── student_directory.py  # Lógica de negócio
        └── schemas/
            └── student_directory.py  # Schemas ajustados
```

## Como Usar

### Para Usuários

1. Faça login na plataforma
2. Clique no ícone de usuários (👥) na navbar
3. Você será direcionado para o Diretório de Alunos
4. Use os filtros para refinar sua busca:
   - Digite um nome no campo de busca
   - Selecione uma faculdade no dropdown
   - Selecione um curso no dropdown
5. Navegue pelas páginas usando os botões de paginação
6. Clique em um card para ver mais detalhes do aluno
7. No modal, clique em "Ver Perfil Completo" para acessar o perfil do aluno

### Para Desenvolvedores

#### Executar Frontend

```bash
cd src/frontend
npm install
npm run dev
```

#### Executar Backend

```bash
cd src/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tecnologias Utilizadas

### Frontend

- React 18+
- React Router DOM (navegação)
- Styled Components (estilização)
- React Icons (ícones)
- Axios (requisições HTTP)

### Backend

- FastAPI
- SQLAlchemy (ORM)
- Pydantic (validação)
- PostgreSQL (banco de dados)

## Melhorias Futuras

1. **Infinite Scroll**: Implementar carregamento automático ao rolar
2. **Filtros Avançados**:
   - Filtro por interesses múltiplos
   - Filtro por ano de entrada
   - Filtro por cidade
3. **Ordenação**: Adicionar mais opções de ordenação
   - Por nome (A-Z)
   - Por compatibilidade
   - Por data de cadastro
4. **Cache**: Implementar cache de filtros frequentes
5. **Bookmarks**: Permitir salvar/favoritar alunos
6. **Exportação**: Permitir exportar lista de alunos (CSV)
7. **Estatísticas**: Dashboard com estatísticas do diretório

## Screenshots

### Página Principal

- Grid de cards com fotos e informações básicas
- Filtros no topo
- Paginação no rodapé

### Modal de Detalhes

- Foto ampliada
- Informações completas públicas
- Botão para perfil completo

## Suporte

Para dúvidas ou problemas:

- Abra uma issue no GitHub
- Entre em contato com a equipe de desenvolvimento
