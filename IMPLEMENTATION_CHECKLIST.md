# Implementation Checklist

Last updated: 2026-06-17

## Implemented

- [x] Monorepo structure created (`frontend`, `backend`, `shared`, `infra/aws`).
- [x] React + TypeScript + Vite frontend scaffolded manually.
- [x] FastAPI backend scaffolded with layered structure (`routers`, `services`, `repositories`).
- [x] SQLite-backed async SQLAlchemy setup (`DATABASE_URL`-driven for future DB swap).
- [x] Todo API endpoints implemented (list, create, update completion).
- [x] Socket.IO server/client integration for real-time todo list updates.
- [x] Frontend todo UI wired to API and socket updates.
- [x] Environment templates added (`.env.example`, `frontend/.env.example`).
- [x] Dockerfiles and `docker-compose.yml` added for containerized workflow.
- [x] AWS readiness notes added in `infra/aws/README.md`.
- [x] Proxy helper script added (`set-pxproxy.ps1`).
- [x] Local no-Docker VS Code tasks configured (`.vscode/tasks.json`).
- [x] Dependency installation completed for frontend and backend.
- [x] Build/validation completed:
  - [x] Frontend production build succeeded.
  - [x] Backend compile/import checks succeeded.
  - [x] Runtime health checks succeeded (`/health`, frontend HTTP 200).

## In Progress

- [ ] OAuth integration hardening (currently skeleton routes; full token exchange/session flow pending).
- [ ] Local run documentation alignment (README still prioritizes Docker, while active verified path is no-Docker task flow).
- [ ] Production-grade Socket.IO scaling design (Redis adapter and multi-instance strategy not implemented yet).

## Yet To Be Implemented

### Product Features

- [ ] Shared list membership and role enforcement (`owner`, `editor`, `viewer`).
- [ ] User presence indicators (who is online/in a list).
- [ ] Activity/audit log for collaborative actions.
- [ ] Conflict-resolution strategy for concurrent edits (versioning/optimistic concurrency hooks).
- [ ] Advanced task capabilities (priorities, due dates, reminders, labels/categories).

### Auth and Security

- [ ] End-to-end OAuth flow with provider token validation and callback handling.
- [ ] Session/JWT strategy finalized (access + refresh handling).
- [ ] Route authorization middleware/guards.
- [ ] Secure secret management strategy for local + cloud.

### Data and Platform

- [ ] Database migrations (e.g., Alembic) and schema evolution workflow.
- [ ] PostgreSQL deployment profile and migration from SQLite.
- [ ] Test suite expansion (unit, integration, API, socket behavior).
- [ ] CI pipeline (lint, test, build, image publish).
- [ ] AWS infrastructure as code (ECS/App Runner, RDS, secrets, networking).
- [ ] Observability (structured logging, metrics, tracing, alerting).

## Notes

- Docker-based launch task currently cannot be executed on this machine because Docker CLI is not installed.
- Current local development is verified via direct backend/frontend process execution and VS Code no-Docker task setup.
