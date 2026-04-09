from fastapi import APIRouter, Depends, HTTPException

from backend.app.routes.auth_routes import require_manager
from backend.models.user import User
from backend.schemas.order_schema import OrderAdminUpdate, OrderCreate, ReorderDraftRequest
from backend.services.order_service import OrderService

router = APIRouter()

@router.post("/orders")
def create_order(order: OrderCreate):
    if order.customer_id == "INVALID":
        raise HTTPException(
            status_code=400, 
            detail="Customer is not eligible"
        )
    
    new_order = OrderService.create_order(order)
    return {
        "message": "Order created",
        "order": new_order.to_dict()
    }


@router.get("/orders/admin")
def admin_list_orders(_current: User = Depends(require_manager)):
    orders = OrderService.list_all_orders()
    return {"orders": [o.to_dict() for o in orders]}


@router.patch("/orders/admin/{order_id}")
def admin_update_order(
    order_id: str,
    body: OrderAdminUpdate,
    _current: User = Depends(require_manager),
):
    updates = body.model_dump(exclude_unset=True)
    try:
        order = OrderService.admin_update_order(order_id, updates)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"message": "Order updated", "order": order.to_dict()}


@router.get("/orders/{order_id}")
def get_order(order_id: str):
    order = OrderService.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=404, 
            detail="Order not found"
        )
    return order.to_dict()


@router.get("/orders/history/{customer_id}")
def get_order_history(customer_id: str):
    orders = OrderService.get_order_history(customer_id)
    return {
        "customer_id": customer_id,
        "orders": [order.to_dict() for order in orders],
    }


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str):
    order = OrderService.cancel_order(order_id)
    return {
        "message": "Order cancelled",
        "order": order.to_dict()
    }


@router.get("/orders/{order_id}/total")
def get_order_total(order_id: str):
    try:
        pricing = OrderService.calculate_order_total(order_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        "order_id": order_id,
        "pricing": pricing,
    }


@router.post("/orders/{order_id}/reorder")
def create_reorder_draft(order_id: str, request: ReorderDraftRequest):
    try:
        draft_id, payload = OrderService.create_reorder_draft(order_id, request.customer_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Order not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Cannot reorder another customer's order")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "message": "Reorder draft created",
        "reorder_draft_id": draft_id,
        "order": payload,
    }


@router.patch("/orders/reorder/{reorder_draft_id}")
def update_reorder_draft(reorder_draft_id: str, request: dict):
    updates = {key: value for key, value in request.items() if value is not None}
    try:
        payload = OrderService.update_reorder_draft(reorder_draft_id, updates)
    except LookupError:
        raise HTTPException(status_code=404, detail="Reorder draft not found")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "message": "Reorder draft updated",
        "reorder_draft_id": reorder_draft_id,
        "order": payload,
    }


@router.post("/orders/reorder/{reorder_draft_id}/confirm")
def confirm_reorder(reorder_draft_id: str):
    try:
        order = OrderService.confirm_reorder(reorder_draft_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Reorder draft not found")

    return {
        "message": "Reorder confirmed",
        "order": order.to_dict(),
    }
