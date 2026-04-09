import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";

function draftStorageKey(draftId) {
  return `reorder:draft:${draftId}`;
}

export default function ReorderConfirm() {
  const { draftId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [draftOrder, setDraftOrder] = useState(null);
  const [form, setForm] = useState({ order_time: "", delivery_method: "bike" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const sourceOrderId = useMemo(
    () => draftOrder?.source_order_id || location.state?.sourceOrderId,
    [draftOrder, location.state]
  );

  useEffect(() => {
    const fromRoute = location.state?.draftOrder;
    if (fromRoute) {
      setDraftOrder(fromRoute);
      setForm({
        order_time: fromRoute.order_time || "",
        delivery_method: fromRoute.delivery_method || "bike",
      });
      sessionStorage.setItem(draftStorageKey(draftId), JSON.stringify(fromRoute));
      setLoading(false);
      return;
    }

    const raw = sessionStorage.getItem(draftStorageKey(draftId));
    if (!raw) {
      setError(
        "Reorder draft details are unavailable. Start reorder again from the order page."
      );
      setLoading(false);
      return;
    }
    const parsed = JSON.parse(raw);
    setDraftOrder(parsed);
    setForm({
      order_time: parsed.order_time || "",
      delivery_method: parsed.delivery_method || "bike",
    });
    setLoading(false);
  }, [draftId, location.state]);

  async function handleSaveChanges() {
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const payload = {};
      if (form.order_time) payload.order_time = form.order_time;
      if (form.delivery_method) payload.delivery_method = form.delivery_method;
      const response = await api.orders.updateReorderDraft(draftId, {
        ...payload,
      });
      setDraftOrder(response.order);
      sessionStorage.setItem(draftStorageKey(draftId), JSON.stringify(response.order));
      setMessage("Changes saved.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleConfirm() {
    setConfirming(true);
    setError("");
    setMessage("");
    try {
      const response = await api.orders.confirmReorder(draftId);
      sessionStorage.removeItem(draftStorageKey(draftId));
      navigate(`/orders/${response.order.order_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setConfirming(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-zinc-500">Loading reorder details...</p>;
  }

  return (
    <div className="mx-auto max-w-2xl">
      <button
        onClick={() => navigate("/orders")}
        className="mb-4 text-sm text-zinc-400 hover:text-zinc-600"
      >
        &larr; Back to orders
      </button>

      <h1 className="text-2xl font-bold tracking-tight">Confirm reorder</h1>
      <p className="mt-1 text-sm text-zinc-500">
        Review details, optionally edit delivery settings, then confirm.
      </p>

      {sourceOrderId && (
        <p className="mt-2 text-xs text-emerald-700">Source order: {sourceOrderId}</p>
      )}

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}
      {message && (
        <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
          {message}
        </div>
      )}

      {draftOrder && (
        <div className="mt-6 rounded-xl border border-zinc-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Order preview
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <span className="text-xs text-zinc-400">Item</span>
              <p className="font-medium">{draftOrder.food_item}</p>
            </div>
            <div>
              <span className="text-xs text-zinc-400">Value</span>
              <p className="font-medium">${Number(draftOrder.order_value).toFixed(2)}</p>
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-400">Order time</label>
              <input
                type="datetime-local"
                value={form.order_time ? form.order_time.slice(0, 16) : ""}
                onChange={(e) =>
                  setForm({
                    ...form,
                    order_time: e.target.value ? new Date(e.target.value).toISOString() : "",
                  })
                }
                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-400">Delivery method</label>
              <select
                value={form.delivery_method}
                onChange={(e) => setForm({ ...form, delivery_method: e.target.value })}
                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
              >
                <option value="bike">Bike</option>
                <option value="car">Car</option>
              </select>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleSaveChanges}
              disabled={saving || confirming}
              className="rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Make changes"}
            </button>
            <button
              type="button"
              onClick={handleConfirm}
              disabled={confirming}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              {confirming ? "Confirming..." : "Confirm reorder"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
