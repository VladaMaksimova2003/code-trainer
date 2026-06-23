// src/pages/TaskPages/student/SubmissionCommentsTab.jsx
// Содержимое вкладки «Комментарии» в StudentBottomPanel.
// - Student: read-only список
// - Teacher review: список + composer + edit/delete своих
import { useEffect, useState, useCallback } from "react";
import {
  listStudentComments,
  listTeacherComments,
  deleteComment,
} from "../../../features/analytics/api/submissionCommentsApi";
import { formatAbsolute } from "../../../shared/lib/relativeTime";
import TeacherCommentComposer from "../../../features/solve-task/components/TeacherCommentComposer";

export default function SubmissionCommentsTab({
  submissionId,
  isTeacherReview = false,
  currentTeacherId = null,
  onCountChange,
}) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [menuId, setMenuId] = useState(null);

  const load = useCallback(async () => {
    if (!submissionId) {
      setComments([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = isTeacherReview
        ? await listTeacherComments(submissionId)
        : await listStudentComments(submissionId);
      setComments(data);
      onCountChange?.(data.length);
    } catch (e) {
      setError("Не удалось загрузить комментарии");
    } finally {
      setLoading(false);
    }
  }, [submissionId, isTeacherReview, onCountChange]);

  useEffect(() => {
    load();
  }, [load]);

  const handleCreated = (item) => {
    setComments((prev) => {
      const next = [...prev, item];
      onCountChange?.(next.length);
      return next;
    });
  };
  const handleUpdated = (item) => {
    setComments((prev) => prev.map((c) => (c.id === item.id ? item : c)));
    setEditingId(null);
  };
  const handleDelete = async (id) => {
    setMenuId(null);
    try {
      await deleteComment(submissionId, id);
      setComments((prev) => {
        const next = prev.filter((c) => c.id !== id);
        onCountChange?.(next.length);
        return next;
      });
    } catch {
      setError("Не удалось удалить комментарий");
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2.5">
        {loading && <p className="text-[13px] text-ink-faint">Загрузка…</p>}
        {error && <p className="text-[13px] text-danger">{error}</p>}

        {!loading && !error && comments.length === 0 && (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <div className="mb-3 grid h-12 w-12 place-items-center rounded-xl border border-border bg-surface-2 text-ink-faint">
              💬
            </div>
            <p className="text-[13px] text-ink-muted">
              {isTeacherReview
                ? "Пока нет комментариев. Оставьте первый ниже."
                : "Преподаватель ещё не оставил комментариев к этому решению."}
            </p>
          </div>
        )}

        {comments.map((c) => {
          const own = isTeacherReview && currentTeacherId != null && c.teacher_id === currentTeacherId;
          const edited = c.updated_at && c.updated_at !== c.created_at;
          if (editingId === c.id) {
            return (
              <TeacherCommentComposer
                key={c.id}
                submissionId={submissionId}
                editing={c}
                onUpdated={handleUpdated}
                onCancel={() => setEditingId(null)}
              />
            );
          }
          return (
            <div
              key={c.id}
              className="relative rounded-lg border border-border bg-surface-2 px-3.5 py-2.5"
            >
              <div className="mb-1 flex items-center justify-between gap-2">
                <span className="text-[13px] font-semibold text-ink">
                  {c.teacher_name}
                  <span className="ml-2 font-normal text-ink-faint">
                    {formatAbsolute(c.created_at)}
                    {edited && " · изменён"}
                  </span>
                </span>
                {own && (
                  <div className="relative">
                    <button
                      type="button"
                      aria-label="Действия с комментарием"
                      onClick={() => setMenuId(menuId === c.id ? null : c.id)}
                      className="icon-btn h-7 w-7 text-ink-faint hover:text-ink"
                    >
                      ⋯
                    </button>
                    {menuId === c.id && (
                      <div className="absolute right-0 top-8 z-10 w-32 rounded-lg border border-border bg-surface p-1 shadow-lg">
                        <button
                          type="button"
                          className="block w-full rounded px-3 py-1.5 text-left text-[13px] text-ink hover:bg-surface-2"
                          onClick={() => {
                            setEditingId(c.id);
                            setMenuId(null);
                          }}
                        >
                          Редактировать
                        </button>
                        <button
                          type="button"
                          className="block w-full rounded px-3 py-1.5 text-left text-[13px] text-danger hover:bg-surface-2"
                          onClick={() => handleDelete(c.id)}
                        >
                          Удалить
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <p className="whitespace-pre-wrap text-[13px] leading-snug text-ink-muted">{c.body}</p>
            </div>
          );
        })}
      </div>

      {isTeacherReview && !editingId && (
        <div className="shrink-0 border-t border-border p-3">
          <TeacherCommentComposer submissionId={submissionId} onCreated={handleCreated} />
        </div>
      )}
    </div>
  );
}
