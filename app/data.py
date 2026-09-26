from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain import EntryMode, ThreeDSResult
from pydantic import BaseModel


class CreditCardData(BaseModel):
    card_number: str
    bin: str
    last4: str
    cardholder_name: str
    expiration_date: str
    card_type: str
    card_brand: str | None = None
    card_level: str | None = None
    issuer_country: str | None = None
    issuer_name: str | None = None
    is_commercial: bool | None = None
    is_prepaid: bool | None = None
    token_requestor_id: str | None = None


class MerchantData(BaseModel):
    id: UUID
    name: str
    category: str
    location: str


class PaymentData(BaseModel):
    id: UUID
    timestamp: datetime
    amount: Decimal
    currency: str
    card: CreditCardData
    merchant: MerchantData
    entry_mode: EntryMode
    mcc: str
    pos_condition_code: str | None = None
    ip_address: str | None = None
    device_fingerprint: str | None = None
    email: str | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    three_ds_result: ThreeDSResult = ThreeDSResult.NOT_ATTEMPTED
    cavv: str | None = None
    eci: str | None = None
