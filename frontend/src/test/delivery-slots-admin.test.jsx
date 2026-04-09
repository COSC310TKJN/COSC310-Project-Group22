import { render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import DeliverySlots from "../pages/admin/DeliverySlots";
import { server } from "./server";

describe("delivery slots admin page", () => {
  it("loads restaurants and shows slot availability for the selected restaurant", async () => {
    const availabilitySpy = vi.fn();
    const blackoutSpy = vi.fn();

    server.use(
      http.get("/api/restaurants", () =>
        HttpResponse.json({
          items: [
            { id: 1, name: "Noodle House", cuisine_type: "Asian", address: "123 Main St" },
            { id: 2, name: "Pizza Lab", cuisine_type: "Italian", address: "42 Oak Ave" },
          ],
          total: 2,
          page: 1,
          page_size: 100,
          total_pages: 1,
        })
      ),
      http.get("/api/restaurants/:restaurantId/delivery-slots/availability", ({ params, request }) => {
        availabilitySpy({ restaurantId: params.restaurantId, date: new URL(request.url).searchParams.get("date") });
        return HttpResponse.json({
          restaurant_id: Number(params.restaurantId),
          date: "2026-04-08",
          slot_duration_minutes: 45,
          slot_capacity: 4,
          slots: [
            {
              slot_start: "2026-04-08T17:00:00+00:00",
              slot_end: "2026-04-08T17:45:00+00:00",
              is_available: true,
              remaining_capacity: 3,
              disabled_reason: null,
            },
          ],
        });
      }),
      http.get("/api/admin/restaurants/:restaurantId/delivery-blackouts", ({ params, request }) => {
        blackoutSpy({ restaurantId: params.restaurantId, date: new URL(request.url).searchParams.get("date") });
        return HttpResponse.json([]);
      })
    );

    render(<DeliverySlots />);

    expect(await screen.findByRole("heading", { name: "Noodle House" })).toBeInTheDocument();
    expect(await screen.findByDisplayValue("45")).toBeInTheDocument();
    expect(await screen.findByText(/3 spots left/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(availabilitySpy).toHaveBeenCalled();
      expect(blackoutSpy).toHaveBeenCalled();
    });
  });
});
