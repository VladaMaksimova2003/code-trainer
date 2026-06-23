// src/features/support/components/ReportTaskIssueModal.jsx
// «Сообщить об ошибке» на странице задачи. Один экран (hybrid), chips подставляют draft.
import { useEffect, useState } from "react";
import Modal from "../../../shared/ui/Modal";
import { getTemplates, createTicket } from "../api/supportApi";

const MIN = 20;

export default function ReportTaskIssueModal({
  open,
  onClose,
  taskId,
  taskTitle,
  submissionId = null,
  onSuccess, // (ticket) => void  — для toast «Обращение #N отправлено»
}) {
  const [templates, setTemplates] = useState([]);
  const [category, setCategory] = useState("task_content");
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open) return;
    setBody("");
    setError(null);
    setCategory("task_content");
    getTemplates("task").then(setTemplates).catch(() => setTemplates([]));
  }, [open]);

  const pickChip = (tpl) => {
    setCategory(tpl.category);
    if (tpl.draft) setBody(tpl.draft);
  };

  const trimmed = body.trim();
  const valid = trimmed.length >= MIN;

  const submit = async () => {
    if (!valid || busy) return;
    setBusy(true);
    setError(null);
    try {
      const ticket = await createTicket({
        category,
        body: trimmed,
        task_id: taskId,
        submission_id: submissionId,
        context: { page_url: `/tasks/${taskId}` },
      });
      onSuccess?.(ticket);
      onClose?.();
    } catch {
      setError("Не удалось отправить обращение. Попробуйте позже.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Сообщить об ошибке"
      footer={
        <>
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            Отмена
          </button>
          <button
            type="button"
            className="btn btn-primary disabled:opacity-50"
            disabled={!valid || busy}
            onClick={submit}
          >
            {busy ? "Отправка…" : "Отправить"}
          </button>
        </>
      }
    >
      {taskTitle && (
        <p className="mb-4 text-[13px] text-ink-muted">
          Задание: <span className="font-medium text-ink">«{taskTitle}»</span>
        </p>
      )}

      <label className="mb-2 block text-[13px] font-medium text-ink-muted">Что не так?</label>
      <div className="mb-4 flex flex-wrap gap-2">
        {templates.map((tpl, i) => {
          const active = category === tpl.category;
          return (
            <button
              key={i}
              type="button"
              onClick={() => pickChip(tpl)}
              className={
                "rounded-full border px-3 py-1.5 text-[13px] transition " +
                (active
                  ? "border-lime/45 bg-lime-soft text-lime"
                  : "border-border bg-surface-2 text-ink-muted hover:text-ink")
              }
            >
              {tpl.label}
            </button>
          );
        })}
      </div>

      <label htmlFor="issue-body" className="mb-2 block text-[13px] font-medium text-ink-muted">
        Описание <span className="text-danger">*</span>
      </label>
      <textarea
        id="issue-body"
        value={body}
        onChange={(e) => setBody(e.target.value)}
        rows={5}
        placeholder="Например: Тест №3 — ожидается 0, но проверка требует -1…"
        className="w-full resize-y rounded-md border border-border bg-bg px-3 py-2 text-[13px] text-ink
                   placeholder:text-ink-faint focus:border-lime focus:outline-none focus:ring-2 focus:ring-lime/20"
      />
      <div className="mt-1.5 flex items-center justify-between">
        <span className={"text-[12px] " + (valid ? "text-ink-faint" : "text-ink-faint")}>
          мин. {MIN} символов
        </span>
        <span className="text-[12px] text-ink-faint">{trimmed.length}</span>
      </div>
      {error && <p className="mt-2 text-[12px] text-danger">{error}</p>}
    </Modal>
  );
}
