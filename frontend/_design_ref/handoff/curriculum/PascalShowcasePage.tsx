// handoff/curriculum/PascalShowcasePage.tsx
// Страница сборника (/learn/pascal/:chapterSlug). Обёрнута в LearningAppShell снаружи.
import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import type {
  ShowcaseResponse,
  ShowcaseNextResponse,
  ShowcaseSection,
  CurriculumNavState,
} from "./types";
import { getShowcase, getShowcaseNext, sectionsOf } from "./api/curriculumApi";
import CurriculumStates from "./components/CurriculumStates";
import SubtopicSection from "./components/SubtopicSection";
import ProgressBar from "./components/ProgressBar";
import Badge from "./components/Badge";

const LANGUAGE = "pascal";
const HUB_PATH = "/learn/pascal";

interface Props {
  /** Если используете useParams — можно не передавать. */
  chapterSlug?: string;
  /** true, если пользователь не авторизован (нет прогресса). */
  isGuest?: boolean;
}

export default function PascalShowcasePage({ chapterSlug: slugProp, isGuest = false }: Props) {
  const navigate = useNavigate();
  const params = useParams<{ chapterSlug: string }>();
  const slug = slugProp ?? params.chapterSlug ?? "";
  const returnTo = `${HUB_PATH}/${slug}`;

  const [data, setData] = useState<ShowcaseResponse | null>(null);
  const [next, setNext] = useState<ShowcaseNextResponse | null>(null);
  const [sections, setSections] = useState<ShowcaseSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [showcase, nextData] = await Promise.all([
        getShowcase(LANGUAGE, slug),
        getShowcaseNext(LANGUAGE, slug).catch(() => null),
      ]);
      setData(showcase);
      setSections(sectionsOf(showcase));
      setNext(nextData);
    } catch {
      setError("Не удалось загрузить сборник. Попробуйте обновить страницу.");
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    void load();
  }, [load]);

  const openTask = (taskId: number) => {
    const state: CurriculumNavState = {
      returnTo,
      navigationMode: "curriculum",
      collectionId: data?.collection_id ?? slug,
    };
    navigate(`/tasks/${taskId}`, { state });
  };

  const continueCollection = () => {
    if (!next?.next_task) return;
    openTask(next.next_task.task_id);
  };

  const progress = data?.progress ?? null;
  const hasProgress = !isGuest && !!progress;
  const percent =
    progress && progress.total_tasks
      ? Math.round((progress.passed_tasks / progress.total_tasks) * 100)
      : 0;
  const buttonLabel = next?.button_label ?? "Продолжить сборник";

  return (
    <div className="mx-auto max-w-[960px] px-4 py-7 sm:px-6">
      <CurriculumStates
        loading={loading}
        error={error}
        empty={!loading && !error && !data}
        loadingText="Загрузка сборника…"
        onRetry={load}
      >
        {data && (
          <>
            <button
              type="button"
              className="btn btn-ghost btn-sm mb-3.5"
              onClick={() => navigate(HUB_PATH)}
            >
              ← Все сборники
            </button>

            {/* header */}
            <div className="mb-1 flex flex-wrap items-end justify-between gap-4">
              <div className="min-w-0">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <Badge tone="purple">Сборник «{data.title}»</Badge>
                  <span className="text-[13px] text-ink-faint">{data.total_tasks} задач</span>
                </div>
                <h1 className="m-0 mb-1 text-[26px] font-extrabold tracking-[-0.6px] text-ink">
                  <span className="text-[18px] font-semibold text-ink-faint">Pascal / </span>
                  {data.title}
                </h1>
                <p className="m-0 text-[14px] text-ink-muted">{data.description}</p>
              </div>
              <div className="flex flex-wrap gap-2.5">
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => navigate(HUB_PATH)}>
                  Все сборники
                </button>
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  disabled={!next?.next_task}
                  onClick={continueCollection}
                >
                  ▸ {buttonLabel}
                </button>
              </div>
            </div>

            {/* progress / guest note */}
            {hasProgress ? (
              <div className="my-6 rounded-2xl border border-border bg-surface p-5">
                <div className="mb-3 flex flex-wrap items-center justify-between gap-2.5">
                  <b className="text-[14px] text-ink">Прогресс сборника</b>
                  <span className="font-mono text-[13px] text-ink-faint">
                    {progress!.passed_tasks}/{progress!.total_tasks} · {percent}%
                  </span>
                </div>
                <ProgressBar percent={percent} />
              </div>
            ) : (
              <div className="my-6 rounded-xl border border-purple/30 bg-purple/10 p-4 text-[13.5px] text-[#cbb6ff]">
                <b className="text-ink">Вы не авторизованы. </b>
                Войдите, чтобы отслеживать прогресс по задачам этого сборника.
              </div>
            )}

            {/* sections */}
            <div className="grid gap-[30px]">
              {sections.map((section, i) => (
                <SubtopicSection
                  key={section.id ?? i}
                  section={section}
                  index={i + 1}
                  isGuest={!hasProgress}
                  onOpenTask={openTask}
                />
              ))}
            </div>
          </>
        )}
      </CurriculumStates>
    </div>
  );
}
