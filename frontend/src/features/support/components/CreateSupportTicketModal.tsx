// src/features/support/components/CreateSupportTicketModal.jsx
// Создание обращения в общем контексте (Помощь). Subject + категория + описание.
import { useEffect, useState } from "react";
import Modal from "../../../shared/ui/Modal";
import { getTemplates, createTicket } from "../api/supportApi";
import { SUPPORT_BODY_MAX } from "../constants";

export default function CreateSupportTicketModal({ open, onClose, onCreated }) {
  const [templates, setTemplates] = useState([]);
  const [category, setCategory] = useState("technical");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open) return;
    setSubject("");
    setBody("");
    setError(null);
    setCategory("technical");
    getTemplates("general").then(setTemplates).catch(() => setTemplates([]));
  }, [open]);

  const pickChip = (tpl: unknown) => {
    setCategory(tpl.category);
    if (tpl.draft) setBody(tpl.draft);
  };

  const trimmed = body.trim();
  const valid = trimmed.length > 0 && trimmed.length <= SUPPORT_BODY_MAX;
  const overLimit = trimmed.length > SUPPORT_BODY_MAX;

  const submit = async () => {
    if (!valid || busy) return;
    setBusy(true);
    setError(null);
    try {
      const ticket = await createTicket({ category, subject: subject.trim() || undefined, body: trimmed });
      onCreated?.(ticket);
      onClose?.();
    } catch {
      setError("Не удалось создать обращение.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Новое обращение"
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
            {busy ? "Отправка…" : "Создать"}
          </button>
        </>
      }
    >
      <label className="mb-2 block text-[13px] font-medium text-ink-muted">Категория</label>
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

      <label htmlFor="ticket-subject" className="mb-2 block text-[13px] font-medium text-ink-muted">
        Тема <span className="text-ink-faint">(опционально)</span>
      </label>
      <input
        id="ticket-subject"
        value={subject}
        onChange={(e: unknown) => setSubject(e.target.value)}
        placeholder="Кратко: в чём проблема"
        className="mb-4 w-full rounded-md border border-border bg-bg px-3 py-2 text-[13px] text-ink
                   placeholder:text-ink-faint focus:border-lime focus:outline-none focus:ring-2 focus:ring-lime/20"
      />

      <label htmlFor="ticket-body" className="mb-2 block text-[13px] font-medium text-ink-muted">
        Описание <span className="text-danger">*</span>
      </label>
      <textarea
        id="ticket-body"
        value={body}
        onChange={(e: unknown) => setBody(e.target.value)}
        rows={5}
        maxLength={SUPPORT_BODY_MAX}
        placeholder="Опишите, что произошло и как воспроизвести…"
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
