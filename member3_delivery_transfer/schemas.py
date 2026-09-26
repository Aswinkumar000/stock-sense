from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models import DeliveryStatus, TransferStatus


# ---------- Delivery Order ----------

class DeliveryOrderLineCreate(BaseModel):
    product_id: int
    quantity: float


class DeliveryOrderCreate(BaseModel):
    reference: str
    source_location_id: int
    lines: List[DeliveryOrderLineCreate] = []


class DeliveryOrderLineOut(BaseModel):
    id: int
    product_id: int
    quantity: float

    class Config:
        from_attributes = True


class DeliveryOrderOut(BaseModel):
    id: int
    reference: str
    source_location_id: int
    status: DeliveryStatus
    created_at: datetime
    validated_at: Optional[datetime]
    lines: List[DeliveryOrderLineOut] = []

    class Config:
        from_attributes = True

# ---------- Internal Transfer ----------

class InternalTransferLineCreate(BaseModel):
    product_id: int
    quantity: float


class InternalTransferCreate(BaseModel):
    reference: str
    source_location_id: int
    destination_location_id: int
    lines: List[InternalTransferLineCreate] = []


class InternalTransferLineOut(BaseModel):
    id: int
    product_id: int
    quantity: float

    class Config:
        from_attributes = True


class InternalTransferOut(BaseModel):
    id: int
    reference: str
    source_location_id: int
    destination_location_id: int
    status: TransferStatus
    created_at: datetime
    validated_at: Optional[datetime]
    lines: List[InternalTransferLineOut] = []

    class Config:
        from_attributes = True