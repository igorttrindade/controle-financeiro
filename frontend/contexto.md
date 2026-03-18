  # Contexto do Projeto - Controle Financeiro

  ## 1. O que este sistema faz
  Este sistema é uma plataforma SaaS de controle financeiro pessoal com autenticação por usuário.

  Fluxo atual principal:
  - cadastro e login de usuário;
  - dashboard com KPIs e gráfico mensal (receitas vs despesas);
  - criação, listagem e edição de transações;
  - criação rápida de operações financeiras (categorias/tipos);
  - gestão de perfil (dados básicos, avatar por upload, preferências visuais);
  - fluxo de segurança para mudanças sensíveis (e-mail/senha) com confirmação por token mock;
  - gestão de sessão com JWT.

  Objetivo funcional central:
  - permitir que cada usuário acompanhe entradas e despesas de forma simples, visual e segura.

  ## 2. Onde devemos chegar
  Evoluir de um MVP funcional para uma aplicação de gestão financeira mais completa, com:

  - gestão de assinatura/plano;
  - filtros avançados (data, tipo, operação) e relatórios;
  - dashboards com comparativos por período;
  - observabilidade e auditoria de ações sensíveis;
  - endurecimento de segurança e validações;
  - melhor experiência mobile e refinamento de performance.

  Meta de produto:
  - transformar o sistema em um painel financeiro confiável para uso recorrente, com dados claros e decisões orientadas por métricas.

  ## 3. Tecnologias utilizadas

  ### Frontend
  - Vue 3 (Composition API)
  - Vite
  - Vue Router
  - Axios
  - Tailwind CSS
  - DaisyUI
  - ECharts (gráficos do dashboard)
  - Pinia (disponível no projeto)
  - ESLint + Oxlint (qualidade de código)
  - Vitest (testes unitários)

  ### Backend (integração com frontend)
  - Python
  - Flask
  - Flask-CORS
  - Flask-Bcrypt
  - PyJWT
  - PostgreSQL (psycopg2)

  ## 4. Arquitetura atual (resumo)

  ### Frontend (`src/`)
  - `views/` por domínio:
    - `auth/` (login, registro)
    - `dashboard/` (visão consolidada)
    - `marketing/` (landing/home)
    - `transactions/` (criação e edição)
    - `profile/` (perfil, configurações, segurança)
  - `components/` por tipo:
    - `layout/` (Navbar)
    - `feedback/` (toasts)
  - `services/` por responsabilidade:
    - `http/` (cliente API base)
    - `auth/` (autenticação)
    - `transactions/` (operações e transações)
    - `profile/` (perfil/avatar/segurança)
  - `composables/`:
    - `useTheme`
    - `useNotifications`
  - `utils/`:
    - regras de cálculo do dashboard
    - validações de formulários (transação e perfil)

  ### Backend
  - `api/routes/`:
    - `users.py` (auth, perfil, avatar, segurança)
    - `transactions.py` (operações e transações)
  - `api/middlewares/`:
    - autenticação JWT
  - `api/security/`:
    - revogação de tokens (logout)
  - `core/`:
    - extensões e configurações
  - `db/`:
    - conexão com banco
  - `sql/`:
    - scripts de criação/migração
  - `tests/`:
    - testes mínimos de API

  ## 5. Diretrizes para próximos passos
  - manter organização por domínio e responsabilidade;
  - evitar acoplamento entre UI e regra de negócio;
  - manter contratos de API claros e versionáveis;
  - ampliar cobertura de testes para fluxos críticos (perfil/segurança/transações);
  - preservar consistência visual e responsividade;
  - monitorar performance do frontend (bundle size e renderizações da dashboard).
