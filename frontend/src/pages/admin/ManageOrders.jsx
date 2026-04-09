import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";

const STATUS_FLOW = ["created", "paid", "preparing", "out_for_delivery", "delivered"];

function editOrderPath(orderId) {
  return `/admin/order/${encodeURIComponent(String(orderId))}`;
}

export default function ManageOrders() {
  const [paidOrders, setPaidOrders] = useState([]);
  const [failedPayments, setFailedPayments] = useState([]);
  const [allOrders, setAllOrders] = useState([]);
  const [tab, setTab] = useState("paid");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updating, setUpdating] = useState(null);

  function loadPayments() {
    return Promise.all([
      api.get("/payments/manager/orders"),
      api.get("/payments/manager/failed-payments"),
    ]).then(([paid, failed]) => {
      setPaidOrders(paid);
      setFailedPayments(failed);
    });
  }

  function loadAllOrders() {
    return api.get("/orders/admin").then((d) => setAllOrders(d.orders || []));
  }

  useEffect(() => {
    setLoading(true);
    setError("");
    Promise.all([loadPayments(), loadAllOrders()])
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function advanceStatus(orderId) {
    setUpdating(orderId);
    setError("");
    try {
      await api.patch(`/orders/${orderId}/advance`);
      await Promise.all([loadPayments(), loadAllOrders()]);
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

      <div className="mb-6 flex flex-wrap gap-1 rounded-lg bg-zinc-100 p-1">
        <button
          type="button"
          onClick={() => setTab("paid")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            tab === "paid" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500"
          }`}
        >
          Paid ({paidOrders.length})
        </button>
        <button
          type="button"
          onClick={() => setTab("failed")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            tab === "failed" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500"
          }`}
        >
          Failed payments ({failedPayments.length})
        </button>
        <button
          type="button"
          onClick={() => setTab("all")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            tab === "all" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500"
          }`}
        >
          All orders ({allOrders.length})
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
                className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-zinc-200 bg-white p-4"
              >
                <div>
                  <p className="font-medium">Order #{o.order_id}</p>
                  <p className="text-sm text-zinc-500">
                    ${Number(o.amount).toFixed(2)} &middot; {o.status}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Link
                    to={editOrderPath(o.order_id)}
                    className="rounded-lg border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-50"
                  >
                    Edit order
                  </Link>
                  <button
                    type="button"
                    onClick={() => advanceStatus(o.order_id)}
                    disabled={updating === o.order_id}
                    className="rounded-lg bg-zinc-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
                  >
                    {updating === o.order_id ? "Updating..." : "Advance status"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )
      ) : tab === "failed" ? (
        failedPayments.length === 0 ? (
          <p className="py-10 text-center text-zinc-400">No failed payments.</p>
        ) : (
          <div className="space-y-2">
            {failedPayments.map((p) => (
              <div
                key={p.transaction_id}
                className="rounded-xl border border-red-100 bg-white p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="font-medium">Order #{p.order_id}</p>
                    <p className="text-sm text-zinc-500">
                      ${Number(p.amount).toFixed(2)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Link
                      to={editOrderPath(p.order_id)}
                      className="text-xs font-medium text-emerald-700 hover:underline"
                    >
                      Edit order
                    </Link>
                    <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
                      {p.status}
                    </span>
                  </div>
                </div>
                <p className="mt-2 text-xs text-zinc-400">
                  Transaction: {p.transaction_id}
                </p>
              </div>
            ))}
          </div>
        )
      ) : allOrders.length === 0 ? (
        <p className="py-10 text-center text-zinc-400">No orders in the system.</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-zinc-100 bg-zinc-50 text-xs font-semibold uppercase text-zinc-500">
              <tr>
                <th className="px-4 py-3">Order</th>
                <th className="px-4 py-3">Customer</th>
                <th className="px-4 py-3">Items</th>
                <th className="px-4 py-3">Value</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 w-28" />
              </tr>
            </thead>
            <tbody>
              {allOrders.map((o) => (
                <tr key={o.order_id} className="border-b border-zinc-50 last:border-0">
                  <td className="px-4 py-3 font-mono text-xs">{o.order_id}</td>
                  <td className="px-4 py-3">{o.customer_id}</td>
                  <td className="max-w-[220px] truncate px-4 py-3" title={o.food_item}>
                    {o.food_item}
                  </td>
                  <td className="px-4 py-3 tabular-nums">
                    ${Number(o.order_value).toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-xs">{o.status}</td>
                  <td className="px-4 py-3">
                    <Link
                      to={editOrderPath(o.order_id)}
                      className="text-xs font-medium text-emerald-700 hover:underline"
                    >
                      Edit
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
