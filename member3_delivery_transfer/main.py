from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models
import schemas
import crud_delivery
import crud_transfer


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockSense - Delivery & Internal Transfers Service (Member 3)",
    description="Handles Delivery Orders (outgoing stock) and Internal Transfers "
                 "(stock movement between locations), built on a shared stock ledger.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "StockSense Delivery & Internal Transfers API is running!",
        "docs": "Visit /docs for interactive API documentation",
    }


@app.post("/api/delivery-orders", response_model=schemas.DeliveryOrderOut)
def create_delivery_order(payload: schemas.DeliveryOrderCreate, db: Session = Depends(get_db)):
    return crud_delivery.create_delivery_order(db, payload)


@app.get("/api/delivery-orders/{delivery_id}", response_model=schemas.DeliveryOrderOut)
def get_delivery_order(delivery_id: int, db: Session = Depends(get_db)):
    return crud_delivery.get_delivery_order(db, delivery_id)


@app.post("/api/delivery-orders/{delivery_id}/validate", response_model=schemas.DeliveryOrderOut)
def validate_delivery_order(delivery_id: int, db: Session = Depends(get_db)):
    return crud_delivery.validate_delivery_order(db, delivery_id)
@app.post("/api/internal-transfers", response_model=schemas.InternalTransferOut)
def create_internal_transfer(payload: schemas.InternalTransferCreate, db: Session = Depends(get_db)):
    return crud_transfer.create_internal_transfer(db, payload)


@app.get("/api/internal-transfers/{transfer_id}", response_model=schemas.InternalTransferOut)
def get_internal_transfer(transfer_id: int, db: Session = Depends(get_db)):
    return crud_transfer.get_internal_transfer(db, transfer_id)


@app.post("/api/internal-transfers/{transfer_id}/validate", response_model=schemas.InternalTransferOut)
def validate_internal_transfer(transfer_id: int, db: Session = Depends(get_db)):
    return crud_transfer.validate_internal_transfer(db, transfer_id)