// handoff/curriculum/LoadingPage.tsx
// Минималистичная страница загрузки (Toxic Pulse). Один элемент: спиннер + общая подпись.
import { Spinner } from "./components/LoadingBlock";

interface LoadingPageProps {
  text?: string;
  /** true — занимать весь экран; false — высоту контейнера. */
  fullscreen?: boolean;
}

export default function LoadingPage({ text = "Загрузка…", fullscreen = true }: LoadingPageProps) {
  return (
    <div
      className={
        (fullscreen ? "min-h-screen " : "min-h-[60vh] ") +
        "grid place-items-center bg-bg px-6 text-center"
      }
    >
      <div className="flex flex-col items-center gap-4">
        <Spinner size={36} />
        <span className="text-[14px] text-ink-muted">{text}</span>
      </div>
    </div>
  );
}
