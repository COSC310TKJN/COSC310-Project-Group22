import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { describe, it, vi } from "vitest";
import Restaurants from "../pages/Restaurants";
import { server } from "./server";

describe("restaurants page endpoint coverage", () => {
  it("loads restaurants list and searches via backend query", async () => {
    const searchSpy = vi.fn();
    server.use(
      http.get("/api/restaurants", () =>
        HttpResponse.json({
          items: [
            { id: 1, name: "Noodle House", cuisine_type: "Asian", address: "A St" },
          ],
          total: 1,
          page: 1,
          page_size: 12,
          total_pages: 1,
        })
      ),
      http.get("/api/restaurants/search", ({ request }) => {
        searchSpy(new URL(request.url).searchParams.get("q"));
        return HttpResponse.json({
          items: [
            { id: 2, name: "Pizza Lab", cuisine_type: "Italian", address: "B St" },
          ],
          total: 1,
          page: 1,
          page_size: 12,
          total_pages: 1,
        });
      })
    );

    render(
      <MemoryRouter>
        <Restaurants />
      </MemoryRouter>
    );

    await screen.findByText("Noodle House");
    await userEvent.type(
      screen.getByPlaceholderText(/search by name or cuisine/i),
      "pizza"
    );
    await userEvent.click(screen.getByRole("button", { name: /search/i }));
    await screen.findByText("Pizza Lab");
    expect(searchSpy).toHaveBeenCalledWith("pizza");
  });
});
