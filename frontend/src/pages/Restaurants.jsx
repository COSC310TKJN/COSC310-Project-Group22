import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

const CUISINES = ["All", "American", "Asian", "Italian", "Mediterranean", "Mexican"];

function restaurantSummary(restaurant) {
  const menuCount = restaurant.menu_items?.length || 0;
  if (menuCount > 0) {
    return `${menuCount} menu item${menuCount !== 1 ? "s" : ""} ready to order`;
  }
  if (restaurant.address) {
    return "Browse the menu and schedule delivery";
  }
  return "Fresh meals with delivery scheduling";
}

export default function Restaurants() {
  const [restaurants, setRestaurants] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [cuisine, setCuisine] = useState("All");
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const cuisineFilter = cuisine !== "All" ? cuisine : undefined;
    const request = query
      ? api.restaurants.search({ q: query, page, pageSize: 12, cuisine: cuisineFilter })
      : api.restaurants.list({ page, pageSize: 12, cuisine: cuisineFilter });
    request
      .then((data) => {
        setRestaurants(data.items);
        setTotal(data.total);
        setTotalPages(data.total_pages);
      })
      .catch(() => setRestaurants([]))
      .finally(() => setLoading(false));
  }, [page, cuisine, query]);

  function handleSearch(e) {
    e.preventDefault();
    setPage(1);
    setQuery(search.trim());
  }

  function handleCuisine(c) {
    setCuisine(c);
    setPage(1);
  }

  return (
    <div>
      <div className="mb-8 rounded-3xl border border-emerald-100 bg-[linear-gradient(135deg,#f5fff8_0%,#ffffff_45%,#f7fbff_100%)] p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-600">
              QuickBite delivery
            </p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-zinc-950">
              Restaurants near you
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-zinc-600">
              Compare cuisines, open a menu, and choose a delivery window before you place your order.
            </p>
          </div>
          <div className="rounded-2xl bg-white px-4 py-3 text-sm shadow-sm ring-1 ring-zinc-100">
            <p className="text-zinc-400">Available now</p>
            <p className="mt-1 text-2xl font-semibold text-zinc-950">{total}</p>
          </div>
        </div>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="mb-6 flex gap-2">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or cuisine..."
          className="flex-1 rounded-lg border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        />
        <button
          type="submit"
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800"
        >
          Search
        </button>
        {query && (
          <button
            type="button"
            onClick={() => { setSearch(""); setQuery(""); setPage(1); }}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-50"
          >
            Clear
          </button>
        )}
      </form>

      {/* Cuisine filter */}
      <div className="mb-6 flex flex-wrap gap-2">
        {CUISINES.map((c) => (
          <button
            key={c}
            onClick={() => handleCuisine(c)}
            className={`rounded-full px-3 py-1 text-sm font-medium transition-colors ${
              cuisine === c
                ? "bg-emerald-600 text-white"
                : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200"
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      {/* Results */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-xl bg-zinc-100" />
          ))}
        </div>
      ) : restaurants.length === 0 ? (
        <div className="py-20 text-center">
          <p className="text-lg font-medium text-zinc-400">No restaurants found</p>
          <p className="mt-1 text-sm text-zinc-400">Try adjusting your search or filters.</p>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {restaurants.map((r) => (
              <Link
                key={r.id}
                to={`/restaurants/${r.id}`}
                className="group overflow-hidden rounded-2xl border border-zinc-200 bg-white transition-all hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-lg"
              >
                <div className="border-b border-zinc-100 bg-[linear-gradient(135deg,#fafafa_0%,#eefbf4_100%)] px-5 py-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-zinc-400">
                        {r.cuisine_type}
                      </p>
                      <h3 className="mt-1 font-semibold text-zinc-900 transition-colors group-hover:text-emerald-600">
                        {r.name}
                      </h3>
                    </div>
                    <span className="rounded-full bg-white px-2 py-0.5 text-xs font-medium text-zinc-500 shadow-sm ring-1 ring-zinc-100">
                      #{r.id}
                    </span>
                  </div>
                </div>
                <div className="px-5 py-4">
                  <p className="text-sm text-zinc-600">{restaurantSummary(r)}</p>
                  {r.address && (
                    <p className="mt-3 text-xs text-zinc-400">{r.address}</p>
                  )}
                  <div className="mt-4 flex items-center justify-between">
                    <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                      Delivery slots available
                    </span>
                    <span className="text-sm font-medium text-zinc-900">
                      View menu &rarr;
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="mt-8 flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-lg border border-zinc-200 px-3 py-1.5 text-sm font-medium text-zinc-600 hover:bg-zinc-50 disabled:opacity-40"
              >
                Previous
              </button>
              <span className="px-3 text-sm text-zinc-500">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="rounded-lg border border-zinc-200 px-3 py-1.5 text-sm font-medium text-zinc-600 hover:bg-zinc-50 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
