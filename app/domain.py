from datetime import datetime
from decimal import Decimal
from enum import Enum
import time
from uuid import UUID

from fastapi.datastructures import Address
from eventsourcing.domain import event
from eventsourcing.domain import Aggregate


class CardType(Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMEX = "AMEX"
    DISCOVER = "DISCOVER"
    OTHER = "OTHER"


class CardLevel(Enum):
    STANDARD = "STANDARD"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    INFINITE = "INFINITE"
    BUSINESS = "BUSINESS"


class CreditCard(Aggregate):
    @event('CreditCardCreated')
    def __init__(
        self,
        card_number: str,
        bin: str,
        last4: str,
        cardholder_name: str,
        expiration_date: str,
        card_type: CardType,
        card_brand: str | None = None,
        card_level: CardLevel | None = None,
        issuer_country: str | None = None,
        issuer_name: str | None = None,
        is_commercial: bool | None = None,
        is_prepaid: bool | None = None,
        token_requestor_id: str | None = None,
    ):
        self.card_token = card_number
        self.bin = bin
        self.last4 = last4
        self.cardholder_name = cardholder_name
        self.expiration_date = expiration_date
        self.card_type = card_type
        self.card_brand = card_brand
        self.card_level = card_level
        self.issuer_country = issuer_country
        self.issuer_name = issuer_name
        self.is_commercial = is_commercial
        self.is_prepaid = is_prepaid
        self.token_requestor_id = token_requestor_id


class Merchant(Aggregate):

    @event('MerchantCreated')
    def __init__(
        self,
        id: UUID,
        name: str,
        category: str,
        location: str,
        mcc_description: str | None = None,
        website_url: str | None = None,
        merchant_age_days: int | None = None,
        risk_score: float | None = None,
        chargeback_rate_30d: float | None = None,
        refund_rate_30d: float | None = None,
        avg_ticket_amount: Decimal | None = None,
        txn_volume_30d: int | None = None,
        is_high_risk_mcc: bool | None = None,
        acquirer_id: str | None = None,
        terminal_id: str | None = None,
    ):
        self.name = name
        self.category = category
        self.location = location
        self.mcc_description = mcc_description
        self.website_url = website_url
        self.merchant_age_days = merchant_age_days
        self.risk_score = risk_score
        self.chargeback_rate_30d = chargeback_rate_30d
        self.refund_rate_30d = refund_rate_30d
        self.avg_ticket_amount = avg_ticket_amount
        self.txn_volume_30d = txn_volume_30d
        self.is_high_risk_mcc = is_high_risk_mcc
        self.acquirer_id = acquirer_id
        self.terminal_id = terminal_id


class KYCLevel(Enum):
    NONE = "NONE"
    BASIC = "BASIC"
    FULL = "FULL"
    ENHANCED = "ENHANCED"


class RiskTier(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKED = "BLOCKED"


class Customer(Aggregate):

    @event('CustomerCreated')
    def __init__(
        self,
        user_id: UUID,
        created_at: datetime,
        external_customer_id: str | None = None,
        email: str | None = None,
        email_age_days: int | None = None,
        phone: str | None = None,
        billing_address: Address | None = None,
        shipping_addresses: list[Address] | None = None,
        cards: list[CreditCard] | None = None,
        devices: list[str] | None = None,
        kyc_level: KYCLevel | None = None,
        risk_tier: RiskTier | None = None,
    ):
        self.user_id = user_id
        self.created_at = created_at
        self.external_customer_id = external_customer_id
        self.email = email
        self.email_age_days = email_age_days
        self.phone = phone
        self.billing_address = billing_address
        self.shipping_addresses = shipping_addresses
        self.cards = cards
        self.devices = devices
        self.kyc_level = kyc_level
        self.risk_tier = risk_tier


class EntryMode(Enum):
    CNP = "CNP"
    CHIP = "CHIP"
    CONTACTLESS = "CONTACTLESS"
    MAGSTRIPE = "MAGSTRIPE"


class ThreeDSResult(Enum):
    ATTEMPTED = "ATTEMPTED"
    AUTHENTICATED = "AUTHENTICATED"
    FAILED = "FAILED"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"


class Payment(Aggregate):

    @event('PaymentCreated')
    def __init__(
        self,
        id: UUID,
        timestamp: datetime,
        amount: Decimal,
        currency: str,
        card_number: str,
        merchant_id: UUID,
        entry_mode: EntryMode,
        mcc: str,
        pos_condition_code: str | None = None,
        ip_address: str | None = None,
        device_fingerprint: str | None = None,
        email: str | None = None,
        billing_address: str | None = None,
        shipping_address: str | None = None,
        three_ds_result: ThreeDSResult = ThreeDSResult.NOT_ATTEMPTED,
        cavv: str | None = None,
        eci: str | None = None,
    ):
        self.timestamp = timestamp
        self.amount = amount
        self.currency = currency
        self.card_number = card_number
        self.merchant_id = merchant_id
        self.entry_mode = entry_mode
        self.mcc = mcc
        self.pos_condition_code = pos_condition_code
        self.ip_address = ip_address
        self.device_fingerprint = device_fingerprint
        self.email = email
        self.billing_address = billing_address
        self.shipping_address = shipping_address
        self.three_ds_result = three_ds_result
        self.cavv = cavv
        self.eci = eci

    @event('PaymentRequested')
    def request(self):
        self.three_ds_result = ThreeDSResult.ATTEMPTED

        # Simulate authentication
        time.sleep(0.5)

        self.approve()

    @event('PaymentApproved')
    def approve(self):
        self.three_ds_result = ThreeDSResult.AUTHENTICATED

    @event('PaymentDeclined')
    def decline(self):
        self.three_ds_result = ThreeDSResult.FAILED
