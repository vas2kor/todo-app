import { FormEvent, useEffect, useRef, useState } from "react";
import type { Priority, RepeatRule, TodoFormData } from "../types";

interface Props {
  open: boolean;
  onClose: () => void;
  onSave: (data: TodoFormData) => Promise<void>;
}

const EMPTY: TodoFormData = {
  title: "",
  description: "",
  dueDate: "",
  remindMe: "",
  repeat: "none",
  category: "",
  priority: "medium",
};

export function AddTaskModal({ open, onClose, onSave }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState<TodoFormData>(EMPTY);
  const [titleError, setTitleError] = useState("");
  const [saving, setSaving] = useState(false);

  // Sync open/close with native <dialog>
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open) {
      dialog.showModal();
      titleRef.current?.focus();
    } else {
      dialog.close();
    }
  }, [open]);

  // Close when user presses Escape via native dialog event
  function handleDialogClose() {
    if (!saving) {
      resetAndClose();
    }
  }

  function resetAndClose() {
    setForm(EMPTY);
    setTitleError("");
    setSaving(false);
    onClose();
  }

  function handleChange(field: keyof TodoFormData, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (field === "title") setTitleError("");
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmedTitle = form.title.trim();
    if (!trimmedTitle) {
      setTitleError("Title is required.");
      titleRef.current?.focus();
      return;
    }

    setSaving(true);
    try {
      await onSave({
        title: trimmedTitle,
        description: form.description?.trim() || undefined,
        dueDate: form.dueDate || undefined,
        remindMe: form.remindMe || undefined,
        repeat: form.repeat,
        category: form.category?.trim() || undefined,
        priority: form.priority,
      });
      resetAndClose();
    } catch {
      setSaving(false);
    }
  }

  return (
    <dialog ref={dialogRef} className="modal" onClose={handleDialogClose}>
      <form onSubmit={handleSubmit} className="modal-form" noValidate>
        <header className="modal-header">
          <h2 className="modal-title">Add Task</h2>
          <button
            type="button"
            className="modal-close-btn"
            onClick={resetAndClose}
            aria-label="Close dialog"
            disabled={saving}
          >
            ✕
          </button>
        </header>

        <div className="modal-body">
          {/* Title */}
          <div className="field">
            <label className="field-label" htmlFor="task-title">
              Title <span className="required" aria-hidden="true">*</span>
            </label>
            <input
              id="task-title"
              ref={titleRef}
              type="text"
              value={form.title}
              onChange={(e) => handleChange("title", e.target.value)}
              placeholder="What needs to be done?"
              aria-required="true"
              aria-invalid={titleError ? "true" : undefined}
              aria-describedby={titleError ? "title-error" : undefined}
              className={titleError ? "input-error" : ""}
            />
            {titleError && (
              <span id="title-error" className="field-error" role="alert">
                {titleError}
              </span>
            )}
          </div>

          {/* Description */}
          <div className="field">
            <label className="field-label" htmlFor="task-description">
              Description
            </label>
            <textarea
              id="task-description"
              value={form.description}
              onChange={(e) => handleChange("description", e.target.value)}
              placeholder="Optional details..."
              rows={3}
            />
          </div>

          {/* Due Date + Remind Me */}
          <div className="field-row">
            <div className="field">
              <label className="field-label" htmlFor="task-due-date">
                Due Date
              </label>
              <input
                id="task-due-date"
                type="date"
                value={form.dueDate}
                onChange={(e) => handleChange("dueDate", e.target.value)}
              />
            </div>

            <div className="field">
              <label className="field-label" htmlFor="task-remind-me">
                Remind Me
              </label>
              <input
                id="task-remind-me"
                type="datetime-local"
                value={form.remindMe}
                onChange={(e) => handleChange("remindMe", e.target.value)}
              />
            </div>
          </div>

          {/* Repeat + Priority */}
          <div className="field-row">
            <div className="field">
              <label className="field-label" htmlFor="task-repeat">
                Repeat
              </label>
              <select
                id="task-repeat"
                value={form.repeat}
                onChange={(e) => handleChange("repeat", e.target.value as RepeatRule)}
              >
                <option value="none">Never</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div className="field">
              <label className="field-label" htmlFor="task-priority">
                Priority
              </label>
              <select
                id="task-priority"
                value={form.priority}
                onChange={(e) => handleChange("priority", e.target.value as Priority)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          <div className="field">
            <label className="field-label" htmlFor="task-category">
              Category
            </label>
            <input
              id="task-category"
              type="text"
              value={form.category}
              onChange={(e) => handleChange("category", e.target.value)}
              placeholder="e.g. Work, Personal"
              maxLength={64}
            />
          </div>
        </div>

        <footer className="modal-footer">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={resetAndClose}
            disabled={saving}
          >
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Saving…" : "Save"}
          </button>
        </footer>
      </form>
    </dialog>
  );
}
