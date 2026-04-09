import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

const CUISINES = ["All", "American", "Asian", "Italian", "Mediterranean", "Mexican"];

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
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Restaurants</h1>
        <p className="mt-1 text-zinc-500">
          {total} restaurants available
        </p>
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
                className="group rounded-xl border border-zinc-200 bg-white p-5 transition-all hover:border-zinc-300 hover:shadow-sm"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-zinc-900 group-hover:text-emerald-600 transition-colors">
                      {r.name}
                    </h3>
                    <p className="mt-1 text-sm text-zinc-500">{r.cuisine_type}</p>
                  </div>
                  <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-500">
                    #{r.id}
                  </span>
                </div>
                {r.address && (
                  <p className="mt-3 text-xs text-zinc-400">{r.address}</p>
                )}
              </Link>
            ))}
          </div>

          {/* Pagination */}
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
