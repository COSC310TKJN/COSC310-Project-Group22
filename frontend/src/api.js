const BASE = "/api";

function getUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

function headers(extra = {}) {
  const h = { "Content-Type": "application/json", ...extra };
  const user = getUser();
  if (user) h["X-User-Id"] = String(user.id);
  return h;
}

async function request(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: headers(opts.headers),
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body }),
  put: (path, body) => request(path, { method: "PUT", body }),
  patch: (path, body) => request(path, { method: "PATCH", body }),
  delete: (path) => request(path, { method: "DELETE" }),

  // Special version for delivery status updates that needs X-Role header
  patchWithRole: (path, body, role) =>
    request(path, {
      method: "PATCH",
      body,
      headers: { "X-Role": role },
    }),
};
