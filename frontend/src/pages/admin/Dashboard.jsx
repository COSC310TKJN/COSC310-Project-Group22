import { Link } from "react-router-dom";

const links = [
  {
    to: "/admin/orders",
    title: "Manage Orders",
    desc: "View paid orders, failed payments, and update delivery status.",
  },
  {
    to: "/admin/restaurants",
    title: "Manage Restaurants",
    desc: "Add restaurants and menu items to the platform.",
  },
  {
    to: "/admin/delivery-slots",
    title: "Delivery Slots",
    desc: "Configure slot capacity, duration, and blackout periods.",
  },
];

export default function Dashboard() {
  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold tracking-tight">Admin Panel</h1>
      <p className="mb-8 text-zinc-500">
        Manage your restaurant operations from here.
      </p>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {links.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            className="group rounded-xl border border-zinc-200 bg-white p-6 transition-all hover:border-zinc-300 hover:shadow-sm"
          >
            <h2 className="text-lg font-semibold group-hover:text-emerald-600 transition-colors">
              {l.title}
            </h2>
            <p className="mt-2 text-sm text-zinc-500 leading-relaxed">{l.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
