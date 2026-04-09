import { Routes, Route, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Restaurants from "./pages/Restaurants";
import RestaurantDetail from "./pages/RestaurantDetail";
import OrderHistory from "./pages/OrderHistory";
import OrderDetail from "./pages/OrderDetail";
import Notifications from "./pages/Notifications";
import Dashboard from "./pages/admin/Dashboard";
import ManageOrders from "./pages/admin/ManageOrders";
import AdminOrderEdit from "./pages/admin/AdminOrderEdit";
import ManageRestaurants from "./pages/admin/ManageRestaurants";
import DeliverySlots from "./pages/admin/DeliverySlots";
import ReorderConfirm from "./pages/ReorderConfirm";

function RequireAuth({ children }) {
  const { user, clearAuth, verifyUserPortal } = useAuth();
  const [checking, setChecking] = useState(true);
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    let mounted = true;
    if (!user) {
      setChecking(false);
      setAllowed(false);
      return () => {
        mounted = false;
      };
    }

    verifyUserPortal()
      .then(() => {
        if (!mounted) return;
        setAllowed(true);
      })
      .catch(() => {
        if (!mounted) return;
        clearAuth();
        setAllowed(false);
      })
      .finally(() => {
        if (!mounted) return;
        setChecking(false);
      });

    return () => {
      mounted = false;
    };
  }, [user, clearAuth, verifyUserPortal]);

  if (!user) return <Navigate to="/login" replace />;
  if (checking) return <div className="text-sm text-zinc-500">Checking session...</div>;
  if (!allowed) {
    return <Navigate to="/login" replace state={{ message: "Your session expired. Please sign in again." }} />;
  }
  return children;
}

function RequireManager({ children }) {
  const { user, clearAuth, verifyManagerPortal } = useAuth();
  const [checking, setChecking] = useState(true);
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    let mounted = true;
    if (!user) {
      setChecking(false);
      setAllowed(false);
      return () => {
        mounted = false;
      };
    }

    verifyManagerPortal()
      .then(() => {
        if (!mounted) return;
        setAllowed(true);
      })
      .catch((error) => {
        if (!mounted) return;
        const message = String(error?.message || "").toLowerCase();
        if (message.includes("login") || message.includes("authentication")) {
          clearAuth();
        }
        setAllowed(false);
      })
      .finally(() => {
        if (!mounted) return;
        setChecking(false);
      });

    return () => {
      mounted = false;
    };
  }, [user, clearAuth, verifyManagerPortal]);

  if (!user) return <Navigate to="/login" replace />;
  if (checking) return <div className="text-sm text-zinc-500">Checking manager access...</div>;
  if (!allowed) {
    return (
      <Navigate
        to="/"
        replace
        state={{ message: "Manager access required. Sign in with a manager account to continue." }}
      />
    );
  }
  return children;
}

function RedirectIfAuth({ children }) {
  const { user } = useAuth();
  if (user) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Public auth routes */}
        <Route
          path="/login"
          element={
            <RedirectIfAuth>
              <Login />
            </RedirectIfAuth>
          }
        />
        <Route
          path="/register"
          element={
            <RedirectIfAuth>
              <Register />
            </RedirectIfAuth>
          }
        />

        {/* Authenticated user routes */}
        <Route
          path="/"
          element={
            <RequireAuth>
              <Restaurants />
            </RequireAuth>
          }
        />
        <Route
          path="/restaurants/:id"
          element={
            <RequireAuth>
              <RestaurantDetail />
            </RequireAuth>
          }
        />
        <Route
          path="/orders"
          element={
            <RequireAuth>
              <OrderHistory />
            </RequireAuth>
          }
        />
        <Route
          path="/orders/:orderId"
          element={
            <RequireAuth>
              <OrderDetail />
            </RequireAuth>
          }
        />
        <Route
          path="/orders/reorder/:draftId"
          element={
            <RequireAuth>
              <ReorderConfirm />
            </RequireAuth>
          }
        />
        <Route
          path="/notifications"
          element={
            <RequireAuth>
              <Notifications />
            </RequireAuth>
          }
        />

        {/* Admin routes (manager only) */}
        <Route
          path="/admin"
          element={
            <RequireManager>
              <Dashboard />
            </RequireManager>
          }
        />
        <Route
          path="/admin/orders"
          element={
            <RequireManager>
              <ManageOrders />
            </RequireManager>
          }
        />
        <Route
          path="/admin/order/:orderId"
          element={
            <RequireManager>
              <AdminOrderEdit />
            </RequireManager>
          }
        />
        <Route
          path="/admin/restaurants"
          element={
            <RequireManager>
              <ManageRestaurants />
            </RequireManager>
          }
        />
        <Route
          path="/admin/delivery-slots"
          element={
            <RequireManager>
              <DeliverySlots />
            </RequireManager>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
