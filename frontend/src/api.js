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

function emitAuthExpired() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("auth:expired"));
  }
}

function formatApiError(err) {
  const d = err?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d))
    return d.map((e) => e?.msg || JSON.stringify(e)).join("; ") || "Request failed";
  if (d && typeof d === "object") return JSON.stringify(d);
  return err?.message || "Request failed";
}

async function request(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: headers(opts.headers),
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    if (res.status === 401) {
      emitAuthExpired();
    }
    throw new Error(formatApiError(err));
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

  auth: {
    register: (payload) => request("/auth/register", { method: "POST", body: payload }),
    login: (payload) => request("/auth/login", { method: "POST", body: payload }),
    logout: () => request("/auth/logout", { method: "POST" }),
    portalUser: () => request("/portal/user"),
    portalManager: () => request("/portal/manager"),
  },

  restaurants: {
    list: ({ page = 1, pageSize = 20, cuisine } = {}) =>
      request(
        `/restaurants?page=${page}&page_size=${pageSize}${
          cuisine ? `&cuisine=${encodeURIComponent(cuisine)}` : ""
        }`
      ),
    search: ({ q, page = 1, pageSize = 20, cuisine } = {}) =>
      request(
        `/restaurants/search?q=${encodeURIComponent(q || "")}&page=${page}&page_size=${pageSize}${
          cuisine ? `&cuisine=${encodeURIComponent(cuisine)}` : ""
        }`
      ),
    detail: (restaurantId) => request(`/restaurants/${restaurantId}`),
    menu: (restaurantId) => request(`/restaurants/${restaurantId}/menu`),
    create: (payload) => request("/restaurants", { method: "POST", body: payload }),
    createMenuItem: (payload) => request("/menu-items", { method: "POST", body: payload }),
  },

  deliverySlots: {
    availability: (restaurantId, { date } = {}) =>
      request(
        `/restaurants/${restaurantId}/delivery-slots/availability${
          date ? `?date=${encodeURIComponent(date)}` : ""
        }`
      ),
    select: (orderId, slotStart) =>
      request(`/orders/${orderId}/delivery-slot`, {
        method: "POST",
        body: { slot_start: slotStart },
      }),
    updateConfig: (restaurantId, payload) =>
      request(`/admin/restaurants/${restaurantId}/delivery-slot-config`, {
        method: "PUT",
        body: payload,
      }),
    createBlackout: (restaurantId, payload) =>
      request(`/admin/restaurants/${restaurantId}/delivery-blackouts`, {
        method: "POST",
        body: payload,
      }),
    listBlackouts: (restaurantId, { date } = {}) =>
      request(
        `/admin/restaurants/${restaurantId}/delivery-blackouts${
          date ? `?date=${encodeURIComponent(date)}` : ""
        }`
      ),
  },

  orders: {
    create: (payload) => request("/orders", { method: "POST", body: payload }),
    get: (orderId) => request(`/orders/${orderId}`),
    total: (orderId) => request(`/orders/${orderId}/total`),
    cancel: (orderId) => request(`/orders/${orderId}/cancel`, { method: "POST" }),
    history: (customerId) => request(`/orders/history/${customerId}`),
    createReorderDraft: (orderId, customerId) =>
      request(`/orders/${orderId}/reorder`, {
        method: "POST",
        body: { customer_id: customerId },
      }),
    updateReorderDraft: (draftId, payload) =>
      request(`/orders/reorder/${draftId}`, { method: "PATCH", body: payload }),
    confirmReorder: (draftId) =>
      request(`/orders/reorder/${draftId}/confirm`, { method: "POST" }),
  },
};
