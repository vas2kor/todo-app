from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Priority = Literal["low", "medium", "high"]
RepeatRule = Literal["none", "daily", "weekly", "monthly"]


class TodoCreate(BaseModel):
    list_id: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=280)
    description: str | None = Field(default=None, max_length=2000)
    due_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    remind_at: str | None = Field(default=None, max_length=19)
    repeat_rule: RepeatRule = "none"
    category: str | None = Field(default=None, max_length=64)
    priority: Priority = "medium"


class TodoUpdate(BaseModel):
    completed: bool


class TodoRead(BaseModel):
    id: str
    list_id: str
    title: str
    description: str | None
    due_date: str | None
    remind_at: str | None
    repeat_rule: str
    category: str | None
    priority: str
    completed: bool
    updated_at: datetime

    class Config:
        from_attributes = True
