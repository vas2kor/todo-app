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

1. Use `.env.development` for local development and `.env.production` for production values.
2. Keep `.env.example` as the neutral template for creating additional environments (e.g. staging).
3. Optionally create `.env` for local overrides.
4. Run `docker compose up --build`.
5. Frontend: `http://localhost:5500`
6. Backend health: `http://localhost:8000/health`

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

## Production Configuration Notes

- Set `APP_ENV=production` to disable OpenAPI/docs routes.
- Set `EXPOSE_TEST_OTP=false` in production so OTP codes are never returned in API responses.
- Configure `CORS_ALLOWED_ORIGINS` with your deployed frontend origins only.
- Use a strong `SESSION_SECRET` from a secure secret manager.
- Set `VITE_API_BASE_URL` and `VITE_SOCKET_URL` to deployed backend URLs for non-proxied environments.

## Google OAuth Configuration (Implemented)

The app now uses a real Google OAuth authorization code flow:

1. Frontend requests `GET /api/v1/auth/google/login`.
2. Backend generates `state`, stores it in session cookie, and returns Google `oauth_url`.
3. Browser redirects to Google and user consents.
4. Google redirects back to `OAUTH_GOOGLE_REDIRECT_URI` (configured to frontend URL).
5. Frontend reads `code` and `state` from URL and calls `POST /api/v1/auth/google/callback`.
6. Backend validates `state`, exchanges `code` for Google tokens, fetches profile, and returns app auth token.

### 1) Create Google OAuth credentials

- Open Google Cloud Console.
- Select/create a project.
- Go to APIs & Services > Credentials.
- Create OAuth 2.0 Client ID (Web application).
- Add Authorized redirect URI:
	- Dev: `http://localhost:5500/`
	- Prod: `https://your-frontend-domain.com/`

### 2) Set environment variables

In `.env.development`:

- `OAUTH_GOOGLE_CLIENT_ID=<your-dev-client-id>`
- `OAUTH_GOOGLE_CLIENT_SECRET=<your-dev-client-secret>`
- `OAUTH_GOOGLE_REDIRECT_URI=http://localhost:5500/`

In `.env.production`:

- `OAUTH_GOOGLE_CLIENT_ID=<your-prod-client-id>`
- `OAUTH_GOOGLE_CLIENT_SECRET=<your-prod-client-secret>`
- `OAUTH_GOOGLE_REDIRECT_URI=https://your-frontend-domain.com/`

### 3) Verify backend session secret

- Set a strong `SESSION_SECRET`.
- OAuth state validation depends on session middleware and this secret.

### 4) Test the flow locally

- Start app with `APP_ENV=development`.
- Click "Continue with Google".
- Complete consent screen.
- You should be redirected back and logged in automatically.
