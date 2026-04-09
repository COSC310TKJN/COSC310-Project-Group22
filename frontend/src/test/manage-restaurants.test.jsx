import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { describe, it } from "vitest";
import ManageRestaurants from "../pages/admin/ManageRestaurants";
import { server } from "./server";

describe("manager restaurant/menu endpoints", () => {
  it("submits restaurant create payload and shows backend response", async () => {
    server.use(
      http.post("/api/restaurants", async ({ request }) => {
        const body = await request.json();
        return HttpResponse.json({ id: 101, ...body }, { status: 201 });
      }),
      http.post("/api/menu-items", () =>
        HttpResponse.json({ detail: "Valid restaurant_id is required." }, { status: 400 })
      )
    );

    render(
      <MemoryRouter>
        <ManageRestaurants />
      </MemoryRouter>
    );

    await userEvent.type(screen.getByPlaceholderText(/restaurant name/i), "Manager Bistro");
    await userEvent.click(screen.getByRole("button", { name: /create restaurant/i }));
    await screen.findByText(/Manager Bistro/i);
  });

  it("surfaces backend validation error for menu item create", async () => {
    server.use(
      http.post("/api/restaurants", () => HttpResponse.json({}, { status: 201 })),
      http.post("/api/menu-items", () =>
        HttpResponse.json({ detail: "Valid restaurant_id is required." }, { status: 400 })
      )
    );

    render(
      <MemoryRouter>
        <ManageRestaurants />
      </MemoryRouter>
    );

    const inputs = screen.getAllByRole("spinbutton");
    await userEvent.type(inputs[0], "9999");
    await userEvent.type(screen.getByPlaceholderText(/grilled salmon/i), "Ghost Noodles");
    await userEvent.type(inputs[1], "10");
    await userEvent.click(screen.getByRole("button", { name: /add menu item/i }));

    await screen.findByText(/valid restaurant_id is required/i);
  });
});
