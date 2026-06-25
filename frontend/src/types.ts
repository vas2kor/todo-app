export type Priority = "low" | "medium" | "high";
export type RepeatRule = "none" | "daily" | "weekly" | "monthly";

export interface User {
  id: string;
  email: string | null;
  phone: string | null;
  oauth_provider: string | null;
  verified_at: string | null;  // ISO datetime string from JSON serialization
}

export interface AuthToken {
  access_token: string;
  user: User;
}

export interface Todo {
  id: string;
  title: string;
  description: string | null;
  dueDate: string | null;
  remindMe: string | null;
  repeat: RepeatRule;
  category: string | null;
  priority: Priority;
  completed: boolean;
  listId: string;
  updatedAt: string;
}

export interface TodoFormData {
  title: string;
  description?: string;
  dueDate?: string;
  remindMe?: string;
  repeat: RepeatRule;
  category?: string;
  priority: Priority;
}
