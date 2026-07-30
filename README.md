# JAC Face Id Management System

Authentication, access control, and face recognition device management platform.

## Features

- User authentication (JWT, LDAP, OAuth2)
- Role-based access control (RBAC)
- Face ID device management (100+ devices)
- Personnel management with photo registration
- Recognition records and access logs
- Real-time device callbacks and event handling

## Running

### Backend (FastAPI + PostgreSQL)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
uv run alembic upgrade head
```

### Frontend (React 19 + Vite)

```bash
cd frontend
npm install
npm run generate-types   # backend must be running
npm run dev              # http://localhost:5175
```

## Architecture

See `AGENTS.md` for full module structure, conventions, and API documentation.
