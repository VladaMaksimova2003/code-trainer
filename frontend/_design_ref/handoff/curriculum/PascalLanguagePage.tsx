// handoff/curriculum/PascalLanguagePage.tsx
// Хаб трека Pascal (/learn/pascal). Обёрнут в LearningAppShell снаружи (роут).
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Collection, LanguageTrack, CurriculumNavState } from "./types";
import { getLanguageTrack } from "./api/curriculumApi";
import CurriculumStates from "./components/CurriculumStates";
import ChapterCard from "./components/ChapterCard";
import ProgressBar from "./components/ProgressBar";
import Badge from "./components/Badge";

const LANGUAGE = "pascal";
const HUB_PATH = "/learn/pascal";

export default function PascalLanguagePage() {
  const navigate = useNavigate();
  const [track, setTrack] = useState<LanguageTrack | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setTrack(await getLanguageTrack(LANGUAGE));
    } catch {
      setError("Не удалось загрузить трек. Попробуйте обновить страницу.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const openChapter = (c: Collection) => navigate(c.route_path);

  const continueChapter = (c: Collection) => {
    if (!c.next_task) return;
    const state: CurriculumNavState = {
      returnTo: HUB_PATH,
      navigationMode: "curriculum",
      collectionId: c.collection_id,
    };
    navigate(`/tasks/${c.next_task.task_id}`, { state });
  };

  const nextChapter = track?.collections.find((c) => !c.completed && c.next_task) ?? null;
  const agg = track?.progress;
  const aggPercent = agg && agg.total_tasks ? Math.round((agg.passed_tasks / agg.total_tasks) * 100) : 0;

  return (
    <div className="mx-auto max-w-[920px] px-4 py-7 sm:px-6">
      <CurriculumStates loading={loading} error={error} loadingText="Загрузка трека…" onRetry={load}>
        {track && (
          <>
            {/* HERO */}
            <div className="relative mb-6 overflow-hidden rounded-[22px] border border-border bg-surface p-7
                            [background-image:radial-gradient(600px_280px_at_0%_0%,rgba(139,83,254,.12),transparent_60%),radial-gradient(520px_300px_at_100%_100%,rgba(142,255,1,.08),transparent_60%)]">
              <div className="flex flex-wrap items-start gap-[18px]">
                <div className="grid h-14 w-14 flex-none place-items-center rounded-2xl border border-purple/35 bg-purple/15 font-mono text-xl font-bold text-[#b89bff]">
                  Pas
                </div>
                <div className="min-w-0 flex-[1_1_280px]">
                  <div className="mb-1.5 flex items-center gap-2.5">
                    <Badge tone="purple">Учебный трек</Badge>
                    {agg && agg.passed_tasks >= agg.total_tasks && <Badge tone="lime">✓ Трек пройден</Badge>}
                  </div>
                  <h1 className="m-0 mb-1.5 text-[30px] font-extrabold tracking-[-0.8px] text-ink">
                    {track.language_label}
                  </h1>
                  <p className="m-0 max-w-[440px] text-[14.5px] text-ink-muted">
                    Линейный путь от первой программы до процедур и рекурсии. Проходите сборники по порядку.
                  </p>
                </div>
                <div className="min-w-[140px] text-right">
                  <div className="text-[34px] font-extrabold tracking-[-0.5px] text-lime">{aggPercent}%</div>
                  <div className="mb-2.5 font-mono text-[12.5px] text-ink-faint">
                    {agg?.passed_tasks}/{agg?.total_tasks} задач
                  </div>
                  <ProgressBar percent={aggPercent} />
                </div>
              </div>

              {nextChapter && (
                <div className="mt-[22px] flex flex-wrap items-center justify-between gap-3.5 border-t border-border pt-5">
                  <div>
                    <div className="mb-0.5 text-[12px] uppercase tracking-[0.06em] text-ink-faint">Продолжить с</div>
                    <b className="text-[15px] text-ink">
                      {nextChapter.order}. {nextChapter.title_ru}
                    </b>
                  </div>
                  <button type="button" className="btn btn-primary" onClick={() => continueChapter(nextChapter)}>
                    ▸ Продолжить обучение
                  </button>
                </div>
              )}
            </div>

            {/* CHAPTERS */}
            <div className="mb-4 flex items-center justify-between">
              <h2 className="m-0 text-[18px] font-bold text-ink">Сборники</h2>
              <span className="text-[13px] text-ink-faint">{track.collections.length} глав</span>
            </div>

            {track.collections.length === 0 ? (
              <div className="rounded-2xl border border-border bg-surface p-12 text-center">
                <div className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-2xl border border-border bg-surface-2 text-2xl text-ink-faint">
                  📚
                </div>
                <p className="mb-1 text-[16px] font-semibold text-ink">Сборников пока нет</p>
                <p className="mx-auto max-w-sm text-[13.5px] text-ink-muted">
                  Материалы появятся здесь, когда преподаватель их добавит.
                </p>
              </div>
            ) : (
              <div className="grid gap-3.5">
                {track.collections.map((c, i) => (
                  <ChapterCard
                    key={c.collection_id}
                    chapter={c}
                    isCurrent={nextChapter?.collection_id === c.collection_id}
                    isLast={i === track.collections.length - 1}
                    onOpen={openChapter}
                    onContinue={continueChapter}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </CurriculumStates>
    </div>
  );
}
