// src/features/analytics/api/submissionCommentsApi.js
// Паттерн как в analyticsApi.js: axios + опциональный mock через VITE_USE_MOCK_API.
import client from "../../../shared/api/client";

const USE_MOCK = import.meta.env.VITE_USE_MOCK_API === "true";

// ---- mock store ----
let _mockComments = [
  {
    id: 1,
    submission_id: 42,
    teacher_id: 5,
    teacher_name: "Петрова А.",
    body: "Хорошее решение, но добавь проверку на пустой ввод.",
    created_at: "2026-06-04T10:00:00Z",
    updated_at: "2026-06-04T10:00:00Z",
  },
  {
    id: 2,
    submission_id: 42,
    teacher_id: 5,
    teacher_name: "Петрова А.",
    body: "Проверь граничный случай n=0 — цикл не обрабатывает пустой ввод.",
    created_at: "2026-06-04T14:32:00Z",
    updated_at: "2026-06-04T14:32:00Z",
  },
];
const delay = (ms = 300) => new Promise((r) => setTimeout(r, ms));

// ---- teacher: список + CRUD ----
export async function listTeacherComments(submissionId) {
  if (USE_MOCK) {
    await delay();
    return _mockComments.filter((c) => c.submission_id === Number(submissionId));
  }
  const { data } = await client.get(`/teacher/submissions/${submissionId}/comments`);
  return data;
}

export async function createComment(submissionId, body) {
  if (USE_MOCK) {
    await delay();
    const item = {
      id: Math.max(0, ..._mockComments.map((c) => c.id)) + 1,
      submission_id: Number(submissionId),
      teacher_id: 5,
      teacher_name: "Вы",
      body,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    _mockComments = [..._mockComments, item];
    return item;
  }
  const { data } = await client.post(`/teacher/submissions/${submissionId}/comments`, { body });
  return data;
}

export async function updateComment(submissionId, commentId, body) {
  if (USE_MOCK) {
    await delay();
    _mockComments = _mockComments.map((c) =>
      c.id === commentId ? { ...c, body, updated_at: new Date().toISOString() } : c
    );
    return _mockComments.find((c) => c.id === commentId);
  }
  const { data } = await client.patch(
    `/teacher/submissions/${submissionId}/comments/${commentId}`,
    { body }
  );
  return data;
}

export async function deleteComment(submissionId, commentId) {
  if (USE_MOCK) {
    await delay();
    _mockComments = _mockComments.filter((c) => c.id !== commentId);
    return { ok: true };
  }
  await client.delete(`/teacher/submissions/${submissionId}/comments/${commentId}`);
  return { ok: true };
}

// ---- student: read-only ----
export async function listStudentComments(submissionId) {
  if (USE_MOCK) {
    await delay();
    return _mockComments.filter((c) => c.submission_id === Number(submissionId));
  }
  const { data } = await client.get(`/student/submissions/${submissionId}/comments`);
  return data;
}
