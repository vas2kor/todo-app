import type { Todo, TodoFormData } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export type TodoApi = {
  id: string;
  list_id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  remind_at: string | null;
  repeat_rule: "none" | "daily" | "weekly" | "monthly";
  category: string | null;
  priority: "low" | "medium" | "high";
  completed: boolean;
  updated_at: string;
};

export function mapTodoFromApi(todo: TodoApi): Todo {
  return {
    id: todo.id,
    listId: todo.list_id,
    title: todo.title,
    description: todo.description,
    dueDate: todo.due_date,
    remindMe: todo.remind_at,
    repeat: todo.repeat_rule,
    category: todo.category,
    priority: todo.priority,
    completed: todo.completed,
    updatedAt: todo.updated_at,
  };
}

export async function fetchTodos(listId: string): Promise<Todo[]> {
  const response = await fetch(`${API_BASE}/api/v1/todos?list_id=${listId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch todos");
  }
  const data = (await response.json()) as TodoApi[];
  return data.map(mapTodoFromApi);
}

export async function createTodo(listId: string, data: TodoFormData): Promise<Todo> {
  const response = await fetch(`${API_BASE}/api/v1/todos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      list_id: listId,
      title: data.title,
      description: data.description ?? null,
      due_date: data.dueDate ?? null,
      remind_at: data.remindMe ?? null,
      repeat_rule: data.repeat,
      category: data.category ?? null,
      priority: data.priority,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to create todo");
  }
  const created = (await response.json()) as TodoApi;
  return mapTodoFromApi(created);
}

export async function toggleTodo(todoId: string, completed: boolean): Promise<Todo> {
  const response = await fetch(`${API_BASE}/api/v1/todos/${todoId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ completed }),
  });
  if (!response.ok) {
    throw new Error("Failed to update todo");
  }
  const updated = (await response.json()) as TodoApi;
  return mapTodoFromApi(updated);
}
