import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

const TYPE_LABELS = {
  order_placed: "Order Placed",
  status_change: "Status Update",
  order_cancelled: "Cancelled",
  delivery: "Delivery",
  manager_new_order: "New Order (Manager)",
};

export default function Notifications() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [preferences, setPreferences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("inbox");

  useEffect(() => {
    loadData();
  }, [user]);

  function loadData() {
    setLoading(true);
    Promise.all([
      api.get(`/notifications/?user_id=${user.id}`),
      api.get(`/notifications/preferences?user_id=${user.id}`),
    ])
      .then(([notifs, prefs]) => {
        setNotifications(notifs);
        setPreferences(prefs);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  async function markRead(id) {
    try {
      await api.patch(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch {}
  }

  async function togglePref(notificationType, enabled, channel) {
    try {
      const res = await api.put(
        `/notifications/preferences?user_id=${user.id}&notification_type=${notificationType}&enabled=${!enabled}&channel=${channel}`
      );
      setPreferences((prev) =>
        prev.map((p) =>
          p.notification_type === notificationType ? res : p
        )
      );
    } catch {}
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="h-8 w-48 animate-pulse rounded bg-zinc-100" />
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-16 animate-pulse rounded-xl bg-zinc-100" />
        ))}
      </div>
    );
  }

  const unread = notifications.filter((n) => !n.is_read);

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Notifications</h1>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg bg-zinc-100 p-1 w-fit">
        <button
          onClick={() => setTab("inbox")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            tab === "inbox" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500"
          }`}
        >
          Inbox ({notifications.length})
        </button>
        <button
          onClick={() => setTab("preferences")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            tab === "preferences" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500"
          }`}
        >
          Preferences
        </button>
      </div>

      {tab === "inbox" ? (
        notifications.length === 0 ? (
          <div className="py-20 text-center">
            <p className="text-lg font-medium text-zinc-400">No notifications</p>
            <p className="mt-1 text-sm text-zinc-400">
              You'll see order updates and delivery notifications here.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {unread.length > 0 && (
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-zinc-400">
                Unread ({unread.length})
              </p>
            )}
            {notifications.map((n) => (
              <div
                key={n.id}
                className={`rounded-xl border p-4 transition-colors ${
                  n.is_read
                    ? "border-zinc-100 bg-zinc-50"
                    : "border-zinc-200 bg-white"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      {!n.is_read && (
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                      )}
                      <h3 className="text-sm font-semibold">{n.title}</h3>
                    </div>
                    <p className="mt-1 text-sm text-zinc-500">{n.message}</p>
                    <div className="mt-2 flex gap-2 text-[10px] text-zinc-400">
                      <span>
                        {TYPE_LABELS[n.notification_type] || n.notification_type}
                      </span>
                      <span>&middot;</span>
                      <span>{n.channel}</span>
                      {n.created_at && (
                        <>
                          <span>&middot;</span>
                          <span>{new Date(n.created_at).toLocaleString()}</span>
                        </>
                      )}
                    </div>
                  </div>
                  {!n.is_read && (
                    <button
                      onClick={() => markRead(n.id)}
                      className="ml-4 shrink-0 text-xs text-emerald-600 hover:text-emerald-700"
                    >
                      Mark read
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        <div className="space-y-2">
          {preferences.length === 0 ? (
            <p className="py-10 text-center text-sm text-zinc-400">
              No preferences configured yet. They'll appear after you receive notifications.
            </p>
          ) : (
            preferences.map((p) => (
              <div
                key={p.notification_type}
                className="flex items-center justify-between rounded-xl border border-zinc-200 bg-white p-4"
              >
                <div>
                  <p className="text-sm font-medium">
                    {TYPE_LABELS[p.notification_type] || p.notification_type}
                  </p>
                  <p className="text-xs text-zinc-400">Channel: {p.channel}</p>
                </div>
                <button
                  onClick={() =>
                    togglePref(p.notification_type, p.enabled, p.channel)
                  }
                  className={`relative h-6 w-11 rounded-full transition-colors ${
                    p.enabled ? "bg-emerald-600" : "bg-zinc-300"
                  }`}
                >
                  <span
                    className={`absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition-transform shadow-sm ${
                      p.enabled ? "translate-x-5" : ""
                    }`}
                  />
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
