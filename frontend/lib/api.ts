const API_BASE_URL = "http://127.0.0.1:8000";

export async function fetchQuestions(params = {}) {
  const query = new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)])).toString();
  const res = await fetch(`${API_BASE_URL}/questions${query ? "?" + query : ""}`);
  if (!res.ok) throw new Error("Failed to fetch questions");
  return res.json();
}

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function fetchQuiz(limit = 20, topic = null) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (topic) params.append("topic", topic);
  const res = await fetch(`${API_BASE_URL}/quiz?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch quiz");
  return res.json();
}
