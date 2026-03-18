# Relatório Técnico - SaaS Controle Financeiro

## 1. Visão Geral
O projeto está em estágio **MVP avançado**, com evolução consistente de arquitetura e domínio. O sistema hoje cobre autenticação, gestão de transações, dashboard analítico, perfil do usuário e uma camada inicial de inteligência financeira no backend.

A arquitetura está organizada por responsabilidade:
- frontend por domínio (`views/*`) e camadas (`components`, `services`, `utils`, `composables`)
- backend Flask modular (`api/routes`, `api/middlewares`, `api/security`, `services`, `db`, `core`)

## 2. Stack Tecnológica
### Frontend
- Vue 3 (Composition API)
- Vite
- Vue Router
- Axios
- Tailwind CSS + DaisyUI
- ECharts
- Vitest
- ESLint + Oxlint

### Backend
- Python + Flask
- Flask-CORS
- Flask-Bcrypt
- PyJWT
- PostgreSQL (psycopg2)

## 3. Arquitetura Atual (Resumo)
### Frontend (`frontend/controle-financeiro/src`)
- `views/auth`: login e registro
- `views/marketing`: landing page
- `views/dashboard`: dashboard analítico
- `views/transactions`: tela unificada de operações de transação
- `views/profile`: perfil, configurações e segurança
- `components/layout`: Navbar
- `components/feedback`: NotificationToast
- `services/http`, `services/auth`, `services/transactions`, `services/profile`
- `utils`: regras puras de dashboard, lista e formulário de transações, validações de perfil

### Backend (`backend`)
- `api/routes/users.py`: auth, perfil, avatar, segurança
- `api/routes/transactions.py`: operações + CRUD de transações
- `api/routes/dashboard.py`: resumo inteligente mensal
- `services/`: domínio puro (agregação, projeção, recomendação, explicação, cache)
- `services/cache/`: abstração + implementação em memória
- `tests/`: testes de API, domínio e cache

## 4. Funcionalidades Implementadas
### Autenticação e Sessão
- Cadastro de usuário
- Login com JWT
- Logout com revogação de token (JTI)
- Proteção de rotas no backend via middleware
- Redirecionamento para login em casos de 401 no frontend
- Rate limit e lockout temporário no fluxo de login/cadastro

### Transações e Operações
- CRUD de transações no backend (`create`, `read`, `update`, `delete`)
- Operações financeiras por usuário (`listar` e `criar`)
- Validação de ownership por `id_user_fk`
- Tela `TransactionsView` com:
  - listagem paginada
  - filtros por período
  - busca textual
  - ordenação
  - criação/edição/exclusão em fluxo unificado

### Dashboard (Frontend)
- Estrutura analítica com:
  - KPIs principais (receitas, despesas, saldo)
  - gráfico comparativo
  - insight principal
  - meta mensal e barra de progresso
- Filtros de período: `este_mes`, `mes_anterior`, `3m`, `6m`
- Persistência de filtro selecionado no `localStorage`

### Dashboard Inteligente (Backend)
- Endpoint: `GET /api/dashboard/intelligent-summary`
- Suporte a `?month=YYYY-MM` (default: mês atual)
- Pipeline em camadas sem cálculo duplicado no controller:
  1. busca transações do mês
  2. `aggregate_transactions`
  3. `calculate_projection`
  4. `generate_recommendations`
  5. `generate_natural_summary`
- Resposta estruturada:
  - `period`
  - `totals`
  - `projection`
  - `recommendations`
  - `natural_summary`

### Camada de Cache Desacoplada (Backend)
- Contrato abstrato: `CacheBackend`
- Implementação atual: `MemoryCache` (TTL + lock + delete por prefixo)
- Injeção via `cache_backend` em `services/cache/__init__.py`
- Cache no endpoint inteligente:
  - chave: `dashboard:{user_id}:{month}`
  - TTL: 900s
- Invalidação por usuário após:
  - criar transação
  - atualizar transação
  - excluir transação
  - atualizar perfil quando `monthly_goal_value` é enviado

### Perfil
- Leitura e atualização de dados básicos
- Upload/remoção de avatar (armazenamento em `bytea`)
- Persistência de tema
- Fluxo de alterações sensíveis com token mock
- Meta mensal (`monthly_goal_value`) com fallback para schema incompleto

## 5. Estado Atual de Qualidade
### Testes Backend disponíveis
- `test_api_minimum.py` (fluxos críticos de API)
- `test_dashboard_intelligent_summary.py` (endpoint inteligente)
- `test_financial_aggregator.py` (agregação financeira)
- `test_recommendation_engine.py` (regras determinísticas)
- `test_ai_explainer.py` (sumário textual determinístico)
- `test_cache_layer.py` (hit/miss/ttl/delete_pattern/invalidação)

### Testes Frontend disponíveis
- `dashboardUtils.test.js`
- `transactionListUtils.test.js`
- `transactionFormUtils.test.js`
- `profileValidators.test.js`

## 6. Segurança (Status)
### Implementado
- JWT com claims e validações obrigatórias
- Revogação de token no logout
- Rate limit e lockout de login
- Queries parametrizadas
- Autorização por usuário em endpoints sensíveis
- Invalidação de cache por usuário após mutações relevantes

### Próximos incrementos recomendados
- Refresh token com rotação
- CORS segmentado por ambiente
- Headers de segurança adicionais
- Auditoria de ações sensíveis
- Rate limiting por rota de maior risco

## 7. Pontos de Atenção
1. **Migrações de banco**
- O projeto ainda depende de scripts SQL incrementais sem framework de versionamento formal.

2. **Timezone**
- Existe tratamento no backend, mas ainda recomenda-se política única ponta a ponta (UTC + conversão na borda).

3. **Observabilidade**
- Falta instrumentação consolidada (métricas, tracing e alertas).

4. **Produto comercial**
- Módulo de assinatura/planos/cobrança ainda não implementado.

## 8. Maturidade Atual (Resumo)
- **Produto:** funcional para uso real individual
- **Arquitetura:** boa separação de camadas, incluindo domínio puro no backend
- **UI/UX:** moderna, responsiva e mais organizada entre análise (dashboard) e operação (transações)
- **Confiabilidade:** intermediária para alta no escopo atual
- **Prontidão para monetização:** parcial (falta camada comercial)

## 9. Próximos Passos Prioritários
1. Implementar módulo de assinatura (planos, limites e cobrança).
2. Introduzir versionamento formal de migrações (ex.: Alembic).
3. Expandir testes de integração backend para todos os fluxos sensíveis de perfil/segurança.
4. Expandir testes de componente frontend para estados críticos (erro, vazio, loading) nas views principais.
5. Consolidar política definitiva de timezone e padronizar persistência/apresentação.
6. Evoluir cache para backend distribuído (Redis) reaproveitando `CacheBackend` sem acoplamento no controller.

---
Relatório atualizado em: **09/03/2026**
