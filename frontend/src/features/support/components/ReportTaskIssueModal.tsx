interface ReportTaskIssueModalProps {
  open: unknown
  onClose: (...args: unknown[]) => unknown
  taskId: unknown
  taskTitle: unknown
  submissionId?: unknown | null
  issueContext?: unknown | null
}

// src/features/support/components/ReportTaskIssueModal.jsx
// «Сообщить об ошибке» на странице задачи — только описание, маршрутизация к преподавателю.
import { useEffect, useState } from "react";
import Modal from "../../../shared/ui/Modal";
import { createTicket } from "../api/supportApi";
import { SUPPORT_BODY_MAX } from "../constants";
import { formatSupportError } from "../formatSupportError";

const TASK_ISSUE_CATEGORY = "task_content";

export default function ReportTaskIssueModal({

  open,
  onClose,
  taskId,
  taskTitle,
  submissionId = null,
  issueContext = null,
  onSuccess, // (ticket: unknown) => void  — для toast «Обращение #N отправлено»

}: ReportTaskIssueModalProps) {
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open) return;
    setBody("");
    setError(null);
  }, [open]);

  const trimmed = body.trim();
  const valid = trimmed.length > 0 && trimmed.length <= SUPPORT_BODY_MAX;
  const overLimit = trimmed.length > SUPPORT_BODY_MAX;

  const submit = async () => {
    if (!valid || busy) return;
    setBusy(true);
    setError(null);
    try {
      const ticket = await createTicket({
        category: TASK_ISSUE_CATEGORY,
        body: trimmed,
        task_id: taskId,
        submission_id: submissionId,
        context: issueContext ?? { page_url: `/tasks/${taskId}` },
      });
      onSuccess?.(ticket);
      onClose?.();
    } catch (err) {
      setError(formatSupportError(err));
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

      <label htmlFor="issue-body" className="mb-2 block text-[13px] font-medium text-ink-muted">
        Описание <span className="text-danger">*</span>
      </label>
      <textarea
        id="issue-body"
        value={body}
        onChange={(e: unknown) => setBody(e.target.value)}
        rows={5}
        maxLength={SUPPORT_BODY_MAX}
        placeholder="Например: Тест №3 — ожидается 0, но проверка требует -1…"
        className="w-full resize-y rounded-md border border-border bg-bg px-3 py-2 text-[13px] text-ink
                   placeholder:text-ink-faint focus:border-lime focus:outline-none focus:ring-2 focus:ring-lime/20"
      />
      <div className="mt-1.5 flex items-center justify-between">
        <span className={"text-[12px] " + (overLimit ? "text-danger" : "text-ink-faint")}>
          {overLimit ? `Не больше ${SUPPORT_BODY_MAX} символов` : "Кратко опишите проблему"}
        </span>
        <span className={"text-[12px] " + (overLimit ? "text-danger" : "text-ink-faint")}>
          {trimmed.length}/{SUPPORT_BODY_MAX}
        </span>
      </div>
      {error && <p className="mt-2 text-[12px] text-danger">{error}</p>}
    </Modal>
  );
}
