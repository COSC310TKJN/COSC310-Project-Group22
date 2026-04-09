import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import RestaurantDetail from "../pages/RestaurantDetail";
import { AuthProvider } from "../context/AuthContext";
import { server } from "./server";

describe("restaurant detail delivery flow", () => {
  it("creates an order and books the selected delivery slot", async () => {
    localStorage.setItem(
      "user",
      JSON.stringify({ id: 7, username: "casey", is_manager: false, role: "user" })
    );

    const createOrderSpy = vi.fn();
    const selectSlotSpy = vi.fn();

    server.use(
      http.get("/api/restaurants/1", () =>
        HttpResponse.json({
          id: 1,
          name: "Noodle House",
          cuisine_type: "Asian",
          address: "123 Main St",
          menu_items: [
            {
              id: 11,
              name: "Spicy Ramen",
              estimated_price: 14.5,
              description: "Rich broth",
              category: "Bowls",
            },
          ],
        })
      ),
      http.get("/api/reviews/restaurant/1/average", () => HttpResponse.json({ average_rating: 4.7, total_reviews: 2 })),
      http.get("/api/reviews/restaurant/1", () => HttpResponse.json([])),
      http.get("/api/restaurants/1/delivery-slots/availability", () =>
        HttpResponse.json({
          restaurant_id: 1,
          date: "2026-04-08",
          slot_duration_minutes: 60,
          slot_capacity: 3,
          slots: [
            {
              slot_start: "2026-04-08T17:00:00+00:00",
              slot_end: "2026-04-08T18:00:00+00:00",
              is_available: true,
              remaining_capacity: 2,
              disabled_reason: null,
            },
          ],
        })
      ),
      http.post("/api/orders", async ({ request }) => {
        const body = await request.json();
        createOrderSpy(body);
        return HttpResponse.json({
          message: "Order created",
          order: { ...body, status: "created" },
        });
      }),
      http.post("/api/orders/:orderId/delivery-slot", async ({ request, params }) => {
        const body = await request.json();
        selectSlotSpy({ orderId: params.orderId, body });
        return HttpResponse.json({
          id: 1,
          order_id: params.orderId,
          restaurant_id: 1,
          slot_start: body.slot_start,
          slot_end: "2026-04-08T18:00:00+00:00",
          status: "scheduled",
          created_at: "2026-04-08T16:00:00+00:00",
        });
      })
    );

    render(
      <MemoryRouter initialEntries={["/restaurants/1"]}>
        <AuthProvider>
          <Routes>
            <Route path="/restaurants/:id" element={<RestaurantDetail />} />
            <Route path="/orders/:orderId" element={<div>Order page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await screen.findByText("Noodle House");
    await userEvent.click(screen.getByRole("button", { name: /add to cart/i }));
    await userEvent.click(screen.getByRole("button", { name: /2 left/i }));
    await userEvent.click(screen.getByRole("button", { name: /place order/i }));

    await screen.findByText("Order page");

    expect(createOrderSpy).toHaveBeenCalledTimes(1);
    expect(selectSlotSpy).toHaveBeenCalledWith({
      orderId: expect.stringMatching(/^ORD-\d+$/),
      body: { slot_start: "2026-04-08T17:00:00+00:00" },
    });
  });

  it("requires a delivery slot before checkout", async () => {
    localStorage.setItem(
      "user",
      JSON.stringify({ id: 7, username: "casey", is_manager: false, role: "user" })
    );

    server.use(
      http.get("/api/restaurants/1", () =>
        HttpResponse.json({
          id: 1,
          name: "Noodle House",
          cuisine_type: "Asian",
          menu_items: [{ id: 11, name: "Spicy Ramen", estimated_price: 14.5 }],
        })
      ),
      http.get("/api/reviews/restaurant/1/average", () => HttpResponse.json({ average_rating: 4.7, total_reviews: 2 })),
      http.get("/api/reviews/restaurant/1", () => HttpResponse.json([])),
      http.get("/api/restaurants/1/delivery-slots/availability", () =>
        HttpResponse.json({
          restaurant_id: 1,
          date: "2026-04-08",
          slot_duration_minutes: 60,
          slot_capacity: 3,
          slots: [
            {
              slot_start: "2026-04-08T17:00:00+00:00",
              slot_end: "2026-04-08T18:00:00+00:00",
              is_available: true,
              remaining_capacity: 2,
              disabled_reason: null,
            },
          ],
        })
      )
    );

    render(
      <MemoryRouter initialEntries={["/restaurants/1"]}>
        <AuthProvider>
          <Routes>
            <Route path="/restaurants/:id" element={<RestaurantDetail />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await screen.findByText("Noodle House");
    await userEvent.click(screen.getByRole("button", { name: /add to cart/i }));
    await userEvent.click(screen.getByRole("button", { name: /place order/i }));

    expect(await screen.findByText(/choose a delivery time slot/i)).toBeInTheDocument();
  });
});
