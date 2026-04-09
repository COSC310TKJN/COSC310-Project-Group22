
# Frontend (Vite + React)

## Run with Docker Compose (dev)
From repo root:

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000` (proxied through frontend as `/api`)

Environment:
- `API_PROXY_TARGET` is used by Vite dev proxy.
- In Compose, it is set to `http://backend:8000`.

## Endpoint coverage in frontend
- Auth/session + portals:
  - `POST /auth/register`
  - `POST /auth/login`
  - `POST /auth/logout`
  - `GET /portal/user`
  - `GET /portal/manager`
- Restaurants/menu:
  - `GET /restaurants`
  - `GET /restaurants/search`
  - `GET /restaurants/{id}`
  - `GET /restaurants/{id}/menu`
  - `POST /restaurants` (manager)
  - `POST /menu-items` (manager)
- Orders/reorder:
  - `GET /orders/history/{customer_id}`
  - `GET /orders/{order_id}`
  - `GET /orders/{order_id}/total`
  - `POST /orders/{order_id}/reorder`
  - `PATCH /orders/reorder/{draft_id}`
  - `POST /orders/reorder/{draft_id}/confirm`

## Reorder UX
- Click `Reorder` on order detail to create draft.
- User is routed to `/orders/reorder/:draftId`.
- User can click `Make changes` (edits `order_time` + `delivery_method`).
- User clicks `Confirm reorder` to place a new order.

## Frontend tests
Run in `frontend/`:

```bash
npm test
```

Test stack:
- Vitest
- React Testing Library
- user-event
- MSW

Coverage includes:
- Auth + portal route guards
- Restaurant browse/search flows
- Manager create restaurant/menu item endpoint interactions
- Reorder two-click flow (draft -> edit -> confirm)

## Docker smoke checklist
1. Register and login a user.
2. Browse/search restaurants and open a restaurant detail page.
3. Place an order and view it in order history.
4. Open a delivered order and click `Reorder`.
5. On confirm page, click `Make changes`, then `Confirm reorder`.
6. Verify navigation to the new order and presence in history.
