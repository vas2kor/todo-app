from app.repositories.todo_repository import TodoRepository


class TodoService:
    def __init__(self, repository: TodoRepository) -> None:
        self.repository = repository

    async def list_todos(self, list_id: str):
        return await self.repository.list_by_list_id(list_id)

    async def create_todo(
        self,
        list_id: str,
        title: str,
        description: str | None = None,
        due_date: str | None = None,
        remind_at: str | None = None,
        repeat_rule: str = "none",
        category: str | None = None,
        priority: str = "medium",
    ):
        return await self.repository.create(list_id, title, description, due_date, remind_at, repeat_rule, category, priority)

    async def update_todo_completed(self, todo_id: str, completed: bool):
        return await self.repository.update_completed(todo_id, completed)
