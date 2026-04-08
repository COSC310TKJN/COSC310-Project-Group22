import { useState } from "react";
import { api } from "../../api";

const CUISINES = ["American", "Asian", "Italian", "Mediterranean", "Mexican"];

export default function ManageRestaurants() {
  // Add restaurant form
  const [restForm, setRestForm] = useState({
    name: "",
    cuisine_type: "American",
    address: "",
  });
  const [restMsg, setRestMsg] = useState("");
  const [restErr, setRestErr] = useState("");
  const [addingRest, setAddingRest] = useState(false);

  // Add menu item form
  const [menuForm, setMenuForm] = useState({
    restaurant_id: "",
    name: "",
    base_price: "",
    estimated_price: "",
    description: "",
    category: "",
  });
  const [menuMsg, setMenuMsg] = useState("");
  const [menuErr, setMenuErr] = useState("");
  const [addingMenu, setAddingMenu] = useState(false);

  async function handleAddRestaurant(e) {
    e.preventDefault();
    setRestErr("");
    setRestMsg("");
    setAddingRest(true);
    try {
      const data = await api.post("/restaurants", {
        name: restForm.name,
        cuisine_type: restForm.cuisine_type,
        address: restForm.address || null,
      });
      setRestMsg(`Restaurant "${data.name}" created (ID: ${data.id}).`);
      setRestForm({ name: "", cuisine_type: "American", address: "" });
    } catch (err) {
      setRestErr(err.message);
    } finally {
      setAddingRest(false);
    }
  }

  async function handleAddMenuItem(e) {
    e.preventDefault();
    setMenuErr("");
    setMenuMsg("");
    setAddingMenu(true);
    try {
      const basePrice = Number(menuForm.base_price);
      const data = await api.post("/menu-items", {
        restaurant_id: Number(menuForm.restaurant_id),
        name: menuForm.name,
        base_price: basePrice,
        estimated_price: Number(menuForm.estimated_price) || basePrice * 1.12,
        description: menuForm.description || null,
        category: menuForm.category || null,
      });
      setMenuMsg(`Menu item "${data.name}" added (ID: ${data.id}).`);
      setMenuForm({
        restaurant_id: menuForm.restaurant_id,
        name: "",
        base_price: "",
        estimated_price: "",
        description: "",
        category: "",
      });
    } catch (err) {
      setMenuErr(err.message);
    } finally {
      setAddingMenu(false);
    }
  }

  const inputCls =
    "w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500";

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold tracking-tight">
        Manage Restaurants
      </h1>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Add Restaurant */}
        <div className="rounded-xl border border-zinc-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold">Add Restaurant</h2>

          {restMsg && (
            <div className="mb-3 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
              {restMsg}
            </div>
          )}
          {restErr && (
            <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {restErr}
            </div>
          )}

          <form onSubmit={handleAddRestaurant} className="space-y-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Name
              </label>
              <input
                required
                value={restForm.name}
                onChange={(e) =>
                  setRestForm({ ...restForm, name: e.target.value })
                }
                className={inputCls}
                placeholder="Restaurant name"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Cuisine
              </label>
              <select
                value={restForm.cuisine_type}
                onChange={(e) =>
                  setRestForm({ ...restForm, cuisine_type: e.target.value })
                }
                className={inputCls}
              >
                {CUISINES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Address (optional)
              </label>
              <input
                value={restForm.address}
                onChange={(e) =>
                  setRestForm({ ...restForm, address: e.target.value })
                }
                className={inputCls}
                placeholder="123 Main St"
              />
            </div>
            <button
              type="submit"
              disabled={addingRest}
              className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              {addingRest ? "Creating..." : "Create restaurant"}
            </button>
          </form>
        </div>

        {/* Add Menu Item */}
        <div className="rounded-xl border border-zinc-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold">Add Menu Item</h2>

          {menuMsg && (
            <div className="mb-3 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
              {menuMsg}
            </div>
          )}
          {menuErr && (
            <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {menuErr}
            </div>
          )}

          <form onSubmit={handleAddMenuItem} className="space-y-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Restaurant ID
              </label>
              <input
                required
                type="number"
                min="1"
                value={menuForm.restaurant_id}
                onChange={(e) =>
                  setMenuForm({ ...menuForm, restaurant_id: e.target.value })
                }
                className={inputCls}
                placeholder="e.g. 1"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Item Name
              </label>
              <input
                required
                value={menuForm.name}
                onChange={(e) =>
                  setMenuForm({ ...menuForm, name: e.target.value })
                }
                className={inputCls}
                placeholder="Grilled Salmon"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-sm font-medium text-zinc-700">
                  Base Price
                </label>
                <input
                  required
                  type="number"
                  step="0.01"
                  min="0"
                  value={menuForm.base_price}
                  onChange={(e) =>
                    setMenuForm({ ...menuForm, base_price: e.target.value })
                  }
                  className={inputCls}
                  placeholder="12.99"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-zinc-700">
                  Est. Price
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={menuForm.estimated_price}
                  onChange={(e) =>
                    setMenuForm({
                      ...menuForm,
                      estimated_price: e.target.value,
                    })
                  }
                  className={inputCls}
                  placeholder="Auto if empty"
                />
              </div>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Description (optional)
              </label>
              <input
                value={menuForm.description}
                onChange={(e) =>
                  setMenuForm({ ...menuForm, description: e.target.value })
                }
                className={inputCls}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-zinc-700">
                Category (optional)
              </label>
              <input
                value={menuForm.category}
                onChange={(e) =>
                  setMenuForm({ ...menuForm, category: e.target.value })
                }
                className={inputCls}
                placeholder="Mains, Desserts, etc."
              />
            </div>
            <button
              type="submit"
              disabled={addingMenu}
              className="w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              {addingMenu ? "Adding..." : "Add menu item"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
