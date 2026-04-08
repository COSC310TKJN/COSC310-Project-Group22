from pydantic import BaseModel, Field


class DeliverySlotItemResponse(BaseModel):
    slot_start: str
    slot_end: str
    is_available: bool
    remaining_capacity: int
    disabled_reason: str | None = None


class DeliverySlotAvailabilityResponse(BaseModel):
    restaurant_id: int
    date: str
    slot_duration_minutes: int
    slot_capacity: int
    slots: list[DeliverySlotItemResponse]


class DeliverySlotSelectionRequest(BaseModel):
    slot_start: str = Field(..., description="ISO timestamp for the selected slot start")


class DeliverySlotBookingResponse(BaseModel):
    id: int
    order_id: str
    restaurant_id: int
    slot_start: str
    slot_end: str
    status: str
    created_at: str


class DeliverySlotConfigUpdateRequest(BaseModel):
    slot_duration_minutes: int = Field(..., ge=15, le=240)
    slot_capacity: int = Field(..., ge=1, le=100)


class DeliverySlotConfigResponse(BaseModel):
    restaurant_id: int
    slot_duration_minutes: int
    slot_capacity: int


class DeliveryBlackoutCreateRequest(BaseModel):
    start_time: str = Field(..., description="ISO timestamp")
    end_time: str = Field(..., description="ISO timestamp")
    reason: str | None = Field(default=None, max_length=200)


class DeliveryBlackoutResponse(BaseModel):
    id: int
    restaurant_id: int
    start_time: str
    end_time: str
    reason: str | None = None


class DriverAssignmentRequest(BaseModel):
    order_id: str
    driver_id: str


class DriverAssignmentResponse(BaseModel):
    id: int
    order_id: str
    driver_id: str
    assigned_at: str
    slot_start: str
    slot_end: str


class DriverQueueItemResponse(BaseModel):
    order_id: str
    restaurant_id: int
    slot_start: str
    slot_end: str
    booking_status: str


class DriverQueueResponse(BaseModel):
    driver_id: str
    items: list[DriverQueueItemResponse]
