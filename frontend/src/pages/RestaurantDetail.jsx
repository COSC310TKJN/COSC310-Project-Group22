import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

/** Matches backend `FIXED_DELIVERY_DISTANCE_KM` (default 5). Not user-editable. */
const FIXED_DELIVERY_DISTANCE_KM = 5;

function buildFoodItemSummary(lines) {
  return lines.map((l) => `${l.qty}× ${l.name}`).join("; ");
}

/** Stable cart row key (handles missing `id` in API data). */
function cartKeyForMenuItem(item) {
  if (item == null) return "unknown";
  if (item.id != null && item.id !== "") return String(item.id);
  const name = item.name ?? "item";
  const price = item.estimated_price ?? 0;
  return `${name}:${price}`;
}

export default function RestaurantDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [restaurant, setRestaurant] = useState(null);
  const [reviews, setReviews] = useState(null);
  const [loading, setLoading] = useState(true);
  /** cart[cartKey] = { cartKey, menuId, name, estimated_price, qty } */
  const [cart, setCart] = useState({});
  const [orderForm, setOrderForm] = useState({
    delivery_method: "bike",
    coupon_code: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const cartLines = useMemo(
    () => Object.values(cart).filter((l) => l.qty > 0),
    [cart]
  );

  const subtotal = useMemo(
    () =>
      cartLines.reduce(
        (sum, l) => sum + Number(l.estimated_price) * l.qty,
        0
      ),
    [cartLines]
  );

  useEffect(() => {
    setLoading(true);
    setCart({});
    Promise.all([
      api.get(`/restaurants/${id}`),
      api.get(`/reviews/restaurant/${id}/average`).catch(() => null),
    ])
      .then(([rest, rev]) => {
        setRestaurant(rest);
        setReviews(rev);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  function addToCart(item) {
    const key = cartKeyForMenuItem(item);
    setCart((prev) => {
      const cur = prev[key];
      const qty = (cur?.qty || 0) + 1;
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
    const n = Number(qty);
    if (!Number.isFinite(n) || n < 1) {
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
      return { ...prev, [key]: { ...line, qty: n } };
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
      const trimmed = orderForm.coupon_code?.trim();
      if (trimmed) body.coupon_code = trimmed;
      const res = await api.post("/orders", body);
      setCart({});
      navigate(`/orders/${res.order.order_id}`);
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
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded-xl bg-zinc-100" />
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
      <button
        onClick={() => navigate(-1)}
        className="mb-4 text-sm text-zinc-400 hover:text-zinc-600"
      >
        &larr; Back
      </button>

      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{restaurant.name}</h1>
          <p className="mt-1 text-zinc-500">{restaurant.cuisine_type}</p>
          {restaurant.address && (
            <p className="mt-0.5 text-sm text-zinc-400">{restaurant.address}</p>
          )}
        </div>
        {reviews && reviews.total_reviews > 0 && (
          <div className="text-right">
            <div className="text-2xl font-bold text-emerald-600">
              {reviews.average_rating.toFixed(1)}
            </div>
            <div className="text-xs text-zinc-400">
              {reviews.total_reviews} review{reviews.total_reviews !== 1 && "s"}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {/*
        Mobile: cart first (flex-col-reverse) so "Add to cart" updates are visible without scrolling past the whole menu.
        lg+: two-column grid — menu | cart.
      */}
      <div className="flex flex-col-reverse gap-8 lg:grid lg:grid-cols-[1fr_minmax(280px,360px)] lg:items-start lg:gap-8">
        <div>
          <h2 className="mb-4 text-lg font-semibold">Menu</h2>

          {restaurant.menu_items?.length === 0 ? (
            <p className="py-10 text-center text-zinc-400">No menu items yet.</p>
          ) : (
            <div className="space-y-3">
              {restaurant.menu_items?.map((item) => (
                <div
                  key={cartKeyForMenuItem(item)}
                  className="flex items-center justify-between gap-3 rounded-xl border border-zinc-200 bg-white p-4"
                >
                  <div className="min-w-0 flex-1">
                    <h3 className="font-medium">{item.name}</h3>
                    {item.description && (
                      <p className="mt-0.5 text-sm text-zinc-500">{item.description}</p>
                    )}
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    <span className="text-lg font-semibold tabular-nums">
                      ${Number(item.estimated_price ?? 0).toFixed(2)}
                    </span>
                    <button
                      type="button"
                      onClick={() => addToCart(item)}
                      className="rounded-lg bg-zinc-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-zinc-800"
                    >
                      Add to cart
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <aside
          id="restaurant-cart"
          className="lg:sticky lg:top-4 lg:mt-0"
        >
          <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
            <h2 className="text-base font-semibold tracking-tight">Your order</h2>
            <p className="mt-0.5 text-xs text-zinc-400">
              {cartLines.length === 0
                ? "Add items from the menu."
                : `${cartLines.reduce((n, l) => n + l.qty, 0)} item${
                    cartLines.reduce((n, l) => n + l.qty, 0) !== 1 ? "s" : ""
                  } from this restaurant`}
            </p>

            {cartLines.length > 0 && (
              <ul className="mt-4 max-h-64 space-y-3 overflow-y-auto border-t border-zinc-100 pt-4">
                {cartLines.map((line) => (
                  <li
                    key={line.cartKey}
                    className="flex flex-wrap items-center justify-between gap-2 text-sm"
                  >
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
                          −
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
                <div className="mt-4 flex justify-between border-t border-zinc-100 pt-4 text-sm">
                  <span className="text-zinc-500">Subtotal</span>
                  <span className="font-semibold tabular-nums">
                    ${subtotal.toFixed(2)}
                  </span>
                </div>

                <div className="mt-4 space-y-3 border-t border-zinc-100 pt-4">
                  <div>
                    <label className="mb-1 block text-xs font-medium text-zinc-500">
                      Delivery
                    </label>
                    <div className="flex flex-wrap items-center gap-2">
                      <select
                        value={orderForm.delivery_method}
                        onChange={(e) =>
                          setOrderForm({ ...orderForm, delivery_method: e.target.value })
                        }
                        className="w-full rounded-lg border border-zinc-300 px-2 py-2 text-sm sm:w-auto"
                      >
                        <option value="bike">Bike</option>
                        <option value="car">Car</option>
                      </select>
                      <span className="inline-flex shrink-0 items-center whitespace-nowrap text-xs tabular-nums text-zinc-500">
                        {FIXED_DELIVERY_DISTANCE_KM}
                        {"\u00A0"}
                        km
                      </span>
                    </div>
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium text-zinc-500">
                      Coupon (optional)
                    </label>
                    <input
                      type="text"
                      placeholder="Code"
                      value={orderForm.coupon_code}
                      onChange={(e) =>
                        setOrderForm({ ...orderForm, coupon_code: e.target.value })
                      }
                      className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleCheckout}
                  disabled={submitting}
                  className="mt-4 w-full rounded-lg bg-emerald-600 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                >
                  {submitting ? "Placing order…" : "Place order"}
                </button>
              </>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
