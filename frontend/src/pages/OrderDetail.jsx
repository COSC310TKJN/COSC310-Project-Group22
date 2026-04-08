import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

/** Payments use numeric order_id (digits from order id, e.g. ORD-1712… → 1712…). */
function paymentOrderKey(routeOrderId) {
  const n = Number(String(routeOrderId).replace(/\D/g, ""));
  return Number.isFinite(n) && n > 0 ? n : null;
}

const STATUS_COLORS = {
  created: "bg-blue-100 text-blue-700",
  paid: "bg-indigo-100 text-indigo-700",
  preparing: "bg-amber-100 text-amber-700",
  out_for_delivery: "bg-orange-100 text-orange-700",
  delivered: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-red-100 text-red-700",
  completed: "bg-emerald-100 text-emerald-700",
  pending: "bg-yellow-100 text-yellow-700",
  failed: "bg-red-100 text-red-700",
};

export default function OrderDetail() {
  const { orderId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [order, setOrder] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [payment, setPayment] = useState(null);
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Payment form
  const [payMethod, setPayMethod] = useState("credit_card");
  const [paying, setPaying] = useState(false);

  // Review form
  const [showReview, setShowReview] = useState(false);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: "" });
  const [reviewSubmitted, setReviewSubmitted] = useState(false);
  const [submittingReview, setSubmittingReview] = useState(false);

  // Reorder
  const [reordering, setReordering] = useState(false);

  function loadOrder() {
    setLoading(true);
    const payKey = paymentOrderKey(orderId);
    Promise.all([
      api.get(`/orders/${orderId}`),
      api.get(`/orders/${orderId}/total`).catch(() => null),
      payKey
        ? api.get(`/payments/order/${payKey}`).catch(() => null)
        : Promise.resolve(null),
      payKey
        ? api.get(`/payments/order/${payKey}/receipt`).catch(() => null)
        : Promise.resolve(null),
    ])
      .then(([ord, pri, pay, rec]) => {
        setOrder(ord);
        setPricing(pri?.pricing || null);
        setPayment(pay);
        setReceipt(rec);
      })
      .catch(() => setError("Failed to load order"))
      .finally(() => setLoading(false));
  }

  useEffect(loadOrder, [orderId]);

  async function handlePay() {
    setError("");
    setPaying(true);
    try {
      const payKey = paymentOrderKey(orderId);
      if (!payKey) {
        throw new Error(
          "This order id cannot be used for payments. Use a numeric or ORD-{digits} id."
        );
      }
      const total = pricing?.total || order.order_value;
      await api.post("/payments/", {
        order_id: payKey,
        customer_id: String(user.id),
        amount: total,
        payment_method: payMethod,
      });
      loadOrder();
    } catch (err) {
      setError(err.message);
    } finally {
      setPaying(false);
    }
  }

  async function handleCancel() {
    setError("");
    try {
      await api.post(`/orders/${orderId}/cancel`);
      loadOrder();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleReview() {
    setSubmittingReview(true);
    try {
      await api.post("/reviews/", {
        customer_id: String(user.id),
        order_id: paymentOrderKey(orderId) || 0,
        restaurant_id: order.restaurant_id,
        rating: reviewForm.rating,
        comment: reviewForm.comment || null,
      });
      setReviewSubmitted(true);
      setShowReview(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmittingReview(false);
    }
  }

  async function handleReorder() {
    setReordering(true);
    setError("");
    try {
      const res = await api.post(`/orders/${orderId}/reorder`, {
        customer_id: String(user.id),
      });
      const confirmRes = await api.post(
        `/orders/reorder/${res.reorder_draft_id}/confirm`
      );
      navigate(`/orders/${confirmRes.order.order_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setReordering(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded bg-zinc-100" />
        <div className="h-40 animate-pulse rounded-xl bg-zinc-100" />
      </div>
    );
  }

  if (!order) {
    return <p className="py-20 text-center text-zinc-400">Order not found.</p>;
  }

  const canPay = order.status === "created" && !payment;
  const canCancel = ["created", "paid"].includes(order.status);
  const canReview = order.status === "delivered" && !reviewSubmitted;
  const canReorder = order.status === "delivered";

  return (
    <div>
      <button
        onClick={() => navigate("/orders")}
        className="mb-4 text-sm text-zinc-400 hover:text-zinc-600"
      >
        &larr; Back to orders
      </button>

      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Order {orderId}</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Restaurant #{order.restaurant_id}
          </p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${
            STATUS_COLORS[order.status] || "bg-zinc-100 text-zinc-600"
          }`}
        >
          {order.status?.replace(/_/g, " ")}
        </span>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Order details */}
      <div className="mb-6 rounded-xl border border-zinc-200 bg-white p-5">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-400">
          Details
        </h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <span className="text-xs text-zinc-400">Item</span>
            <p className="font-medium">{order.food_item}</p>
          </div>
          <div>
            <span className="text-xs text-zinc-400">Value</span>
            <p className="font-medium tabular-nums">
              ${Number(order.order_value).toFixed(2)}
            </p>
          </div>
          <div>
            <span className="text-xs text-zinc-400">Delivery</span>
            <p className="font-medium">
              {order.delivery_method} &middot; {order.delivery_distance} km
            </p>
          </div>
          <div>
            <span className="text-xs text-zinc-400">Ordered</span>
            <p className="font-medium">
              {new Date(order.order_time).toLocaleString()}
            </p>
          </div>
          {order.coupon_code && (
            <div>
              <span className="text-xs text-zinc-400">Coupon</span>
              <p className="font-medium">{order.coupon_code}</p>
            </div>
          )}
        </div>
      </div>

      {/* Pricing */}
      {pricing && (
        <div className="mb-6 rounded-xl border border-zinc-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Pricing
          </h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-zinc-500">Subtotal</span>
              <span className="tabular-nums">${Number(pricing.subtotal).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Delivery fee</span>
              <span className="tabular-nums">${Number(pricing.delivery_fee).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Tax</span>
              <span className="tabular-nums">${Number(pricing.tax).toFixed(2)}</span>
            </div>
            {Number(pricing.discount) > 0 && (
              <div className="flex justify-between text-emerald-700">
                <span>
                  Coupon discount
                  {pricing.coupon_code ? ` (${pricing.coupon_code})` : ""}
                </span>
                <span className="tabular-nums">
                  −${Number(pricing.discount).toFixed(2)}
                </span>
              </div>
            )}
            <div className="flex justify-between border-t border-zinc-100 pt-2 font-semibold">
              <span>Total</span>
              <span className="tabular-nums">${Number(pricing.total).toFixed(2)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Payment */}
      {payment && (
        <div className="mb-6 rounded-xl border border-zinc-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Payment
          </h2>
          <div className="flex items-center justify-between text-sm">
            <span className="text-zinc-500">
              {payment.transaction_id}
            </span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-semibold uppercase ${
                STATUS_COLORS[payment.status] || "bg-zinc-100"
              }`}
            >
              {payment.status}
            </span>
          </div>
        </div>
      )}

      {/* Receipt */}
      {receipt && (
        <div className="mb-6 rounded-xl border border-zinc-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Receipt
          </h2>
          <div className="space-y-1 text-sm">
            <p className="text-zinc-500">
              Receipt #{receipt.receipt_number}
            </p>
            <p>
              Amount: ${Number(receipt.amount).toFixed(2)} &middot; Tax: $
              {Number(receipt.tax).toFixed(2)} &middot; Total: $
              {Number(receipt.total).toFixed(2)}
            </p>
            <p className="text-xs text-zinc-400">
              Paid via {receipt.payment_method}
            </p>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        {canPay && (
          <div className="flex items-center gap-2">
            <select
              value={payMethod}
              onChange={(e) => setPayMethod(e.target.value)}
              className="rounded-lg border border-zinc-300 px-2 py-2 text-sm"
            >
              <option value="credit_card">Credit Card</option>
              <option value="debit_card">Debit Card</option>
              <option value="paypal">PayPal</option>
            </select>
            <button
              onClick={handlePay}
              disabled={paying}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              {paying ? "Processing..." : "Pay now"}
            </button>
          </div>
        )}

        {canCancel && (
          <button
            onClick={handleCancel}
            className="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
          >
            Cancel order
          </button>
        )}

        {canReorder && (
          <button
            onClick={handleReorder}
            disabled={reordering}
            className="rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-50 disabled:opacity-50"
          >
            {reordering ? "Reordering..." : "Reorder"}
          </button>
        )}

        {canReview && !showReview && (
          <button
            onClick={() => setShowReview(true)}
            className="rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-50"
          >
            Leave a review
          </button>
        )}
      </div>

      {/* Review form */}
      {showReview && (
        <div className="mt-4 rounded-xl border border-zinc-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Write a review
          </h2>
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Rating
              </label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    onClick={() => setReviewForm({ ...reviewForm, rating: n })}
                    className={`h-8 w-8 rounded-lg text-sm font-semibold transition-colors ${
                      n <= reviewForm.rating
                        ? "bg-emerald-600 text-white"
                        : "bg-zinc-100 text-zinc-400"
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Comment (optional)
              </label>
              <textarea
                rows={3}
                value={reviewForm.comment}
                onChange={(e) =>
                  setReviewForm({ ...reviewForm, comment: e.target.value })
                }
                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleReview}
                disabled={submittingReview}
                className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                {submittingReview ? "Submitting..." : "Submit review"}
              </button>
              <button
                onClick={() => setShowReview(false)}
                className="rounded-lg border border-zinc-200 px-3 py-2 text-sm text-zinc-500 hover:bg-zinc-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {reviewSubmitted && (
        <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
          Review submitted. Thank you for your feedback.
        </div>
      )}
    </div>
  );
}
