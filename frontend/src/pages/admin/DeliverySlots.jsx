import { useState } from "react";
import { api } from "../../api";

export default function DeliverySlots() {
  // Slot config
  const [configForm, setConfigForm] = useState({
    restaurant_id: "",
    slot_duration_minutes: 60,
    slot_capacity: 3,
  });
  const [configMsg, setConfigMsg] = useState("");
  const [configErr, setConfigErr] = useState("");
  const [savingConfig, setSavingConfig] = useState(false);

  // Blackout
  const [blackoutForm, setBlackoutForm] = useState({
    restaurant_id: "",
    start_time: "",
    end_time: "",
    reason: "",
  });
  const [blackoutMsg, setBlackoutMsg] = useState("");
  const [blackoutErr, setBlackoutErr] = useState("");
  const [savingBlackout, setSavingBlackout] = useState(false);

  // View blackouts
  const [viewRestId, setViewRestId] = useState("");
  const [blackouts, setBlackouts] = useState([]);
  const [loadingBlackouts, setLoadingBlackouts] = useState(false);

  // View availability
  const [availForm, setAvailForm] = useState({ restaurant_id: "", date: "" });
  const [availability, setAvailability] = useState(null);
  const [loadingAvail, setLoadingAvail] = useState(false);

  async function handleSaveConfig(e) {
    e.preventDefault();
    setConfigErr("");
    setConfigMsg("");
    setSavingConfig(true);
    try {
      const data = await api.put(
        `/admin/restaurants/${configForm.restaurant_id}/delivery-slot-config`,
        {
          slot_duration_minutes: configForm.slot_duration_minutes,
          slot_capacity: configForm.slot_capacity,
        }
      );
      setConfigMsg(
        `Config saved: ${data.slot_duration_minutes}min slots, capacity ${data.slot_capacity}.`
      );
    } catch (err) {
      setConfigErr(err.message);
    } finally {
      setSavingConfig(false);
    }
  }

  async function handleCreateBlackout(e) {
    e.preventDefault();
    setBlackoutErr("");
    setBlackoutMsg("");
    setSavingBlackout(true);
    try {
      await api.post(
        `/admin/restaurants/${blackoutForm.restaurant_id}/delivery-blackouts`,
        {
          start_time: blackoutForm.start_time,
          end_time: blackoutForm.end_time,
          reason: blackoutForm.reason || null,
        }
      );
      setBlackoutMsg("Blackout period created.");
      setBlackoutForm({ ...blackoutForm, start_time: "", end_time: "", reason: "" });
    } catch (err) {
      setBlackoutErr(err.message);
    } finally {
      setSavingBlackout(false);
    }
  }

  async function handleViewBlackouts() {
    if (!viewRestId) return;
    setLoadingBlackouts(true);
    try {
      const data = await api.get(
        `/admin/restaurants/${viewRestId}/delivery-blackouts`
      );
      setBlackouts(data);
    } catch {
      setBlackouts([]);
    } finally {
      setLoadingBlackouts(false);
    }
  }

  async function handleCheckAvailability() {
    if (!availForm.restaurant_id) return;
    setLoadingAvail(true);
    try {
      const dateParam = availForm.date ? `&date=${availForm.date}` : "";
      const data = await api.get(
        `/restaurants/${availForm.restaurant_id}/delivery-slots/availability?${dateParam}`
      );
      setAvailability(data);
    } catch {
      setAvailability(null);
    } finally {
      setLoadingAvail(false);
    }
  }

  const inputCls =
    "w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500";

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold tracking-tight">Delivery Slots</h1>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Slot config */}
        <div className="rounded-xl border border-zinc-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold">Slot Configuration</h2>

          {configMsg && (
            <div className="mb-3 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
              {configMsg}
            </div>
          )}
          {configErr && (
            <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {configErr}
            </div>
          )}

          <form onSubmit={handleSaveConfig} className="space-y-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Restaurant ID
              </label>
              <input
                required
                type="number"
                min="1"
                value={configForm.restaurant_id}
                onChange={(e) =>
                  setConfigForm({ ...configForm, restaurant_id: e.target.value })
                }
                className={inputCls}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-sm font-medium text-zinc-700">
                  Duration (min)
                </label>
                <input
                  required
                  type="number"
                  min="15"
                  value={configForm.slot_duration_minutes}
                  onChange={(e) =>
                    setConfigForm({
                      ...configForm,
                      slot_duration_minutes: Number(e.target.value),
                    })
                  }
                  className={inputCls}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-zinc-700">
                  Capacity
                </label>
                <input
                  required
                  type="number"
                  min="1"
                  value={configForm.slot_capacity}
                  onChange={(e) =>
                    setConfigForm({
                      ...configForm,
                      slot_capacity: Number(e.target.value),
                    })
                  }
                  className={inputCls}
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={savingConfig}
              className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              {savingConfig ? "Saving..." : "Save configuration"}
            </button>
          </form>
        </div>

        {/* Create blackout */}
        <div className="rounded-xl border border-zinc-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold">Create Blackout Period</h2>

          {blackoutMsg && (
            <div className="mb-3 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
              {blackoutMsg}
            </div>
          )}
          {blackoutErr && (
            <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {blackoutErr}
            </div>
          )}

          <form onSubmit={handleCreateBlackout} className="space-y-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Restaurant ID
              </label>
              <input
                required
                type="number"
                min="1"
                value={blackoutForm.restaurant_id}
                onChange={(e) =>
                  setBlackoutForm({
                    ...blackoutForm,
                    restaurant_id: e.target.value,
                  })
                }
                className={inputCls}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Start Time (ISO)
              </label>
              <input
                required
                type="datetime-local"
                value={blackoutForm.start_time}
                onChange={(e) =>
                  setBlackoutForm({
                    ...blackoutForm,
                    start_time: e.target.value,
                  })
                }
                className={inputCls}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                End Time (ISO)
              </label>
              <input
                required
                type="datetime-local"
                value={blackoutForm.end_time}
                onChange={(e) =>
                  setBlackoutForm({
                    ...blackoutForm,
                    end_time: e.target.value,
                  })
                }
                className={inputCls}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Reason (optional)
              </label>
              <input
                value={blackoutForm.reason}
                onChange={(e) =>
                  setBlackoutForm({ ...blackoutForm, reason: e.target.value })
                }
                className={inputCls}
                placeholder="Holiday closure"
              />
            </div>
            <button
              type="submit"
              disabled={savingBlackout}
              className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              {savingBlackout ? "Creating..." : "Create blackout"}
            </button>
          </form>
        </div>

        {/* View blackouts */}
        <div className="rounded-xl border border-zinc-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold">View Blackouts</h2>
          <div className="flex gap-2">
            <input
              type="number"
              min="1"
              value={viewRestId}
              onChange={(e) => setViewRestId(e.target.value)}
              placeholder="Restaurant ID"
              className={inputCls}
            />
            <button
              onClick={handleViewBlackouts}
              disabled={loadingBlackouts}
              className="shrink-0 rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
            >
              {loadingBlackouts ? "..." : "Load"}
            </button>
          </div>
          {blackouts.length > 0 && (
            <div className="mt-4 space-y-2">
              {blackouts.map((b) => (
                <div
                  key={b.id}
                  className="rounded-lg border border-zinc-100 bg-zinc-50 p-3 text-sm"
                >
                  <p className="font-medium">
                    {new Date(b.start_time).toLocaleString()} &mdash;{" "}
                    {new Date(b.end_time).toLocaleString()}
                  </p>
                  {b.reason && (
                    <p className="mt-1 text-zinc-500">{b.reason}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* View availability */}
        <div className="rounded-xl border border-zinc-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold">Check Availability</h2>
          <div className="flex gap-2">
            <input
              type="number"
              min="1"
              value={availForm.restaurant_id}
              onChange={(e) =>
                setAvailForm({ ...availForm, restaurant_id: e.target.value })
              }
              placeholder="Restaurant ID"
              className={inputCls}
            />
            <input
              type="date"
              value={availForm.date}
              onChange={(e) =>
                setAvailForm({ ...availForm, date: e.target.value })
              }
              className={inputCls}
            />
            <button
              onClick={handleCheckAvailability}
              disabled={loadingAvail}
              className="shrink-0 rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
            >
              {loadingAvail ? "..." : "Check"}
            </button>
          </div>
          {availability && (
            <div className="mt-4">
              <p className="mb-2 text-sm text-zinc-500">
                {availability.restaurant_id} &middot; {availability.date} &middot;{" "}
                Slot duration: {availability.slot_duration_minutes}min
              </p>
              {availability.slots?.length === 0 ? (
                <p className="text-sm text-zinc-400">No available slots.</p>
              ) : (
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                  {availability.slots?.map((s, i) => (
                    <div
                      key={i}
                      className={`rounded-lg border p-2 text-center text-xs ${
                        s.available
                          ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                          : "border-zinc-100 bg-zinc-50 text-zinc-400"
                      }`}
                    >
                      <p className="font-medium">
                        {s.slot_start?.slice(11, 16)} &mdash;{" "}
                        {s.slot_end?.slice(11, 16)}
                      </p>
                      <p className="mt-0.5">
                        {s.available
                          ? `${s.remaining_capacity} left`
                          : "Full"}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
