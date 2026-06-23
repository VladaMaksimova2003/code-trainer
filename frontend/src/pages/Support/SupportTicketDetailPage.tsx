// src/pages/Support/SupportTicketDetailPage.jsx
// Диалог тикета (chat-layout) + поле ответа. Маршрут /support/tickets/:id
import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate, useOutletContext } from "react-router-dom";
import { getTicket, postMessage, SUPPORT_CATEGORIES } from "../../features/support/api/supportApi";
import StatusPill from "../../features/support/components/StatusPill";
import { formatAbsolute } from "../../shared/lib/relativeTime";

const CAT_LABEL = Object.fromEntries(SUPPORT_CATEGORIES.map((c) => [c.id, c.label]));

export default function SupportTicketDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useOutletContext() ?? {};
  const userId = user?.id ?? null;
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);
  const listRef = useRef(null);

  const load = () => {
    setLoading(true);
    getTicket(id, userId)
      .then(setTicket)
      .finally(() => setLoading(false));
  };
  useEffect(load, [id, userId]);

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [ticket?.messages?.length]);

  const send = async (e) => {
    e?.preventDefault();
    const body = reply.trim();
    if (!body || busy) return;
    setBusy(true);
    try {
      const msg = await postMessage(id, body, userId);
      setTicket((t) => ({ ...t, messages: [...(t.messages || []), msg] }));
      setReply("");
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <p className="px-5 py-6 text-[13px] text-ink-faint">Загрузка…</p>;
  if (!ticket) return <p className="px-5 py-6 text-[13px] text-danger">Обращение не найдено.</p>;

  const closed = ticket.status === "closed" || ticket.status === "resolved";

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col">
      {/* header */}
      <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-3">
        <div className="flex min-w-0 items-center gap-3">
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => navigate("/support")}>
            ←
          </button>
          <div className="min-w-0">
            <div className="truncate text-[15px] font-semibold text-ink">
              #{ticket.id} · {ticket.subject}
            </div>
            <div className="text-[12px] text-ink-faint">{CAT_LABEL[ticket.category] || ticket.category}</div>
          </div>
        </div>
        <StatusPill status={ticket.status} />
      </div>

      {/* messages */}
      <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto px-5 py-4">
        {(ticket.messages || []).map((m) => {
          if (m.author === "system" || m.message_type === "system") {
            return (
              <div key={m.id} className="flex justify-center">
                <span className="rounded-full bg-surface-2 px-3 py-1 text-[12px] text-ink-faint">
                  {m.body}
                </span>
              </div>
            );
          }
          const mine = m.author === "you";
          return (
            <div key={m.id} className={"flex " + (mine ? "justify-end" : "justify-start")}>
              <div
                className={
                  "max-w-[80%] rounded-xl px-3.5 py-2.5 " +
                  (mine
                    ? "bg-lime-soft border border-lime/30"
                    : "bg-surface-2 border border-border")
                }
              >
                <div className="mb-1 flex items-center gap-2 text-[12px]">
                  <span className="font-semibold text-ink">{m.author_name || (mine ? "Вы" : "Поддержка")}</span>
                  <span className="text-ink-faint">{formatAbsolute(m.created_at)}</span>
                </div>
                <p className="whitespace-pre-wrap text-[13px] leading-snug text-ink">{m.body}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* composer */}
      <form onSubmit={send} className="border-t border-border p-3">
        {closed ? (
          <p className="px-2 py-2 text-center text-[13px] text-ink-faint">
            Обращение {ticket.status === "resolved" ? "решено" : "закрыто"}. Создайте новое, если проблема осталась.
          </p>
        ) : (
          <div className="flex items-end gap-2">
            <textarea
              value={reply}
              onChange={(e) => setReply(e.target.value)}
              onKeyDown={(e) => {
                if ((e.metaKey || e.ctrlKey) && e.key === "Enter") send(e);
              }}
              rows={2}
              aria-label="Ответ в обращении"
              placeholder="Напишите ответ…"
              className="flex-1 resize-y rounded-md border border-border bg-bg px-3 py-2 text-[13px] text-ink
                         placeholder:text-ink-faint focus:border-lime focus:outline-none focus:ring-2 focus:ring-lime/20"
            />
            <button type="submit" disabled={!reply.trim() || busy} className="btn btn-primary disabled:opacity-50">
              {busy ? "…" : "Отправить"}
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
