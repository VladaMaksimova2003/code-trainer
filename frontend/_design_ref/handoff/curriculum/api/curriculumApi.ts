// handoff/curriculum/api/curriculumApi.ts
// Слой данных под curriculum. Адаптируйте baseURL/инстанс под ваш http-клиент.
import axios from "axios";
import type {
  CollectionsResponse,
  LanguageTrack,
  ShowcaseResponse,
  ShowcaseNextResponse,
} from "../types";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  withCredentials: true,
});

/** GET /curriculum/collections → конкретный язык. */
export async function getLanguageTrack(language: string): Promise<LanguageTrack | null> {
  const { data } = await http.get<CollectionsResponse>("/curriculum/collections");
  return data.languages.find((l) => l.language === language) ?? null;
}

/** GET /curriculum/{language}/showcase/{slug}/student */
export async function getShowcase(
  language: string,
  slug: string
): Promise<ShowcaseResponse> {
  const { data } = await http.get<ShowcaseResponse>(
    `/curriculum/${language}/showcase/${slug}/student`
  );
  return data;
}

/** GET /curriculum/{language}/showcase/{slug}/next */
export async function getShowcaseNext(
  language: string,
  slug: string
): Promise<ShowcaseNextResponse> {
  const { data } = await http.get<ShowcaseNextResponse>(
    `/curriculum/${language}/showcase/${slug}/next`
  );
  return data;
}

/** Нормализация: API может отдавать subtopics ИЛИ technical_concepts. */
export function sectionsOf(res: ShowcaseResponse) {
  return res.subtopics ?? res.technical_concepts ?? [];
}
