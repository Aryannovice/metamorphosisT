const API_BASE = "/gateway";

export async function sendPrompt(
  prompt,
  mode = "BALANCED",
  cloudProvider = "GROQ"
) {
  const res = await fetch(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt,
      mode,
      cloud_provider: cloudProvider,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }

  return res.json();
}
