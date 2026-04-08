import { useEffect, useState } from "react";
import { api } from "../../api";

const STATUS_FLOW = ["created", "paid", "preparing", "out_for_delivery", "delivered"];

export default function ManageOrders() {
  const [paidOrders, setPaidOrders] = useState([]);
  const [failedPayments, setFailedPayments] = useState([]);
  const [tab, setTab] = useState("paid");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updating, setUpdating] = useState(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get("/payments/manager/orders"),
      api.get("/payments/manager/failed-payments"),
    ])
      .then(([paid, failed]) => {
        setPaidOrders(paid);
        setFailedPayments(failed);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function advanceStatus(orderId) {
    setUpdating(orderId);
    setError("");
    try {
      const st = await api.get(`/orders/${orderId}/status`);
      const cur = st.current_status;
      const idx = STATUS_FLOW.indexOf(cur);
      if (idx < 0 || idx >= STATUS_FLOW.length - 1) {
        setError(`Cannot advance from status: ${cur}`);
        return;
      }
      const nextStatus = STATUS_FLOW[idx + 1];
      await api.patchWithRole(
        `/orders/${orderId}/status`,
        { new_status: nextStatus },
        "admin"
      );
      const [paid, failed] = await Promise.all([
        api.get("/payments/manager/orders"),
        api.get("/payments/manager/failed-payments"),
      ]);
      setPaidOrders(paid);
      setFailedPayments(failed);
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdating(null);
    }
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="h-8 w-48 animate-pulse rounded bg-zinc-100" />
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-16 animate-pulse rounded-xl bg-zinc-100" />
        ))}
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Manage Orders</h1>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg bg-zinc-100 p-1 w-fit">
        <button
          onClick={() => setTab("paid")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            tab === "paid" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500"
          }`}
        >
          Paid Orders ({paidOrders.length})
        </button>
        <button
          onClick={() => setTab("failed")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            tab === "failed" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500"
          }`}
        >
          Failed Payments ({failedPayments.length})
        </button>
      </div>

      {tab === "paid" ? (
        paidOrders.length === 0 ? (
          <p className="py-10 text-center text-zinc-400">No paid orders yet.</p>
        ) : (
          <div className="space-y-2">
            {paidOrders.map((o) => (
              <div
                key={o.order_id}
                className="flex items-center justify-between rounded-xl border border-zinc-200 bg-white p-4"
              >
                <div>
                  <p className="font-medium">Order #{o.order_id}</p>
                  <p className="text-sm text-zinc-500">
                    ${Number(o.amount).toFixed(2)} &middot; {o.status}
                  </p>
                </div>
                <button
                  onClick={() => advanceStatus(o.order_id)}
                  disabled={updating === o.order_id}
                  className="rounded-lg bg-zinc-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
                >
                  {updating === o.order_id ? "Updating..." : "Advance status"}
                </button>
              </div>
            ))}
          </div>
        )
      ) : failedPayments.length === 0 ? (
        <p className="py-10 text-center text-zinc-400">No failed payments.</p>
      ) : (
        <div className="space-y-2">
          {failedPayments.map((p) => (
            <div
              key={p.transaction_id}
              className="rounded-xl border border-red-100 bg-white p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Order #{p.order_id}</p>
                  <p className="text-sm text-zinc-500">
                    ${Number(p.amount).toFixed(2)}
                  </p>
                </div>
                <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
                  {p.status}
                </span>
              </div>
              <p className="mt-2 text-xs text-zinc-400">
                Transaction: {p.transaction_id}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
