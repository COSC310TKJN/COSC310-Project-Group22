import { Routes, Route, Navigate } from "react-router-dom";
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
import ManageRestaurants from "./pages/admin/ManageRestaurants";
import DeliverySlots from "./pages/admin/DeliverySlots";

function RequireAuth({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function RequireManager({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (!user.is_manager) return <Navigate to="/" replace />;
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
