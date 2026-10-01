from datetime import datetime
from decimal import Decimal
from typing import Any, cast
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import BaseModel

from app.application import CustomPostgresFactory, PaymentApplication
from app.domain import Payment, EntryMode

root_router = APIRouter()


@root_router.head("/")
async def health_check_head():
    return {"status": "healthy"}

event_router = APIRouter(prefix="/events", tags=["events"])


@event_router.get("/")
async def get_events():
    return {"events": [""]}


health_router = APIRouter(prefix="/health", tags=["health"])


def get_main_app(request: Request) -> PaymentApplication:
    """Get the main application instance from app state."""
    main_app = getattr(request.app.state, "main_app", None)
    if main_app is None:
        raise HTTPException(
            status_code=503, detail="Application not initialized")
    return main_app


@health_router.get("/")
async def health_check(request: Request) -> dict[str, Any]:
    """Health check endpoint to verify database connectivity."""
    main_app = get_main_app(request)

    try:
        recorder = main_app.recorder
        max_id = recorder.max_notification_id()
        pool = cast(CustomPostgresFactory, main_app.factory).datastore.pool
        stats = pool.get_stats()

        return {
            "status": "healthy",
            "database": "connected",
            "max_notification_id": max_id,
            "pool_size": stats.get("pool_size", 0),
            "pool_available": stats.get("pool_available", 0),
            "pool_min": stats.get("pool_min", 0),
            "pool_max": stats.get("pool_max", 0),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Database error: {str(e)}")


payment_router = APIRouter(prefix="/payments", tags=["payments"])


class ProcessPaymentRequest(BaseModel):
    amount: Decimal
    currency: str
    customer_id: UUID
    card_number: str
    merchant_id: UUID
    entry_mode: EntryMode


@payment_router.post("/")
async def process_payment(request: ProcessPaymentRequest = Body(), app: PaymentApplication = Depends(get_main_app)):
    payment = Payment(
        id=uuid4(),
        timestamp=datetime.now(),
        amount=request.amount,
        currency=request.currency,
        customer_id=request.customer_id,
        card_number=request.card_number,
        merchant_id=request.merchant_id,
        entry_mode=request.entry_mode,
        mcc="1234"
    )
    app.request_payment(payment)
    return payment
