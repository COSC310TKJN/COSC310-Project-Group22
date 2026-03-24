from fastapi import APIRouter
from backend.schemas.order_schema import OrderCreate
from backend.services.order_service import OrderService


router = APIRouter()


@router.post("/orders")
def create_order(order: OrderCreate):

    new_order = OrderService.create_order(order)

    return {
        "message": "Order created",
        "order": new_order.to_dict()
    }


@router.get("/orders/{order_id}")
def get_order(order_id: str):

    order = OrderService.get_order(order_id)

    if not order:
        return {"error": "Order not found"}

    return order.to_dict()


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str):

    order = OrderService.cancel_order(order_id)

    return {
        "message": "Order cancelled",
        "order": order.to_dict()
    }

@router.get("/orders/{order_id}/total")
def get_order_total(order_id: str):

    pricing = OrderService.calculate_order_total(order_id)

    return {
        "order_id": order_id,
        "pricing": pricing
    }