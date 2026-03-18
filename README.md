# Controle Financeiro

Aplicação full stack de controle financeiro pessoal com autenticação por usuário, dashboard com indicadores, gestão de transações, perfil, segurança de conta e evolução para recursos de assinatura.

## Visão geral

O projeto está dividido em:

- `frontend/controle-financeiro`: aplicação web em Vue 3.
- `backend`: API em Flask com integração PostgreSQL.

Fluxos já disponíveis:

- cadastro e login;
- dashboard com KPIs e comparativo de receitas vs despesas;
- criação, listagem e edição de transações;
- gerenciamento de perfil e preferências;
- fluxo de segurança para alterações sensíveis;
- base para gestão de assinatura.

## Stack

### Frontend

- Vue 3
- Vite
- Vue Router
- Axios
- Tailwind CSS
- DaisyUI
- ECharts
- Pinia
- Vitest

### Backend

- Python
- Flask
- Flask-CORS
- Flask-Bcrypt
- PyJWT
- PostgreSQL

## Estrutura

```text
.
├── backend
│   ├── api
│   ├── core
│   ├── db
│   ├── services
│   ├── sql
│   └── tests
├── frontend
│   └── controle-financeiro
│       ├── src
│       └── public
└── README.md
```

## Pré-requisitos

- Node.js 20+
- npm
- Python 3.11+ recomendado
- PostgreSQL

## Configuração do ambiente

### 1. Backend

Crie o arquivo `backend/.env` com base em `backend/.env.example`.

Variáveis principais:

```env
host_db=127.0.0.1
port_db=5432
user_db=postgres
password_db=postgres
database_db=controle_financeiro

SECRET_KEY=change-me
JWT_ISSUER=controle-financeiro-api
JWT_AUDIENCE=controle-financeiro-web

CAKTO_WEBHOOK_SECRET=...
CAKTO_PRODUCT_CHECKOUT_URL=...
```

Observações:

- ao iniciar, o backend tenta aplicar migrações SQL necessárias automaticamente;
- o banco deve existir antes de subir a aplicação.

### 2. Frontend

Crie o arquivo `frontend/controle-financeiro/.env` com base em `frontend/controle-financeiro/.env.example`.

Exemplo:

```env
VITE_API_BASE_URL=http://127.0.0.1:5000
VITE_CAKTO_CHECKOUT_URL=https://pay.cakto.com.br/...
```

## Instalação

### Frontend

```bash
cd frontend/controle-financeiro
npm install
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Executando localmente

### Subir a API

Na raiz do projeto:

```bash
source backend/venv/bin/activate
python -m backend.app
```

A API sobe por padrão em `http://127.0.0.1:5000`.

### Subir o frontend

```bash
cd frontend/controle-financeiro
npm run dev
```

O frontend sobe por padrão em `http://127.0.0.1:5173`.

## Comandos úteis

### Frontend

```bash
cd frontend/controle-financeiro
npm run dev
npm run build
npm run preview
npm run test:unit
npm run lint
```

### Backend

```bash
source backend/venv/bin/activate
python -m pytest backend/tests
```

## Rotas e módulos principais

### Frontend

- `/`: landing page
- `/login`: autenticação
- `/register`: cadastro
- `/dashboard`: visão consolidada
- `/transactions`: transações
- `/profile`: perfil e configurações

### Backend

- `/api/users`: autenticação, perfil, avatar e segurança
- `/api/transaction`: operações e transações
- `/api/dashboard`: resumo e indicadores
- `/api/subscription`: assinatura e integrações relacionadas

## Qualidade e testes

O frontend possui testes unitários com Vitest em `frontend/controle-financeiro/src`.

O backend possui testes em `backend/tests`, cobrindo API mínima, assinatura, dashboard inteligente, cache e serviços auxiliares.

## Observações de desenvolvimento

- o frontend consome a API via variável de ambiente;
- o backend permite CORS para `http://localhost:5173`;
- o projeto segue organização por domínio e responsabilidade;
- há arquivos de contexto e relatório no repositório para apoio de manutenção: `frontend/controle-financeiro/contexto.md` e `Relatório.md`.
