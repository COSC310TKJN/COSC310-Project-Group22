import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../api";


function orderIdLookupCandidates(raw) {
  const id = String(raw).trim();
  if (!id) return [];
  const list = [id];
  if (/^\d+$/.test(id)) {
    list.push(`ORD-${id}`);
  }
  return list;
}

export default function AdminOrderEdit() {
  const { orderId: orderIdParam } = useParams();
  const navigate = useNavigate();
  const orderId = orderIdParam ? decodeURIComponent(orderIdParam) : "";

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [canonicalOrderId, setCanonicalOrderId] = useState("");
  const [orderLoaded, setOrderLoaded] = useState(false);
  const [form, setForm] = useState({
    food_item: "",
    order_value: "",
    delivery_method: "bike",
    restaurant_id: "",
    order_time: "",
    coupon_code: "",
  });

  useEffect(() => {
    if (!orderId) return;
    setLoading(true);
    setError("");
    setOrderLoaded(false);
    setCanonicalOrderId("");

    (async () => {
      for (const candidate of orderIdLookupCandidates(orderId)) {
        try {
          const o = await api.get(`/orders/${encodeURIComponent(candidate)}`);
          setCanonicalOrderId(candidate);
          setForm({
            food_item: o.food_item || "",
            order_value: String(o.order_value ?? ""),
            delivery_method: o.delivery_method || "bike",
            restaurant_id: String(o.restaurant_id ?? ""),
            order_time: o.order_time || "",
            coupon_code: o.coupon_code || "",
          });
          setOrderLoaded(true);
          setLoading(false);
          return;
        } catch {
  
        }
      }
      setError("Order not found or failed to load.");
      setLoading(false);
    })();
  }, [orderId]);

  async function handleSave(e) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const rid = form.restaurant_id.trim();
      const body = {
        food_item: form.food_item.trim(),
        order_value: Number(form.order_value),
        delivery_method: form.delivery_method,
        order_time: form.order_time.trim(),
        coupon_code: form.coupon_code.trim() || null,
        restaurant_id: rid === "" ? undefined : Number(rid),
      };
      if (!body.food_item) throw new Error("Food items / description is required.");
      if (!Number.isFinite(body.order_value) || body.order_value < 0) {
        throw new Error("Order value must be a non-negative number.");
      }
      if (body.restaurant_id !== undefined && !Number.isFinite(body.restaurant_id)) {
        throw new Error("Restaurant ID must be a number.");
      }
      const patchId = canonicalOrderId || orderId;
      await api.patch(`/orders/admin/${encodeURIComponent(patchId)}`, body);
      navigate("/admin/orders");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="h-8 w-64 animate-pulse rounded bg-zinc-100" />
        <div className="h-40 animate-pulse rounded-xl bg-zinc-100" />
      </div>
    );
  }

  return (
    <div>
      <Link
        to="/admin/orders"
        className="mb-4 inline-block text-sm text-zinc-400 hover:text-zinc-600"
      >
        &larr; Back to manage orders
      </Link>

      <h1 className="mb-2 text-2xl font-bold tracking-tight">
        Edit order{" "}
        <span className="font-mono text-lg">
          {canonicalOrderId || orderId}
        </span>
      </h1>
      <p className="mb-6 text-sm text-zinc-500">
        Managers can correct line items, totals, and delivery details after an order is placed.
        Customers cannot change orders through the app.
      </p>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {orderLoaded && (
      <form
        onSubmit={handleSave}
        className="max-w-xl space-y-4 rounded-xl border border-zinc-200 bg-white p-5"
      >
        <div>
          <label className="mb-1 block text-xs font-medium text-zinc-500">
            Items (summary text)
          </label>
          <textarea
            required
            rows={3}
            value={form.food_item}
            onChange={(e) => setForm({ ...form, food_item: e.target.value })}
            className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-500">
              Order value ($)
            </label>
            <input
              type="number"
              required
              min={0}
              step="0.01"
              value={form.order_value}
              onChange={(e) => setForm({ ...form, order_value: e.target.value })}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm tabular-nums"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-500">
              Restaurant ID
            </label>
            <input
              type="number"
              min={1}
              value={form.restaurant_id}
              onChange={(e) => setForm({ ...form, restaurant_id: e.target.value })}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm tabular-nums"
            />
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-500">
              Delivery method
            </label>
            <select
              value={form.delivery_method}
              onChange={(e) => setForm({ ...form, delivery_method: e.target.value })}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
            >
              <option value="bike">Bike</option>
              <option value="car">Car</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-500">
              Order time (ISO string)
            </label>
            <input
              type="text"
              value={form.order_time}
              onChange={(e) => setForm({ ...form, order_time: e.target.value })}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 font-mono text-xs"
            />
          </div>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-zinc-500">
            Coupon code (leave empty to remove)
          </label>
          <input
            type="text"
            value={form.coupon_code}
            onChange={(e) => setForm({ ...form, coupon_code: e.target.value })}
            className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm uppercase"
          />
        </div>
        <div className="flex gap-2 pt-2">
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800 disabled:opacity-50"
          >
            {saving ? "Saving…" : "Save changes"}
          </button>
          <Link
            to="/admin/orders"
            className="rounded-lg border border-zinc-200 px-4 py-2 text-sm text-zinc-600 hover:bg-zinc-50"
          >
            Cancel
          </Link>
        </div>
      </form>
      )}
    </div>
  );
}
