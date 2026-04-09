import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

const FIXED_DELIVERY_DISTANCE_KM = 5;

function buildFoodItemSummary(lines) {
  return lines.map((line) => `${line.qty}× ${line.name}`).join("; ");
}

function cartKeyForMenuItem(item) {
  if (item == null) return "unknown";
  if (item.id != null && item.id !== "") return String(item.id);
  const name = item.name ?? "item";
  const price = item.estimated_price ?? 0;
  return `${name}:${price}`;
}

function localDateInputValue(value = new Date()) {
  const date = new Date(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatSlotTime(value) {
  return new Date(value).toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  });
}

function slotLabel(slot) {
  return `${formatSlotTime(slot.slot_start)} - ${formatSlotTime(slot.slot_end)}`;
}

function slotReason(slot) {
  if (slot.is_available) return `${slot.remaining_capacity} left`;
  if (slot.disabled_reason === "blackout") return "Unavailable";
  if (slot.disabled_reason === "full") return "Full";
  return "Unavailable";
}

function groupMenuItems(items = []) {
  return items.reduce((groups, item) => {
    const key = item.category?.trim() || "Chef Picks";
    if (!groups[key]) groups[key] = [];
    groups[key].push(item);
    return groups;
  }, {});
}

export default function RestaurantDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [restaurant, setRestaurant] = useState(null);
  const [reviews, setReviews] = useState(null);
  const [reviewList, setReviewList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState({});
  const [slotDate, setSlotDate] = useState(localDateInputValue());
  const [slotAvailability, setSlotAvailability] = useState(null);
  const [selectedSlot, setSelectedSlot] = useState("");
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [slotsError, setSlotsError] = useState("");
  const [orderForm, setOrderForm] = useState({
    delivery_method: "bike",
    coupon_code: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const cartLines = useMemo(() => Object.values(cart).filter((line) => line.qty > 0), [cart]);

  const subtotal = useMemo(
    () => cartLines.reduce((sum, line) => sum + Number(line.estimated_price) * line.qty, 0),
    [cartLines]
  );

  const menuGroups = useMemo(
    () => Object.entries(groupMenuItems(restaurant?.menu_items || [])),
    [restaurant]
  );

  const availableSlots = useMemo(
    () => (slotAvailability?.slots || []).filter((slot) => slot.is_available),
    [slotAvailability]
  );

  useEffect(() => {
    setLoading(true);
    setCart({});
    setSelectedSlot("");
    Promise.all([
      api.restaurants.detail(id),
      api.get(`/reviews/restaurant/${id}/average`).catch(() => null),
      api.get(`/reviews/restaurant/${id}`).catch(() => []),
    ])
      .then(([rest, rev, revList]) => {
        setRestaurant(rest);
        setReviews(rev);
        setReviewList(revList);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!id) return;
    setSlotsLoading(true);
    setSlotsError("");
    api.deliverySlots
      .availability(id, { date: slotDate })
      .then((data) => {
        setSlotAvailability(data);
        setSelectedSlot((current) =>
          data.slots?.some((slot) => slot.slot_start === current && slot.is_available) ? current : ""
        );
      })
      .catch((err) => {
        setSlotAvailability(null);
        setSlotsError(err.message || "Could not load delivery windows.");
      })
      .finally(() => setSlotsLoading(false));
  }, [id, slotDate]);

  function addToCart(item) {
    const key = cartKeyForMenuItem(item);
    setCart((prev) => {
      const current = prev[key];
      const qty = (current?.qty || 0) + 1;
      return {
        ...prev,
        [key]: {
          cartKey: key,
          menuId: item.id,
          name: item.name,
          estimated_price: item.estimated_price,
          qty,
        },
      };
    });
  }

  function setLineQty(key, qty) {
    const nextQty = Number(qty);
    if (!Number.isFinite(nextQty) || nextQty < 1) {
      setCart((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
      return;
    }

    setCart((prev) => {
      const line = prev[key];
      if (!line) return prev;
      return { ...prev, [key]: { ...line, qty: nextQty } };
    });
  }

  function removeLine(key) {
    setCart((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }

  async function handleCheckout() {
    if (cartLines.length === 0) return;
    if (!selectedSlot) {
      setError("Choose a delivery time slot before placing your order.");
      return;
    }

    setError("");
    setSubmitting(true);
    const orderId = `ORD-${Date.now()}`;

    try {
      const body = {
        order_id: orderId,
        restaurant_id: Number(id),
        food_item: buildFoodItemSummary(cartLines),
        order_time: new Date().toISOString(),
        order_value: Math.round(subtotal * 100) / 100,
        delivery_method: orderForm.delivery_method,
        delivery_distance: FIXED_DELIVERY_DISTANCE_KM,
        customer_id: String(user.id),
      };
      const trimmedCoupon = orderForm.coupon_code?.trim();
      if (trimmedCoupon) body.coupon_code = trimmedCoupon;

      const res = await api.orders.create(body);
      await api.deliverySlots.select(res.order.order_id, selectedSlot);

      setCart({});
      navigate(`/orders/${res.order.order_id}`, {
        state: {
          message: `Order placed. Delivery scheduled for ${slotLabel({
            slot_start: selectedSlot,
            slot_end:
              slotAvailability?.slots?.find((slot) => slot.slot_start === selectedSlot)?.slot_end ||
              selectedSlot,
          })}.`,
        },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded bg-zinc-100" />
        <div className="h-4 w-32 animate-pulse rounded bg-zinc-100" />
        <div className="mt-8 space-y-3">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="h-20 animate-pulse rounded-xl bg-zinc-100" />
          ))}
        </div>
      </div>
    );
  }

  if (!restaurant) {
    return <p className="py-20 text-center text-zinc-400">Restaurant not found.</p>;
  }

  return (
    <div>
      <button onClick={() => navigate(-1)} className="mb-4 text-sm text-zinc-400 hover:text-zinc-600">
        &larr; Back
      </button>

      <div className="mb-8 overflow-hidden rounded-3xl border border-zinc-200 bg-white shadow-sm">
        <div className="bg-[linear-gradient(135deg,#effcf4_0%,#ffffff_55%,#f5f8ff_100%)] px-6 py-6">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-600">
                {restaurant.cuisine_type}
              </p>
              <h1 className="mt-2 text-3xl font-bold tracking-tight">{restaurant.name}</h1>
              {restaurant.address && <p className="mt-2 text-sm text-zinc-500">{restaurant.address}</p>}
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-zinc-600 shadow-sm ring-1 ring-zinc-100">
                  Delivery windows from 10:00 AM
                </span>
                <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-zinc-600 shadow-sm ring-1 ring-zinc-100">
                  {restaurant.menu_items?.length || 0} items on the menu
                </span>
              </div>
            </div>
            {reviews && reviews.total_reviews > 0 && (
              <div className="rounded-2xl bg-white px-5 py-4 shadow-sm ring-1 ring-zinc-100">
                <div className="text-2xl font-bold text-emerald-600">{reviews.average_rating.toFixed(1)}</div>
                <div className="text-xs text-zinc-400">
                  {reviews.total_reviews} review{reviews.total_reviews !== 1 && "s"}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="flex flex-col-reverse gap-8 lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(320px,380px)] lg:items-start">
        <div className="space-y-8">
          <section>
            <div className="mb-4 flex items-end justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Menu</h2>
                <p className="text-sm text-zinc-500">Pick your dishes, then reserve a delivery window.</p>
              </div>
            </div>

            {menuGroups.length === 0 ? (
              <p className="py-10 text-center text-zinc-400">No menu items yet.</p>
            ) : (
              <div className="space-y-6">
                {menuGroups.map(([category, items]) => (
                  <section key={category}>
                    <div className="mb-3 flex items-center gap-3">
                      <h3 className="text-base font-semibold text-zinc-900">{category}</h3>
                      <span className="h-px flex-1 bg-zinc-100" />
                    </div>
                    <div className="space-y-3">
                      {items.map((item) => (
                        <div
                          key={cartKeyForMenuItem(item)}
                          className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm"
                        >
                          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                            <div className="min-w-0 flex-1">
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <h4 className="font-medium text-zinc-900">{item.name}</h4>
                                  {item.description && (
                                    <p className="mt-1 text-sm leading-6 text-zinc-500">{item.description}</p>
                                  )}
                                </div>
                              </div>
                            </div>
                            <div className="flex shrink-0 items-center gap-3">
                              <span className="text-lg font-semibold tabular-nums text-zinc-900">
                                ${Number(item.estimated_price ?? 0).toFixed(2)}
                              </span>
                              <button
                                type="button"
                                onClick={() => addToCart(item)}
                                className="rounded-xl bg-zinc-900 px-3 py-2 text-xs font-medium text-white hover:bg-zinc-800"
                              >
                                Add to cart
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">Delivery time slots</h2>
                <p className="mt-1 text-sm text-zinc-500">
                  Choose a window for your courier. Slots update live by restaurant capacity.
                </p>
              </div>
              <label className="block text-sm">
                <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-zinc-500">
                  Delivery date
                </span>
                <input
                  type="date"
                  value={slotDate}
                  min={localDateInputValue()}
                  onChange={(event) => setSlotDate(event.target.value)}
                  className="rounded-lg border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                />
              </label>
            </div>

            {slotsError && (
              <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {slotsError}
              </div>
            )}

            {slotsLoading ? (
              <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div key={index} className="h-20 animate-pulse rounded-xl bg-zinc-100" />
                ))}
              </div>
            ) : availableSlots.length === 0 ? (
              <p className="mt-4 rounded-xl border border-dashed border-zinc-200 px-4 py-8 text-center text-sm text-zinc-400">
                No delivery windows available for this date.
              </p>
            ) : (
              <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {slotAvailability?.slots?.map((slot) => {
                  const selected = selectedSlot === slot.slot_start;
                  return (
                    <button
                      key={slot.slot_start}
                      type="button"
                      disabled={!slot.is_available}
                      onClick={() => setSelectedSlot(slot.slot_start)}
                      className={`rounded-2xl border px-4 py-3 text-left transition ${
                        selected
                          ? "border-emerald-500 bg-emerald-50 shadow-sm"
                          : slot.is_available
                            ? "border-zinc-200 bg-white hover:border-emerald-300 hover:bg-emerald-50/40"
                            : "border-zinc-100 bg-zinc-50 text-zinc-400"
                      }`}
                    >
                      <p className="text-sm font-semibold text-zinc-900">{slotLabel(slot)}</p>
                      <p
                        className={`mt-1 text-xs ${
                          slot.is_available ? "text-emerald-700" : "text-zinc-400"
                        }`}
                      >
                        {slotReason(slot)}
                      </p>
                    </button>
                  );
                })}
              </div>
            )}
          </section>
        </div>

        <aside id="restaurant-cart" className="lg:sticky lg:top-4">
          <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
            <h2 className="text-base font-semibold tracking-tight">Your order</h2>
            <p className="mt-1 text-xs text-zinc-400">
              {cartLines.length === 0
                ? "Add items from the menu."
                : `${cartLines.reduce((count, line) => count + line.qty, 0)} item${
                    cartLines.reduce((count, line) => count + line.qty, 0) !== 1 ? "s" : ""
                  } ready for delivery`}
            </p>

            {cartLines.length > 0 && (
              <ul className="mt-4 max-h-64 space-y-3 overflow-y-auto border-t border-zinc-100 pt-4">
                {cartLines.map((line) => (
                  <li key={line.cartKey} className="flex flex-wrap items-center justify-between gap-2 text-sm">
                    <div className="min-w-0 flex-1">
                      <p className="font-medium leading-snug">{line.name}</p>
                      <p className="text-xs text-zinc-400 tabular-nums">
                        ${Number(line.estimated_price).toFixed(2)} each
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex items-center rounded-lg border border-zinc-200">
                        <button
                          type="button"
                          aria-label="Decrease quantity"
                          className="px-2 py-1 text-zinc-600 hover:bg-zinc-50"
                          onClick={() => setLineQty(line.cartKey, line.qty - 1)}
                        >
                          -
                        </button>
                        <span className="min-w-[1.5rem] text-center text-xs font-medium tabular-nums">
                          {line.qty}
                        </span>
                        <button
                          type="button"
                          aria-label="Increase quantity"
                          className="px-2 py-1 text-zinc-600 hover:bg-zinc-50"
                          onClick={() => setLineQty(line.cartKey, line.qty + 1)}
                        >
                          +
                        </button>
                      </div>
                      <span className="w-16 text-right text-sm font-medium tabular-nums">
                        ${(Number(line.estimated_price) * line.qty).toFixed(2)}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeLine(line.cartKey)}
                        className="text-xs text-zinc-400 hover:text-red-600"
                      >
                        Remove
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}

            {cartLines.length > 0 && (
              <>
                <div className="mt-4 space-y-3 border-t border-zinc-100 pt-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-500">Subtotal</span>
                    <span className="font-semibold tabular-nums">${subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-500">Delivery distance</span>
                    <span className="font-medium tabular-nums">{FIXED_DELIVERY_DISTANCE_KM} km</span>
                  </div>
                  {selectedSlot && (
                    <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-800">
                      Delivery window:{" "}
                      <strong>
                        {slotLabel(
                          slotAvailability?.slots?.find((slot) => slot.slot_start === selectedSlot) || {
                            slot_start: selectedSlot,
                            slot_end: selectedSlot,
                          }
                        )}
                      </strong>
                    </div>
                  )}
                </div>

                <div className="mt-4 space-y-3 border-t border-zinc-100 pt-4">
                  <div>
                    <label className="mb-1 block text-xs font-medium text-zinc-500">Delivery method</label>
                    <select
                      value={orderForm.delivery_method}
                      onChange={(event) =>
                        setOrderForm({ ...orderForm, delivery_method: event.target.value })
                      }
                      className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
                    >
                      <option value="bike">Bike</option>
                      <option value="car">Car</option>
                    </select>
                  </div>

                  <div>
                    <label className="mb-1 block text-xs font-medium text-zinc-500">Coupon (optional)</label>
                    <input
                      type="text"
                      placeholder="Code"
                      value={orderForm.coupon_code}
                      onChange={(event) =>
                        setOrderForm({ ...orderForm, coupon_code: event.target.value })
                      }
                      className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleCheckout}
                  disabled={submitting}
                  className="mt-4 w-full rounded-xl bg-emerald-600 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                >
                  {submitting ? "Placing order..." : "Place order"}
                </button>
              </>
            )}
          </div>
        </aside>
      </div>

      <div className="mt-12">
        <h2 className="mb-4 text-lg font-semibold">
          Reviews
          {reviews && reviews.total_reviews > 0 && (
            <span className="ml-2 text-sm font-normal text-zinc-400">
              {reviews.average_rating.toFixed(1)} avg · {reviews.total_reviews} review
              {reviews.total_reviews !== 1 && "s"}
            </span>
          )}
        </h2>

        {reviewList.length === 0 ? (
          <p className="py-8 text-center text-sm text-zinc-400">
            No reviews yet. Order and be the first to leave one.
          </p>
        ) : (
          <div className="space-y-3">
            {reviewList.map((review) => (
              <div key={review.id} className="rounded-xl border border-zinc-200 bg-white p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-0.5">
                      {[1, 2, 3, 4, 5].map((value) => (
                        <span
                          key={value}
                          className={`text-sm ${value <= review.rating ? "text-emerald-500" : "text-zinc-200"}`}
                        >
                          ★
                        </span>
                      ))}
                    </div>
                    <span className="text-xs text-zinc-400">by customer #{review.customer_id}</span>
                  </div>
                  {review.created_at && (
                    <span className="text-xs text-zinc-400">
                      {new Date(review.created_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
                {review.comment && <p className="mt-2 text-sm text-zinc-600">{review.comment}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

