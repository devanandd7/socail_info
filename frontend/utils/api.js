const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function fetchPosts(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/posts${query ? `?${query}` : ""}`);
  if (!res.ok) throw new Error("Failed to fetch posts");
  return res.json();
}

export async function fetchFiltered(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/filtered${query ? `?${query}` : ""}`);
  if (!res.ok) throw new Error("Failed to fetch filtered posts");
  return res.json();
}

export async function fetchSources() {
  const res = await fetch(`${API_BASE}/sources`);
  if (!res.ok) throw new Error("Failed to fetch sources");
  return res.json();
}

export async function createSource(payload) {
  const res = await fetch(`${API_BASE}/sources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Failed to add source");
  }
  return res.json();
}

export async function updateSource(id, payload) {
  const res = await fetch(`${API_BASE}/sources/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Failed to update source");
  }
  return res.json();
}

export async function deleteSource(id) {
  const res = await fetch(`${API_BASE}/sources/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete source");
  return res.json();
}

export async function fetchHashtags() {
  const res = await fetch(`${API_BASE}/hashtags`);
  if (!res.ok) throw new Error("Failed to fetch hashtags");
  return res.json();
}

export async function createHashtag(payload) {
  const res = await fetch(`${API_BASE}/hashtags`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Failed to add hashtag");
  }
  return res.json();
}

export async function updateHashtag(id, payload) {
  const res = await fetch(`${API_BASE}/hashtags/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Failed to update hashtag");
  }
  return res.json();
}

export async function deleteHashtag(id) {
  const res = await fetch(`${API_BASE}/hashtags/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete hashtag");
  return res.json();
}

export async function fetchTrending(limit = 10) {
  const res = await fetch(`${API_BASE}/trending?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch trending items");
  return res.json();
}

export async function triggerCollect() {
  const res = await fetch(`${API_BASE}/collect`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger collection");
  return res.json();
}
