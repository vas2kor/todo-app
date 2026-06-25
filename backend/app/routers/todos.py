from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.repositories.todo_repository import TodoRepository
from app.schemas import TodoCreate, TodoRead, TodoUpdate
from app.services.todo_service import TodoService
from app.sockets import sio

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])


def build_service(db: AsyncSession) -> TodoService:
    return TodoService(TodoRepository(db))


@router.get("", response_model=list[TodoRead])
async def list_todos(list_id: str, db: AsyncSession = Depends(get_db)):
    service = build_service(db)
    return await service.list_todos(list_id)


@router.post("", response_model=TodoRead)
async def create_todo(payload: TodoCreate, db: AsyncSession = Depends(get_db)):
    service = build_service(db)
    todo = await service.create_todo(
        payload.list_id,
        payload.title,
        payload.description,
        payload.due_date,
        payload.remind_at,
        payload.repeat_rule,
        payload.category,
        payload.priority,
    )
    todos = await service.list_todos(payload.list_id)
    await sio.emit("todo_updated", [TodoRead.model_validate(item).model_dump(mode="json") for item in todos], room=payload.list_id)
    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(todo_id: str, payload: TodoUpdate, db: AsyncSession = Depends(get_db)):
    service = build_service(db)
    todo = await service.update_todo_completed(todo_id, payload.completed)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todos = await service.list_todos(todo.list_id)
    await sio.emit("todo_updated", [TodoRead.model_validate(item).model_dump(mode="json") for item in todos], room=todo.list_id)
    return todo
