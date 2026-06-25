import { useEffect, useMemo, useRef, useState } from "react";
import { createTodo, fetchTodos, mapTodoFromApi, toggleTodo, type TodoApi } from "./api";
import { AddTaskModal } from "./components/AddTaskModal";
import { AuthPage } from "./components/AuthPage";
import { socket } from "./socket";
import type { Todo, TodoFormData, User } from "./types";

const DEFAULT_LIST_ID = "default-list";

const PRIORITY_BADGE: Record<string, string> = {
  high: "badge-high",
  medium: "badge-medium",
  low: "badge-low",
};

export function App() {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement | null>(null);
  const completedCount = useMemo(() => todos.filter((t) => t.completed).length, [todos]);
  const pendingCount = todos.length - completedCount;
  const userIdentity = user?.email || user?.phone || "User";
  const avatarInitials = userIdentity
    .split(/[@\s+]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "U";

  function handleAuthSuccess(newToken: string, newUser: User) {
    localStorage.setItem("auth_token", newToken);
    localStorage.setItem("user", JSON.stringify(newUser));
    setUser(newUser);
  }

  function handleLogout() {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user");
    setProfileMenuOpen(false);
    setUser(null);
    setTodos([]);
  }

  useEffect(() => {
    if (!profileMenuOpen) {
      return;
    }

    function handleClickOutside(event: MouseEvent) {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setProfileMenuOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setProfileMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [profileMenuOpen]);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    let mounted = true;

    async function loadTodos() {
      try {
        const initial = await fetchTodos(DEFAULT_LIST_ID);
        if (mounted) setTodos(initial);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadTodos();
    socket.connect();
    socket.emit("join_list", { list_id: DEFAULT_LIST_ID });
    socket.on("todo_updated", (payload: TodoApi[]) => setTodos(payload.map(mapTodoFromApi)));

    return () => {
      mounted = false;
      socket.off("todo_updated");
      socket.disconnect();
    };
  }, [user]);

  if (!user) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  async function handleSave(data: TodoFormData) {
    await createTodo(DEFAULT_LIST_ID, data);
  }

  async function onToggle(todo: Todo) {
    await toggleTodo(todo.id, !todo.completed);
  }

  return (
    <div className="app-page">
      <header className="top-nav">
        <div className="top-nav-title">Task Dashboard</div>
        <div className="profile-dropdown" ref={profileMenuRef}>
          <button
            type="button"
            className="profile-toggle"
            onClick={() => setProfileMenuOpen((prev) => !prev)}
            aria-expanded={profileMenuOpen}
            aria-haspopup="menu"
          >
            <span className="avatar-circle">{avatarInitials}</span>
            <span className="profile-meta">
              <strong>{userIdentity}</strong>
              <span>View profile</span>
            </span>
            <span className="profile-caret">▾</span>
          </button>

          {profileMenuOpen ? (
            <div className="profile-menu" role="menu">
              <button type="button" className="profile-menu-item" onClick={handleLogout} role="menuitem">
                Logout
              </button>
            </div>
          ) : null}
        </div>
      </header>

      <main className="app-shell">
        <aside className="left-rail">
        <div className="brand-block">
          <span className="brand-mark">✓</span>
          <div>
            <strong>FlowBoard</strong>
            <p>Personal workspace</p>
          </div>
        </div>

        <nav className="rail-nav" aria-label="Task sections">
          <button type="button" className="rail-item rail-item--active">
            <span>Inbox</span>
            <strong>{pendingCount}</strong>
          </button>
          <button type="button" className="rail-item">
            <span>Completed</span>
            <strong>{completedCount}</strong>
          </button>
          <button type="button" className="rail-item">
            <span>All Tasks</span>
            <strong>{todos.length}</strong>
          </button>
        </nav>

      </aside>

        <section className="workspace">
        <header className="workspace-header">
          <div>
            <h1>Today</h1>
            <p>Stay focused and finish what matters most.</p>
          </div>
          <button className="btn btn-primary" onClick={() => setModalOpen(true)}>
            + Add Task
          </button>
        </header>

        <section className="panel">
          <div className="meta">
            <span className="stat-pill">{pendingCount} open</span>
            <span className="stat-pill">{completedCount} done</span>
            <span className="stat-pill">{todos.length} total</span>
          </div>

          {loading ? <p className="loading-text">Loading...</p> : null}

          {!loading && todos.length === 0 ? (
            <p className="empty-text">No tasks yet. Click &ldquo;+ Add Task&rdquo; to get started.</p>
          ) : null}

          <ul className="todo-list">
            {todos.map((todo) => (
              <li key={todo.id} className={todo.completed ? "todo-item todo-item--done" : "todo-item"}>
                <label className="todo-item-label">
                  <input
                    type="checkbox"
                    checked={todo.completed}
                    onChange={() => onToggle(todo)}
                  />
                  <div className="todo-item-body">
                    <span className="todo-item-title">{todo.title}</span>
                    {todo.description && (
                      <span className="todo-item-desc">{todo.description}</span>
                    )}
                    <div className="todo-item-meta">
                      {todo.dueDate && (
                        <span className="badge badge-date">📅 {todo.dueDate}</span>
                      )}
                      {todo.remindMe && (
                        <span className="badge badge-remind">⏰ {todo.remindMe.replace("T", " ")}</span>
                      )}
                      {todo.repeat !== "none" && (
                        <span className="badge badge-repeat">🔁 {todo.repeat}</span>
                      )}
                      {todo.category && (
                        <span className="badge badge-category">🏷 {todo.category}</span>
                      )}
                      <span className={`badge ${PRIORITY_BADGE[todo.priority] ?? ""}`}>
                        {todo.priority.charAt(0).toUpperCase() + todo.priority.slice(1)}
                      </span>
                    </div>
                  </div>
                </label>
              </li>
            ))}
          </ul>
        </section>
        </section>

        <AddTaskModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onSave={handleSave}
        />
      </main>
    </div>
  );
}
