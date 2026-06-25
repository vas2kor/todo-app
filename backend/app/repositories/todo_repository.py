from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Todo


class TodoRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_list_id(self, list_id: str) -> list[Todo]:
        query = select(Todo).where(Todo.list_id == list_id).order_by(Todo.updated_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        list_id: str,
        title: str,
        description: str | None = None,
        due_date: str | None = None,
        remind_at: str | None = None,
        repeat_rule: str = "none",
        category: str | None = None,
        priority: str = "medium",
    ) -> Todo:
        todo = Todo(
            list_id=list_id,
            title=title,
            description=description,
            due_date=due_date,
            remind_at=remind_at,
            repeat_rule=repeat_rule,
            category=category,
            priority=priority,
        )
        self.db.add(todo)
        await self.db.commit()
        await self.db.refresh(todo)
        return todo

    async def update_completed(self, todo_id: str, completed: bool) -> Todo | None:
        todo = await self.db.get(Todo, todo_id)
        if not todo:
            return None
        todo.completed = completed
        await self.db.commit()
        await self.db.refresh(todo)
        return todo
