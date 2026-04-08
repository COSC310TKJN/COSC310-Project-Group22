import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useEffect, useState } from "react";
import { api } from "../api";

function Badge({ count }) {
  if (!count) return null;
  return (
    <span className="ml-1 inline-flex items-center justify-center rounded-full bg-emerald-600 px-1.5 py-0.5 text-[10px] font-semibold leading-none text-white">
      {count}
    </span>
  );
}

const navLink =
  "px-3 py-1.5 rounded-lg text-sm font-medium transition-colors hover:bg-zinc-100";
const activeNav = "bg-zinc-100 text-zinc-900";
const inactiveNav = "text-zinc-500";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!user) return;
    api
      .get(`/notifications/unread/count?user_id=${user.id}`)
      .then((d) => setUnread(d.unread_count))
      .catch(() => {});
    const interval = setInterval(() => {
      api
        .get(`/notifications/unread/count?user_id=${user.id}`)
        .then((d) => setUnread(d.unread_count))
        .catch(() => {});
    }, 15000);
    return () => clearInterval(interval);
  }, [user]);

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <div className="min-h-[100dvh] flex flex-col">
      <header className="sticky top-0 z-30 border-b border-zinc-200 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
          <Link to="/" className="text-lg font-bold tracking-tight text-zinc-900">
            QuickBite
          </Link>

          {user && (
            <nav className="flex items-center gap-1">
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `${navLink} ${isActive ? activeNav : inactiveNav}`
                }
              >
                Restaurants
              </NavLink>
              <NavLink
                to="/orders"
                className={({ isActive }) =>
                  `${navLink} ${isActive ? activeNav : inactiveNav}`
                }
              >
                Orders
              </NavLink>
              <NavLink
                to="/notifications"
                className={({ isActive }) =>
                  `${navLink} ${isActive ? activeNav : inactiveNav}`
                }
              >
                Notifications
                <Badge count={unread} />
              </NavLink>
              {user.is_manager && (
                <NavLink
                  to="/admin"
                  className={({ isActive }) =>
                    `${navLink} ${isActive ? activeNav : inactiveNav}`
                  }
                >
                  Admin
                </NavLink>
              )}
            </nav>
          )}

          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-xs text-zinc-400">
                {user.username}
                {user.is_manager && (
                  <span className="ml-1 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold text-amber-700">
                    MGR
                  </span>
                )}
              </span>
              <button
                onClick={handleLogout}
                className="rounded-lg border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-600 transition-colors hover:bg-zinc-50"
              >
                Log out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="rounded-lg px-3 py-1.5 text-sm font-medium text-zinc-600 hover:bg-zinc-100"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-800"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
        <Outlet />
      </main>

      <footer className="border-t border-zinc-200 py-6 text-center text-xs text-zinc-400">
        COSC 310 — Food Delivery Platform
      </footer>
    </div>
  );
}
