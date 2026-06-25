from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from socketio import ASGIApp
from sqlalchemy import text

from app.config import settings
from app.db import engine
from app.models import Base
from app.routers import auth, todos
from app.sockets import sio

api = FastAPI(title=settings.app_name)

api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",  # vite preview
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

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


@api.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _migrate_sqlite_todo_columns()


@api.get("/health")
async def health() -> dict[str, str]:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok"}


app = ASGIApp(socketio_server=sio, other_asgi_app=api)
