from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import Response
from socketio import ASGIApp
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db import engine
from app.models import Base
from app.routers import auth, todos
from app.sockets import sio

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _migrate_sqlite_todo_columns()
    yield


api = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
    lifespan=lifespan,
)

api.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    https_only=settings.is_production,
    same_site="lax",
    max_age=600,
)

api.add_middleware(GZipMiddleware, minimum_size=500)

api.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@api.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; connect-src 'self' https: ws: wss:"
    return response

api.include_router(auth.router)
api.include_router(todos.router)


async def _migrate_sqlite_todo_columns() -> None:
    if "sqlite" not in settings.database_url:
        return

    async with engine.begin() as conn:
        rows = await conn.execute(text("PRAGMA table_info(todos)"))
        existing_columns = {row[1] for row in rows.fetchall()}

        if "remind_at" not in existing_columns:
            await conn.execute(text("ALTER TABLE todos ADD COLUMN remind_at VARCHAR(19)"))

        if "repeat_rule" not in existing_columns:
            await conn.execute(text("ALTER TABLE todos ADD COLUMN repeat_rule VARCHAR(16) NOT NULL DEFAULT 'none'"))

        if "category" not in existing_columns:
            await conn.execute(text("ALTER TABLE todos ADD COLUMN category VARCHAR(64)"))



@api.get("/health")
async def health() -> dict[str, str]:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok"}


app = ASGIApp(socketio_server=sio, other_asgi_app=api)
