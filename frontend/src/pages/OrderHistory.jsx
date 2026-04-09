import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

const STATUS_COLORS = {
  created: "bg-blue-100 text-blue-700",
  paid: "bg-indigo-100 text-indigo-700",
  preparing: "bg-amber-100 text-amber-700",
  out_for_delivery: "bg-orange-100 text-orange-700",
  delivered: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-red-100 text-red-700",
  completed: "bg-emerald-100 text-emerald-700",
};

export default function OrderHistory() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get(`/orders/history/${user.id}`)
      .then((data) => setOrders(data.orders || []))
      .catch(() => setOrders([]))
      .finally(() => setLoading(false));
  }, [user]);

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="h-8 w-48 animate-pulse rounded bg-zinc-100" />
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-20 animate-pulse rounded-xl bg-zinc-100" />
        ))}
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Your Orders</h1>

      {orders.length === 0 ? (
        <div className="py-20 text-center">
          <p className="text-lg font-medium text-zinc-400">No orders yet</p>
          <p className="mt-1 text-sm text-zinc-400">
            Browse restaurants to place your first order.
          </p>
          <Link
            to="/"
            className="mt-4 inline-block rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700"
          >
            Browse restaurants
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((o) => (
            <Link
              key={o.order_id}
              to={`/orders/${o.order_id}`}
              className="flex items-center justify-between rounded-xl border border-zinc-200 bg-white p-4 transition-colors hover:border-zinc-300"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="max-w-[60%] break-words font-medium">{o.food_item}</span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${
                      STATUS_COLORS[o.status] || "bg-zinc-100 text-zinc-600"
                    }`}
                  >
                    {o.status?.replace(/_/g, " ")}
                  </span>
                </div>
                <p className="mt-1 text-xs text-zinc-400">
                  Order {o.order_id} &middot; Restaurant #{o.restaurant_id}
                </p>
              </div>
              <div className="text-right">
                <div className="font-semibold tabular-nums">
                  ${Number(o.order_value).toFixed(2)}
                </div>
                <div className="text-xs text-zinc-400">
                  {o.delivery_method} &middot; {o.delivery_distance} km
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
