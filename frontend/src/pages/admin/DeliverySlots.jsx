import { useEffect, useMemo, useState } from "react";
import { api } from "../../api";

function localDateInputValue(value = new Date()) {
  const date = new Date(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatDateTimeLocal(value) {
  if (!value) return "";
  const date = new Date(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function formatSlotLabel(slot) {
  return `${new Date(slot.slot_start).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  })} - ${new Date(slot.slot_end).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  })}`;
}

export default function DeliverySlots() {
  const [restaurants, setRestaurants] = useState([]);
  const [loadingRestaurants, setLoadingRestaurants] = useState(true);

  const [selectedRestaurantId, setSelectedRestaurantId] = useState("");

  const [configForm, setConfigForm] = useState({
    restaurant_id: "",
    slot_duration_minutes: 60,
    slot_capacity: 3,
  });
  const [configMsg, setConfigMsg] = useState("");
  const [configErr, setConfigErr] = useState("");
  const [savingConfig, setSavingConfig] = useState(false);

  const [blackoutForm, setBlackoutForm] = useState({
    restaurant_id: "",
    start_time: "",
    end_time: "",
    reason: "",
  });
  const [blackoutMsg, setBlackoutMsg] = useState("");
  const [blackoutErr, setBlackoutErr] = useState("");
  const [savingBlackout, setSavingBlackout] = useState(false);

  const [viewDate, setViewDate] = useState(localDateInputValue());
  const [blackouts, setBlackouts] = useState([]);
  const [loadingBlackouts, setLoadingBlackouts] = useState(false);

  const [availability, setAvailability] = useState(null);
  const [loadingAvail, setLoadingAvail] = useState(false);

  const selectedRestaurant = useMemo(
    () => restaurants.find((restaurant) => String(restaurant.id) === String(selectedRestaurantId)) || null,
    [restaurants, selectedRestaurantId]
  );

  useEffect(() => {
    setLoadingRestaurants(true);
    api.restaurants
      .list({ page: 1, pageSize: 100 })
      .then((data) => {
        setRestaurants(data.items || []);
        if (data.items?.length) {
          const firstId = String(data.items[0].id);
          setSelectedRestaurantId(firstId);
          setConfigForm((current) => ({ ...current, restaurant_id: firstId }));
          setBlackoutForm((current) => ({ ...current, restaurant_id: firstId }));
        }
      })
      .catch(() => setRestaurants([]))
      .finally(() => setLoadingRestaurants(false));
  }, []);

  useEffect(() => {
    if (!selectedRestaurantId) return;
    setConfigForm((current) => ({ ...current, restaurant_id: selectedRestaurantId }));
    setBlackoutForm((current) => ({ ...current, restaurant_id: selectedRestaurantId }));
  }, [selectedRestaurantId]);

  useEffect(() => {
    if (!selectedRestaurantId) return;
    handleCheckAvailability(selectedRestaurantId, viewDate);
    handleViewBlackouts(selectedRestaurantId, viewDate);
  }, [selectedRestaurantId, viewDate]);

  async function handleSaveConfig(event) {
    event.preventDefault();
    setConfigErr("");
    setConfigMsg("");
    setSavingConfig(true);
    try {
      const data = await api.deliverySlots.updateConfig(configForm.restaurant_id, {
        slot_duration_minutes: configForm.slot_duration_minutes,
        slot_capacity: configForm.slot_capacity,
      });
      setConfigMsg(`Saved ${data.slot_duration_minutes} minute slots with capacity ${data.slot_capacity}.`);
      handleCheckAvailability(String(data.restaurant_id), viewDate);
    } catch (err) {
      setConfigErr(err.message);
    } finally {
      setSavingConfig(false);
    }
  }

  async function handleCreateBlackout(event) {
    event.preventDefault();
    setBlackoutErr("");
    setBlackoutMsg("");
    setSavingBlackout(true);
    try {
      await api.deliverySlots.createBlackout(blackoutForm.restaurant_id, {
        start_time: new Date(blackoutForm.start_time).toISOString(),
        end_time: new Date(blackoutForm.end_time).toISOString(),
        reason: blackoutForm.reason || null,
      });
      setBlackoutMsg("Blackout period created.");
      setBlackoutForm((current) => ({
        ...current,
        start_time: "",
        end_time: "",
        reason: "",
      }));
      handleViewBlackouts(blackoutForm.restaurant_id, viewDate);
      handleCheckAvailability(blackoutForm.restaurant_id, viewDate);
    } catch (err) {
      setBlackoutErr(err.message);
    } finally {
      setSavingBlackout(false);
    }
  }

  async function handleViewBlackouts(restaurantId = selectedRestaurantId, date = viewDate) {
    if (!restaurantId) return;
    setLoadingBlackouts(true);
    try {
      const data = await api.deliverySlots.listBlackouts(restaurantId, { date });
      setBlackouts(data);
    } catch {
      setBlackouts([]);
    } finally {
      setLoadingBlackouts(false);
    }
  }

  async function handleCheckAvailability(restaurantId = selectedRestaurantId, date = viewDate) {
    if (!restaurantId) return;
    setLoadingAvail(true);
    try {
      const data = await api.deliverySlots.availability(restaurantId, { date });
      setAvailability(data);
      setConfigForm((current) => ({
        ...current,
        restaurant_id: String(data.restaurant_id),
        slot_duration_minutes: data.slot_duration_minutes,
        slot_capacity: data.slot_capacity,
      }));
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
      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Delivery Slots</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Manage courier capacity, blackout periods, and customer-facing time windows.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-[minmax(220px,1fr)_auto]">
          <select
            value={selectedRestaurantId}
            onChange={(event) => setSelectedRestaurantId(event.target.value)}
            disabled={loadingRestaurants || restaurants.length === 0}
            className={inputCls}
          >
            {restaurants.map((restaurant) => (
              <option key={restaurant.id} value={restaurant.id}>
                {restaurant.name} ({restaurant.cuisine_type})
              </option>
            ))}
          </select>
          <input
            type="date"
            value={viewDate}
            min={localDateInputValue()}
            onChange={(event) => setViewDate(event.target.value)}
            className={inputCls}
          />
        </div>
      </div>

      {selectedRestaurant && (
        <div className="mb-8 rounded-2xl border border-zinc-200 bg-[linear-gradient(135deg,#f5fff8_0%,#ffffff_55%,#f7fbff_100%)] p-5 shadow-sm">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-600">
                Restaurant #{selectedRestaurant.id}
              </p>
              <h2 className="mt-2 text-xl font-semibold text-zinc-950">{selectedRestaurant.name}</h2>
              <p className="mt-1 text-sm text-zinc-500">
                {selectedRestaurant.cuisine_type}
                {selectedRestaurant.address ? ` · ${selectedRestaurant.address}` : ""}
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-xl bg-white px-4 py-3 shadow-sm ring-1 ring-zinc-100">
                <p className="text-xs uppercase tracking-wide text-zinc-400">Current slot size</p>
                <p className="mt-1 text-lg font-semibold text-zinc-900">
                  {availability?.slot_duration_minutes || configForm.slot_duration_minutes} min
                </p>
              </div>
              <div className="rounded-xl bg-white px-4 py-3 shadow-sm ring-1 ring-zinc-100">
                <p className="text-xs uppercase tracking-wide text-zinc-400">Capacity per slot</p>
                <p className="mt-1 text-lg font-semibold text-zinc-900">
                  {availability?.slot_capacity || configForm.slot_capacity}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-8 xl:grid-cols-[360px_minmax(0,1fr)]">
        <div className="space-y-8">
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
                <label className="mb-1 block text-sm font-medium text-zinc-700">Restaurant ID</label>
                <input disabled value={configForm.restaurant_id} className={`${inputCls} bg-zinc-50 text-zinc-500`} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-zinc-700">Duration (min)</label>
                  <input
                    required
                    type="number"
                    min="15"
                    value={configForm.slot_duration_minutes}
                    onChange={(event) =>
                      setConfigForm({
                        ...configForm,
                        slot_duration_minutes: Number(event.target.value),
                      })
                    }
                    className={inputCls}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-zinc-700">Capacity</label>
                  <input
                    required
                    type="number"
                    min="1"
                    value={configForm.slot_capacity}
                    onChange={(event) =>
                      setConfigForm({
                        ...configForm,
                        slot_capacity: Number(event.target.value),
                      })
                    }
                    className={inputCls}
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={savingConfig || !configForm.restaurant_id}
                className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                {savingConfig ? "Saving..." : "Save configuration"}
              </button>
            </form>
          </div>

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
                <label className="mb-1 block text-sm font-medium text-zinc-700">Restaurant ID</label>
                <input
                  disabled
                  value={blackoutForm.restaurant_id}
                  className={`${inputCls} bg-zinc-50 text-zinc-500`}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-zinc-700">Start Time</label>
                <input
                  required
                  type="datetime-local"
                  value={blackoutForm.start_time}
                  onChange={(event) =>
                    setBlackoutForm({
                      ...blackoutForm,
                      start_time: event.target.value,
                    })
                  }
                  className={inputCls}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-zinc-700">End Time</label>
                <input
                  required
                  type="datetime-local"
                  value={blackoutForm.end_time}
                  onChange={(event) =>
                    setBlackoutForm({
                      ...blackoutForm,
                      end_time: event.target.value,
                    })
                  }
                  className={inputCls}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-zinc-700">Reason (optional)</label>
                <input
                  value={blackoutForm.reason}
                  onChange={(event) =>
                    setBlackoutForm({ ...blackoutForm, reason: event.target.value })
                  }
                  className={inputCls}
                  placeholder="Holiday closure"
                />
              </div>
              <button
                type="submit"
                disabled={savingBlackout || !blackoutForm.restaurant_id}
                className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                {savingBlackout ? "Creating..." : "Create blackout"}
              </button>
            </form>
          </div>
        </div>

        <div className="space-y-8">
          <div className="rounded-xl border border-zinc-200 bg-white p-6">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Availability Preview</h2>
                <p className="text-sm text-zinc-500">This mirrors what customers can book on the restaurant page.</p>
              </div>
              <button
                type="button"
                onClick={() => handleCheckAvailability()}
                disabled={loadingAvail || !selectedRestaurantId}
                className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
              >
                {loadingAvail ? "Refreshing..." : "Refresh"}
              </button>
            </div>

            {availability && (
              <p className="mb-4 text-sm text-zinc-500">
                {availability.date} · {availability.slot_duration_minutes} minute windows · capacity{" "}
                {availability.slot_capacity}
              </p>
            )}

            {loadingAvail ? (
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div key={index} className="h-20 animate-pulse rounded-xl bg-zinc-100" />
                ))}
              </div>
            ) : availability?.slots?.length ? (
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {availability.slots.map((slot) => (
                  <div
                    key={slot.slot_start}
                    className={`rounded-xl border p-3 ${
                      slot.is_available
                        ? "border-emerald-200 bg-emerald-50"
                        : "border-zinc-100 bg-zinc-50"
                    }`}
                  >
                    <p className="text-sm font-semibold text-zinc-900">{formatSlotLabel(slot)}</p>
                    <p className="mt-1 text-xs text-zinc-500">
                      {slot.is_available
                        ? `${slot.remaining_capacity} spot${slot.remaining_capacity !== 1 ? "s" : ""} left`
                        : slot.disabled_reason === "blackout"
                          ? "Blocked by blackout"
                          : "Fully booked"}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="rounded-xl border border-dashed border-zinc-200 px-4 py-8 text-center text-sm text-zinc-400">
                No slots available for the selected day.
              </p>
            )}
          </div>

          <div className="rounded-xl border border-zinc-200 bg-white p-6">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Blackouts</h2>
                <p className="text-sm text-zinc-500">Current closures affecting the selected date.</p>
              </div>
              <button
                type="button"
                onClick={() => handleViewBlackouts()}
                disabled={loadingBlackouts || !selectedRestaurantId}
                className="rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 disabled:opacity-50"
              >
                {loadingBlackouts ? "Refreshing..." : "Refresh"}
              </button>
            </div>

            {loadingBlackouts ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, index) => (
                  <div key={index} className="h-16 animate-pulse rounded-xl bg-zinc-100" />
                ))}
              </div>
            ) : blackouts.length > 0 ? (
              <div className="space-y-3">
                {blackouts.map((blackout) => (
                  <div key={blackout.id} className="rounded-xl border border-zinc-100 bg-zinc-50 p-4">
                    <p className="text-sm font-semibold text-zinc-900">
                      {formatDateTimeLocal(blackout.start_time).replace("T", " ")} to{" "}
                      {formatDateTimeLocal(blackout.end_time).replace("T", " ")}
                    </p>
                    <p className="mt-1 text-sm text-zinc-500">{blackout.reason || "No reason provided."}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="rounded-xl border border-dashed border-zinc-200 px-4 py-8 text-center text-sm text-zinc-400">
                No blackout periods on this date.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
