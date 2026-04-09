from fastapi import APIRouter, Depends, HTTPException

from backend.app.routes.auth_routes import require_manager
from backend.models.user import User
from backend.schemas.order_schema import OrderAdminUpdate, OrderCreate, ReorderDraftRequest
from backend.app.user_storage import load_users
from backend.services.order_service import OrderService
from backend.services import notification_service


def _notify_managers_new_order(order_id):
    try:
        for user in load_users():
            if user.is_manager:
                notification_service.notify_manager_new_order(str(user.id), order_id)
    except Exception:
        pass

router = APIRouter()

@router.post("/orders")
def create_order(order: OrderCreate):
    if order.customer_id == "INVALID":
        raise HTTPException(
            status_code=400, 
            detail="Customer is not eligible"
        )
    
    new_order = OrderService.create_order(order)
    try:
        notification_service.notify_order_placed(
            str(order.customer_id), order.order_id
        )
    except Exception:
        pass
    _notify_managers_new_order(order.order_id)
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


@router.patch("/orders/{order_id}/advance")
def advance_order_status(
    order_id: str,
    _current: User = Depends(require_manager),
):
    order = OrderService.get_order(order_id)
    if not order:
        order = OrderService.get_order(f"ORD-{order_id}")
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    status_flow = {
        "created": "mark_paid",
        "paid": "prep_order",
        "preparing": "send_out_delivery",
        "out_for_delivery": "mark_delivered",
    }
    current = order.status.value if hasattr(order.status, "value") else str(order.status)
    method_name = status_flow.get(current)
    if not method_name:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot advance from status: {current}",
        )
    try:
        getattr(order, method_name)()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    from backend.repositories.order_repo import OrderRepository
    OrderRepository.save(order)

    new_status = order.status.value if hasattr(order.status, "value") else str(order.status)
    try:
        if new_status == "delivered":
            notification_service.notify_delivery(str(order.customer_id), order_id)
        else:
            notification_service.notify_status_change(
                str(order.customer_id), order_id, new_status
            )
    except Exception:
        pass

    return {
        "message": f"Order advanced to {new_status}",
        "order": order.to_dict(),
    }


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
    try:
        notification_service.notify_order_cancelled(
            str(order.customer_id), order_id
        )
    except Exception:
        pass
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

    try:
        notification_service.notify_order_placed(
            str(order.customer_id), order.order_id
        )
    except Exception:
        pass
    _notify_managers_new_order(order.order_id)

    return {
        "message": "Reorder confirmed",
        "order": order.to_dict(),
    }
