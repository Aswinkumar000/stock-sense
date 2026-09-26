from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

import models
import schemas


def create_internal_transfer(db: Session, payload: schemas.InternalTransferCreate):
    if payload.source_location_id == payload.destination_location_id:
        raise HTTPException(status_code=400, detail="Source and destination locations must differ")

    existing = db.query(models.InternalTransfer).filter(
        models.InternalTransfer.reference == payload.reference
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Reference already exists")

    transfer = models.InternalTransfer(
        reference=payload.reference,
        source_location_id=payload.source_location_id,
        destination_location_id=payload.destination_location_id,
        status=models.TransferStatus.DRAFT,
    )
    for line in payload.lines:
        transfer.lines.append(
            models.InternalTransferLine(
                product_id=line.product_id,
                quantity=line.quantity,
            )
        )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


def get_internal_transfer(db: Session, transfer_id: int):
    transfer = db.query(models.InternalTransfer).filter(
        models.InternalTransfer.id == transfer_id
    ).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Internal transfer not found")
    return transfer


def _get_or_create_stock(db: Session, product_id: int, location_id: int):
    stock = db.query(models.StockQuantity).filter(
        models.StockQuantity.product_id == product_id,
        models.StockQuantity.location_id == location_id,
    ).first()
    if not stock:
        stock = models.StockQuantity(product_id=product_id, location_id=location_id, quantity=0.0)
        db.add(stock)
        db.flush()  # so it's usable within this transaction without a full commit
    return stock


def validate_internal_transfer(db: Session, transfer_id: int):
    transfer = get_internal_transfer(db, transfer_id)

    if transfer.status == models.TransferStatus.DONE:
        raise HTTPException(status_code=400, detail="Transfer already validated")
    if transfer.status == models.TransferStatus.CANCELED:
        raise HTTPException(status_code=400, detail="Cannot validate a canceled transfer")
    if not transfer.lines:
        raise HTTPException(status_code=400, detail="Cannot validate a transfer with no lines")

    # Check source availability for every line BEFORE making any changes
    for line in transfer.lines:
        source_stock = db.query(models.StockQuantity).filter(
            models.StockQuantity.product_id == line.product_id,
            models.StockQuantity.location_id == transfer.source_location_id,
        ).first()
        available = source_stock.quantity if source_stock else 0.0
        if available < line.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product_id={line.product_id} at source: "
                       f"available={available}, requested={line.quantity}"
            )

    # All checks passed -- apply source decrease, destination increase, and log the move
    for line in transfer.lines:
        source_stock = db.query(models.StockQuantity).filter(
            models.StockQuantity.product_id == line.product_id,
            models.StockQuantity.location_id == transfer.source_location_id,
        ).first()
        source_stock.quantity -= line.quantity

        dest_stock = _get_or_create_stock(db, line.product_id, transfer.destination_location_id)
        dest_stock.quantity += line.quantity

        db.add(models.StockMove(
            move_type=models.MoveType.INTERNAL_TRANSFER,
            product_id=line.product_id,
            source_location_id=transfer.source_location_id,
            destination_location_id=transfer.destination_location_id,
            quantity=line.quantity,
            reference=transfer.reference,
        ))

    transfer.status = models.TransferStatus.DONE
    transfer.validated_at = datetime.utcnow()

    db.commit()
    db.refresh(transfer)
    return transfer