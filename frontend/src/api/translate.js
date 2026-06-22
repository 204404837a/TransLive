const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export async function translateText({ text, source, target }) {
  const response = await fetch(`${API_BASE}/api/translate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, source, target }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "翻译请求失败");
  }
  return data;
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error("后端服务不可用");
  }
  return response.json();
}
