const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Upload a logo file → returns { path, filename }
 */
export async function uploadLogo(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/api/upload/logo`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/**
 * Generate a proposal and trigger browser download of the .pptx
 * type: "demand" | "visual" | "chatbot"
 */
export async function generateProposal(type, payload) {
  const res = await fetch(`${BASE}/api/generate/${type}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  // Stream binary → blob → download
  const blob = await res.blob();
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href     = url;
  a.download = `${type}_proposal.pptx`;
  a.click();
  URL.revokeObjectURL(url);
}
