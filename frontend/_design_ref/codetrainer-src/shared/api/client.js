// src/shared/api/client.js
// Если в проекте уже есть axios-инстанс — используйте его и удалите этот файл.
import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001",
  withCredentials: true,
});

// Подстановка токена (подгоните под вашу схему хранения)
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default client;
