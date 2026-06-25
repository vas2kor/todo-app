# Collaborative Todo (React + FastAPI)

MVP-first collaborative todo app scaffold with architecture that is ready to grow into a full-feature product.

## Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy (async) + Socket.IO
- Auth: OAuth (Google example wiring)
- DB (MVP): SQLite via SQLAlchemy URL
- Future DB: PostgreSQL by changing `DATABASE_URL`
- Dev runtime: Docker Compose
- Cloud-ready target: AWS (ECS/Fargate style container deployment)

## Monorepo Layout

- `frontend/`: React client
- `backend/`: FastAPI API + Socket.IO
- `shared/`: contracts and shared docs
- `infra/aws/`: cloud deployment notes/placeholders

## Local Development

1. Copy `.env.example` to `.env` and fill values.
2. Run `docker compose up --build`.
3. Frontend: `http://localhost:5173`
4. Backend health: `http://localhost:8000/health`

## Non-Docker Development

Frontend:

1. `cd frontend`
2. `npm install`
3. `npm run dev`

Backend:

1. `cd backend`
2. `python -m venv .venv`
3. `.venv\\Scripts\\activate`
4. `pip install -r requirements.txt`
5. `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## MVP Scope Included

- OAuth login route skeleton
- Todo CRUD API
- Socket.IO room join + broadcast for list updates
- Layered backend (`routers`, `services`, `repositories`)
- DB abstraction through SQLAlchemy session/repository pattern

## Full-Feature Ready Direction

- Add list roles (`owner`, `editor`, `viewer`)
- Add presence + activity log tables
- Add optimistic concurrency metadata for conflict handling
- Move from SQLite to PostgreSQL by updating `DATABASE_URL`
- Add managed Redis + WebSocket scaling adapter for multi-instance deployment

## AWS-Ready Notes

- Build/push frontend and backend images to ECR
- Deploy with ECS/Fargate or App Runner
- Use RDS PostgreSQL for production data
- Keep secrets in AWS Secrets Manager/SSM
