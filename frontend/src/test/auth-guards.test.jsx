import { MemoryRouter } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, it } from "vitest";
import App from "../App";
import { AuthProvider } from "../context/AuthContext";
import { server } from "./server";

function renderAppAt(route) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("auth and portal guards", () => {
  it("redirects to login when portal user check fails", async () => {
    localStorage.setItem(
      "user",
      JSON.stringify({ id: 10, username: "sam", role: "user", is_manager: false })
    );
    server.use(
      http.get("/api/notifications/unread/count", () =>
        HttpResponse.json({ user_id: "10", unread_count: 0 })
      ),
      http.get("/api/portal/user", () =>
        HttpResponse.json({ detail: "Login required." }, { status: 401 })
      )
    );

    renderAppAt("/");

    await screen.findByText(/sign in to your account to continue/i);
  });

  it("redirects manager route to home with actionable message on denied manager portal", async () => {
    localStorage.setItem(
      "user",
      JSON.stringify({ id: 11, username: "alex", role: "manager", is_manager: true })
    );
    server.use(
      http.get("/api/portal/manager", () =>
        HttpResponse.json({ detail: "Manager role required." }, { status: 403 })
      ),
      http.get("/api/portal/user", () =>
        HttpResponse.json({ message: "Welcome alex. User portal access granted." })
      ),
      http.get("/api/notifications/unread/count", () =>
        HttpResponse.json({ user_id: "11", unread_count: 0 })
      ),
      http.get("/api/restaurants", () =>
        HttpResponse.json({
          items: [],
          total: 0,
          page: 1,
          page_size: 12,
          total_pages: 1,
        })
      )
    );

    renderAppAt("/admin");

    await screen.findByText(/restaurants/i);
    await screen.findByText(/manager access required/i);
  });
});
