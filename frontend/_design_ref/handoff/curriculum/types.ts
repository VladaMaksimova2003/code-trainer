// handoff/curriculum/types.ts
// Доменные типы для учебного трека (Pascal и др.). Подгоните поля под реальный ответ API.

export type ProgressStatus = "passed" | "failed" | "not_started";

export type ActionType =
  | "translate"
  | "assemble"
  | "implement"
  | "debug"
  | "analyze"
  | "recognize";

export type Difficulty = "Лёгкая" | "Средняя" | "Сложная";

export interface CollectionProgress {
  total_tasks: number;
  passed_tasks: number;
  progress_percent: number;
}

export interface NextTask {
  task_id: number;
  title: string;
  slug?: string;
  progress_status?: ProgressStatus;
}

/** Карточка сборника на хабе языка (/learn/pascal). */
export interface Collection {
  collection_id: string;
  title_ru: string;
  description_ru: string;
  route_path: string; // напр. "/learn/pascal/conditions"
  order: number;
  progress: CollectionProgress;
  completed: boolean;
  button_label: string; // "Начать" | "Продолжить" | "Повторить"
  next_task: NextTask | null;
}

/** Язык целиком (агрегат + список сборников). */
export interface LanguageTrack {
  language: string; // "pascal"
  language_label: string;
  progress: CollectionProgress;
  collections: Collection[];
}

export interface CollectionsResponse {
  languages: LanguageTrack[];
}

/** Задача внутри showcase-сборника. */
export interface ShowcaseTask {
  task_id: number;
  title: string;
  action: ActionType;
  action_label: string; // "Перенести", "Собрать", …
  action_skill_label: string; // "Перенести на Pascal"
  action_description_ru: string;
  difficulty: Difficulty;
  progress_status?: ProgressStatus;
  short_instruction: string;
  subtopic_name_ru: string;
}

/** Секция = технический концепт (TC). */
export interface ShowcaseSection {
  id?: string;
  name_ru: string;
  tasks: ShowcaseTask[];
  progress?: CollectionProgress | null;
}

export interface ShowcaseResponse {
  collection_id: string;
  title: string;
  description: string;
  total_tasks: number;
  progress: CollectionProgress | null; // null для гостя
  subtopics?: ShowcaseSection[];
  technical_concepts?: ShowcaseSection[];
}

export interface ShowcaseNextResponse {
  next_task: NextTask | null;
  button_label: string;
  completed: boolean;
  progress: CollectionProgress | null;
}

/** State, который страница задачи ждёт от curriculum-навигации. */
export interface CurriculumNavState {
  returnTo: string;
  navigationMode: "curriculum";
  collectionId: string;
}
