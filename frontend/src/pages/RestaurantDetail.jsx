import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function RestaurantDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [restaurant, setRestaurant] = useState(null);
  const [reviews, setReviews] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ordering, setOrdering] = useState(null);
  const [orderForm, setOrderForm] = useState({
    delivery_method: "bike",
    delivery_distance: 5,
    coupon_code: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
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

  async function handleOrder(item) {
    setError("");
    setSubmitting(true);
    const orderId = `ORD-${Date.now()}`;
    try {
      const body = {
        order_id: orderId,
        restaurant_id: Number(id),
        food_item: item.name,
        order_time: new Date().toISOString(),
        order_value: item.estimated_price,
        delivery_method: orderForm.delivery_method,
        delivery_distance: orderForm.delivery_distance,
        customer_id: String(user.id),
      };
      const trimmed = orderForm.coupon_code?.trim();
      if (trimmed) body.coupon_code = trimmed;
      const res = await api.post("/orders", body);
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

      <h2 className="mb-4 text-lg font-semibold">Menu</h2>

      {restaurant.menu_items?.length === 0 ? (
        <p className="py-10 text-center text-zinc-400">No menu items yet.</p>
      ) : (
        <div className="space-y-3">
          {restaurant.menu_items?.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between rounded-xl border border-zinc-200 bg-white p-4"
            >
              <div className="flex-1">
                <h3 className="font-medium">{item.name}</h3>
                {item.description && (
                  <p className="mt-0.5 text-sm text-zinc-500">{item.description}</p>
                )}
              </div>
              <div className="ml-4 flex items-center gap-3">
                <span className="text-lg font-semibold tabular-nums">
                  ${item.estimated_price.toFixed(2)}
                </span>
                {ordering === item.id ? (
                  <div className="flex items-center gap-2">
                    <select
                      value={orderForm.delivery_method}
                      onChange={(e) =>
                        setOrderForm({ ...orderForm, delivery_method: e.target.value })
                      }
                      className="rounded-lg border border-zinc-300 px-2 py-1 text-xs"
                    >
                      <option value="bike">Bike</option>
                      <option value="car">Car</option>
                    </select>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      step="0.5"
                      value={orderForm.delivery_distance}
                      onChange={(e) =>
                        setOrderForm({
                          ...orderForm,
                          delivery_distance: Number(e.target.value),
                        })
                      }
                      className="w-16 rounded-lg border border-zinc-300 px-2 py-1 text-xs"
                      title="Distance (km)"
                    />
                    <input
                      type="text"
                      placeholder="Coupon (optional)"
                      value={orderForm.coupon_code}
                      onChange={(e) =>
                        setOrderForm({ ...orderForm, coupon_code: e.target.value })
                      }
                      className="w-28 rounded-lg border border-zinc-300 px-2 py-1 text-xs"
                      title="Discount code"
                    />
                    <button
                      onClick={() => handleOrder(item)}
                      disabled={submitting}
                      className="rounded-lg bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                    >
                      {submitting ? "..." : "Confirm"}
                    </button>
                    <button
                      onClick={() => setOrdering(null)}
                      className="text-xs text-zinc-400 hover:text-zinc-600"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setOrdering(item.id)}
                    className="rounded-lg bg-zinc-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-zinc-800"
                  >
                    Order
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
