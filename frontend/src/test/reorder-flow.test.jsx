import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { describe, it } from "vitest";
import { AuthProvider } from "../context/AuthContext";
import OrderDetail from "../pages/OrderDetail";
import ReorderConfirm from "../pages/ReorderConfirm";
import { server } from "./server";

function ReorderLanding() {
  const location = useLocation();
  return (
    <div>
      <p>Reorder confirm route</p>
      <p>{location.state?.sourceOrderId}</p>
    </div>
  );
}

describe("reorder two-click flow", () => {
  it("clicking reorder from order detail creates draft then navigates to confirm route", async () => {
    localStorage.setItem(
      "user",
      JSON.stringify({ id: 12, username: "jamie", role: "user", is_manager: false })
    );
    server.use(
      http.get("/api/orders/100", () =>
        HttpResponse.json({
          order_id: "100",
          restaurant_id: 1,
          food_item: "Pizza",
          order_time: new Date().toISOString(),
          order_value: 20,
          delivery_method: "bike",
          delivery_distance: 5,
          customer_id: "12",
          status: "delivered",
        })
      ),
      http.get("/api/orders/100/total", () =>
        HttpResponse.json({ order_id: "100", pricing: { total: 22.4 } })
      ),
      http.get("/api/payments/order/100", () =>
        HttpResponse.json({ detail: "Not found" }, { status: 404 })
      ),
      http.get("/api/payments/order/100/receipt", () =>
        HttpResponse.json({ detail: "Not found" }, { status: 404 })
      ),
      http.post("/api/orders/100/reorder", () =>
        HttpResponse.json({
          reorder_draft_id: "draft-1",
          order: {
            source_order_id: "100",
            food_item: "Pizza",
            order_time: new Date().toISOString(),
            delivery_method: "bike",
            order_value: 20,
          },
        })
      )
    );

    render(
      <MemoryRouter initialEntries={["/orders/100"]}>
        <AuthProvider>
          <Routes>
            <Route path="/orders/:orderId" element={<OrderDetail />} />
            <Route path="/orders/reorder/:draftId" element={<ReorderLanding />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await screen.findByRole("button", { name: /reorder/i });
    await userEvent.click(screen.getByRole("button", { name: /reorder/i }));
    await screen.findByText(/reorder confirm route/i);
    await screen.findByText("100");
  });

  it("supports edit and confirm on dedicated reorder page", async () => {
    localStorage.setItem(
      "user",
      JSON.stringify({ id: 13, username: "taylor", role: "user", is_manager: false })
    );
    server.use(
      http.patch("/api/orders/reorder/draft-2", async ({ request }) => {
        const body = await request.json();
        return HttpResponse.json({
          reorder_draft_id: "draft-2",
          order: {
            source_order_id: "150",
            restaurant_id: 1,
            food_item: "Burger",
            order_value: 19,
            order_time: body.order_time || "2026-04-01T10:00:00Z",
            delivery_method: body.delivery_method || "bike",
          },
        });
      }),
      http.post("/api/orders/reorder/draft-2/confirm", () =>
        HttpResponse.json({
          message: "Reorder confirmed",
          order: { order_id: "ORD-777", source_order_id: "150" },
        })
      )
    );

    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: "/orders/reorder/draft-2",
            state: {
              sourceOrderId: "150",
              draftOrder: {
                source_order_id: "150",
                restaurant_id: 1,
                food_item: "Burger",
                order_value: 19,
                order_time: "2026-04-01T10:00:00Z",
                delivery_method: "bike",
              },
            },
          },
        ]}
      >
        <AuthProvider>
          <Routes>
            <Route path="/orders/reorder/:draftId" element={<ReorderConfirm />} />
            <Route path="/orders/:orderId" element={<div>Order detail destination</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await screen.findByRole("heading", { name: /confirm reorder/i });
    await userEvent.selectOptions(screen.getByRole("combobox"), "car");
    await userEvent.click(screen.getByRole("button", { name: /make changes/i }));
    await screen.findByText(/changes saved/i);
    await userEvent.click(screen.getByRole("button", { name: /confirm reorder/i }));
    await screen.findByText(/order detail destination/i);
  });
});
