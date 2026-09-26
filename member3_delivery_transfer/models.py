from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

# ============================================================
# PROVISIONAL MODELS (Product, Warehouse, Location, StockQuantity)
# These mirror SCHEMA_ASSUMPTIONS.md and exist only so Member 3's
# service is runnable/testable independently. They MUST be
# reconciled with Member 2's real Master Data models once available.
# ============================================================


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, nullable=False)
    category = Column(String)
    unit_of_measure = Column(String)


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    locations = relationship("Location", back_populates="warehouse")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)

    warehouse = relationship("Warehouse", back_populates="locations")


class StockQuantity(Base):
    __tablename__ = "stock_quantities"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity = Column(Float, default=0.0, nullable=False)

    product = relationship("Product")
    location = relationship("Location")
import enum
from sqlalchemy import DateTime, Enum
from datetime import datetime


# ============================================================
# DELIVERY ORDERS
# ============================================================

class DeliveryStatus(str, enum.Enum):
    DRAFT = "draft"
    WAITING = "waiting"
    READY = "ready"
    DONE = "done"
    CANCELED = "canceled"


class DeliveryOrder(Base):
    __tablename__ = "delivery_orders"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, nullable=False)  # e.g. "DO-0001"
    source_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)

    source_location = relationship("Location")
    lines = relationship("DeliveryOrderLine", back_populates="delivery_order", cascade="all, delete-orphan")


class DeliveryOrderLine(Base):
    __tablename__ = "delivery_order_lines"

    id = Column(Integer, primary_key=True, index=True)
    delivery_order_id = Column(Integer, ForeignKey("delivery_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)

    delivery_order = relationship("DeliveryOrder", back_populates="lines")
    product = relationship("Product")


# ============================================================
# INTERNAL TRANSFERS
# ============================================================

class TransferStatus(str, enum.Enum):
    DRAFT = "draft"
    WAITING = "waiting"
    READY = "ready"
    DONE = "done"
    CANCELED = "canceled"


class InternalTransfer(Base):
    __tablename__ = "internal_transfers"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, nullable=False)  # e.g. "INT-0001"
    source_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    destination_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    status = Column(Enum(TransferStatus), default=TransferStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)

    source_location = relationship("Location", foreign_keys=[source_location_id])
    destination_location = relationship("Location", foreign_keys=[destination_location_id])
    lines = relationship("InternalTransferLine", back_populates="transfer", cascade="all, delete-orphan")


class InternalTransferLine(Base):
    __tablename__ = "internal_transfer_lines"

    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("internal_transfers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)

    transfer = relationship("InternalTransfer", back_populates="lines")
    product = relationship("Product")


# ============================================================
# SHARED STOCK MOVEMENT LEDGER
# Coordinate with Member 4 — this is the table their dashboard's
# "Move History" and stock ledger views will likely read from.
# ============================================================

class MoveType(str, enum.Enum):
    DELIVERY = "delivery"
    INTERNAL_TRANSFER = "internal_transfer"
    RECEIPT = "receipt"          # Member 2's domain, included for completeness
    ADJUSTMENT = "adjustment"    # Whoever owns adjustments


class StockMove(Base):
    __tablename__ = "stock_moves"

    id = Column(Integer, primary_key=True, index=True)
    move_type = Column(Enum(MoveType), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    source_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    destination_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    quantity = Column(Float, nullable=False)
    reference = Column(String, nullable=False)  # e.g. "DO-0001" or "INT-0001"
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")
    source_location = relationship("Location", foreign_keys=[source_location_id])
    destination_location = relationship("Location", foreign_keys=[destination_location_id])