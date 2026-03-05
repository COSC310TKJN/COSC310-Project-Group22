### Order Backend System ###

#----------------------------------------------------------

# Description:
# Implements the Order entity for the Food Delivery Backend
# System. This pertains to all functional requirements
# for Feature 4 (Order Management), including:

# • Creating orders for authenticated users
# • Ensuring all items belong to the same restaurant
# • Enforcing order lifecycle state transitions
# • Preventing modifications after processing begins
# • Supporting order cancellation rules
# • Storing order metadata (ID, timestamp, items)

#----------------------------------------------------------
from enum import Enum

class OrderStatus (str, Enum):
    CREATED = "created"
    PAID = "paid"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order:
    def __init__(
        self,
        order_id: str,
        restaurant_id: int,
        food_item: str,
        order_time: str,
        order_value: float,
        delivery_method: str,
        delivery_distance: float,
        customer_id: str,
        traffic_condition: str = None,
        weather_condition: str = None,
        route_taken: str = None
    ):
        
        # ensures all orders have an associated ID
        if not order_id:
            raise ValueError("Order must provide an ID")
        # ensures user is authenticated to place an order
        if not customer_id:
            raise ValueError("User must be authenticated to place an order")
        # ensures the price can't be a non-negative value
        if order_value < 0:
            raise ValueError("Price cannot be negative")
        # ensures each order has a food item
        if not food_item:
            raise ValueError("Order must include a food item")
            
        # Core order data
        self.order_id = order_id
        self.restauraunt_id = restaurant_id
        self.food_items = food_item
        self.order_time = order_time
        self.order_value = order_value
        self.delivery_method = delivery_method
        self.delivery_distance = delivery_distance
        self.customer_id = customer_id
        self.traffic_condition = traffic_condition
        self.weather_condition = weather_condition
        self.route_taken = route_taken

        self.status = OrderStatus.CREATED


# State Machine (all possible states)

# Label order as paid (authenticated ayment complete)
def mark_paid(self):

    # ensures only one order can be placed at once given instance
    if self.status != OrderStatus.CREATED:
        raise ValueError("Order can only be placed once")
    
    self.status = OrderStatus.PAID

# Prepare order prior to delivery
def prep_order(self):

    # No unpaid orders can be prepared
    if self.status != OrderStatus.PAID:
        raise ValueError("Order must be paid prior to preparation")
    
    self.status = OrderStatus.PREPARING

# Sends out order for delivery
def send_out_delivery(self):

    # ensure prepared prior to delivery
    if self.status != OrderStatus.PREPARING:
        raise ValueError("Order must be prepared before delivery")
    
    self.status = OrderStatus.OUT_FOR_DELIVERY

# Labels orders as delivered
def mark_delivered(self):

    # Check
    if self.status != OrderStatus.OUT_FOR_DELIVERY:
        raise ValueError("Order must be out for delivery")
    
    self.status = OrderStatus.DELIVERED

# Cancelling an order
def cancel(self):

    # Check
    if self.status not in [OrderStatus.CREATED, OrderStatus.PAID]:
        raise ValueError("Order cannot be cancelled after preparing")
    
    self.status = OrderStatus.CANCELLED

# Serialization Component (using FastAPI)

# converts the Order object into a dictonary; "Key" : Value
def to_dict(self):

    # Maps the instance variable to a dict key
    return {
        "order_id" : self.order_id,
        "restaurant_id": self.restaurant_id,
        "food_item": self.food_item,
        "customer_id": self.customer_id,
        "order_time": self.order_time.isoformat(),
        "order_value": self.order_value,
        "delivery_method": self.delivery_method,
        "delivery_distance": self.delivery_distance,
        "traffic_condition": self.traffic_condition,
        "weather_condition": self.weather_condition,
        "route_taken": self.route_taken,
        "status": self.status
        }