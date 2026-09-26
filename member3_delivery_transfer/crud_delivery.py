from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

import models
import schemas


def create_delivery_order(db: Session, payload: schemas.DeliveryOrderCreate):
    existing = db.query(models.DeliveryOrder).filter(
        models.DeliveryOrder.reference == payload.reference
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Reference already exists")

    delivery = models.DeliveryOrder(
        reference=payload.reference,
        source_location_id=payload.source_location_id,
        status=models.DeliveryStatus.DRAFT,
    )
    for line in payload.lines:
        delivery.lines.append(
            models.DeliveryOrderLine(
                product_id=line.product_id,
                quantity=line.quantity,
            )
        )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery


def get_delivery_order(db: Session, delivery_id: int):
    delivery = db.query(models.DeliveryOrder).filter(
        models.DeliveryOrder.id == delivery_id
    ).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery order not found")
    return delivery


def validate_delivery_order(db: Session, delivery_id: int):
    delivery = get_delivery_order(db, delivery_id)

    if delivery.status == models.DeliveryStatus.DONE:
        raise HTTPException(status_code=400, detail="Delivery order already validated")
    if delivery.status == models.DeliveryStatus.CANCELED:
        raise HTTPException(status_code=400, detail="Cannot validate a canceled delivery order")
    if not delivery.lines:
        raise HTTPException(status_code=400, detail="Cannot validate a delivery order with no lines")

    # Check stock availability for every line BEFORE making any changes
    for line in delivery.lines:
        stock = db.query(models.StockQuantity).filter(
            models.StockQuantity.product_id == line.product_id,
            models.StockQuantity.location_id == delivery.source_location_id,
        ).first()

        available = stock.quantity if stock else 0.0
        if available < line.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product_id={line.product_id}: "
                       f"available={available}, requested={line.quantity}"
            )

    # All checks passed -- apply the changes
    for line in delivery.lines:
        stock = db.query(models.StockQuantity).filter(
            models.StockQuantity.product_id == line.product_id,
            models.StockQuantity.location_id == delivery.source_location_id,
        ).first()

        stock.quantity -= line.quantity

        db.add(models.StockMove(
            move_type=models.MoveType.DELIVERY,
            product_id=line.product_id,
            source_location_id=delivery.source_location_id,
            destination_location_id=None,
            quantity=line.quantity,
            reference=delivery.reference,
        ))

    delivery.status = models.DeliveryStatus.DONE
    delivery.validated_at = datetime.utcnow()

    db.commit()
    db.refresh(delivery)
    return delivery