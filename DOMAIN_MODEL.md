# Fraud Detection - Domain Model Documentation

## Overview

This document defines the core domain entities for the Credit Card Card-Not-Present (CNP) Fraud Detection system. The domain model follows the transaction flow:

```
Customer → Merchant → Payment Gateway → Acquirer → Card Network → Issuer → Approve/Decline
                 ↑
          Fraud checks happen HERE (or at issuer)
```

---

## Core Domain Entities

### 1. Transaction
**Purpose**: Core entity representing a payment transaction to be scored for fraud risk.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transaction_id` | UUID | Yes | Unique identifier |
| `timestamp` | DateTime | Yes | Transaction time (UTC) |
| `amount` | Decimal | Yes | Transaction amount |
| `currency` | String(3) | Yes | ISO 4217 currency code |
| `card` | CreditCard | Yes | Card details (tokenized) |
| `merchant` | Merchant | Yes | Merchant information |
| `entry_mode` | Enum | Yes | `CNP`, `CHIP`, `CONTACTLESS`, `MAGSTRIPE` |
| `pos_condition_code` | String(2) | No | POS entry capability |
| `mcc` | String(4) | Yes | Merchant Category Code |
| `ip_address` | String(45) | No | Customer IP (IPv4/IPv6) |
| `device_fingerprint` | String(64) | No | Hashed device identifier |
| `email` | String(255) | No | Customer email |
| `billing_address` | Address | No | Billing address |
| `shipping_address` | Address | No | Shipping address (if different) |
| `three_ds_result` | Enum | No | `ATTEMPTED`, `AUTHENTICATED`, `FAILED`, `NOT_ATTEMPTED` |
| `cavv` | String(40) | No | Cardholder Authentication Verification Value |
| `eci` | String(2) | No | Electronic Commerce Indicator |

**Derived Fields (computed at scoring time)**:
- `distance_from_last_txn_km` - Haversine distance from previous transaction
- `time_since_last_txn_sec` - Seconds since user's last transaction
- `ip_country_vs_card_country` - Boolean mismatch flag
- `amount_zscore` - Z-score vs user's historical amounts

---

### 2. CreditCard
**Purpose**: Tokenized card information (never store full PAN in production).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `card_token` | String(64) | Yes | Tokenized reference to vaulted PAN |
| `bin` | String(6-8) | Yes | Bank Identification Number |
| `last4` | String(4) | Yes | Last 4 digits for display |
| `cardholder_name` | String(100) | Yes | Name on card |
| `expiration_date` | String(4) | Yes | MMYY format |
| `card_type` | Enum | Yes | `VISA`, `MASTERCARD`, `AMEX`, `DISCOVER`, `OTHER` |
| `card_brand` | String(50) | No | Specific product (e.g., "Visa Signature") |
| `card_level` | Enum | No | `STANDARD`, `GOLD`, `PLATINUM`, `INFINITE`, `BUSINESS` |
| `issuer_country` | String(2) | No | ISO 3166-1 alpha-2 |
| `issuer_name` | String(100) | No | Issuing bank name |
| `is_commercial` | Boolean | No | Corporate/purchasing card flag |
| `is_prepaid` | Boolean | No | Prepaid/gift card flag |
| `token_requestor_id` | String(11) | No | For network tokenization (Apple Pay, etc.) |

---

### 3. Merchant
**Purpose**: Merchant/acceptor information for risk assessment.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `merchant_id` | String(50) | Yes | Acquirer-assigned MID |
| `merchant_name` | String(200) | Yes | DBA name |
| `merchant_category` | String(4) | Yes | MCC code |
| `mcc_description` | String(100) | No | Human-readable MCC description |
| `merchant_location` | Address | Yes | Physical location |
| `website_url` | String(500) | No | Merchant website |
| `merchant_age_days` | Integer | No | Days since first transaction seen |
| `risk_score` | Float | No | 0-1 merchant risk score |
| `chargeback_rate_30d` | Float | No | Chargeback ratio (0-1) |
| `refund_rate_30d` | Float | No | Refund ratio (0-1) |
| `avg_ticket_amount` | Decimal | No | Average transaction amount |
| `txn_volume_30d` | Integer | No | Transaction count last 30 days |
| `is_high_risk_mcc` | Boolean | No | Flag for gambling, adult, crypto, etc. |
| `acquirer_id` | String(20) | No | Acquirer identifier |
| `terminal_id` | String(20) | No | Specific terminal/location |

---

### 4. User / Customer
**Purpose**: Aggregated customer profile with rolling window features for behavioral analysis.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID | Yes | Internal customer identifier |
| `external_customer_id` | String(100) | No | Merchant's customer ID |
| `email` | String(255) | No | Primary email |
| `email_age_days` | Integer | No | Days since email first seen |
| `phone` | String(20) | No | Phone number (E.164) |
| `billing_address` | Address | No | Primary billing address |
| `shipping_addresses` | List<Address> | No | Known shipping addresses |
| `cards` | List<CreditCard> | No | Tokenized cards on file |
| `devices` | List<Device> | No | Known devices |
| `created_at` | DateTime | Yes | Account creation timestamp |
| `kyc_level` | Enum | No | `NONE`, `BASIC`, `FULL`, `ENHANCED` |
| `risk_tier` | Enum | No | `LOW`, `MEDIUM`, `HIGH`, `BLOCKED` |

**Rolling Window Features (computed, not stored)**:
| Window | Transaction Count | Amount Sum | Unique Merchants | Unique Countries | Decline Rate |
|--------|-------------------|------------|------------------|------------------|--------------|
| 1 hour | `txn_count_1h` | `amount_sum_1h` | `unique_merchants_1h` | - | - |
| 24 hours | `txn_count_24h` | `amount_sum_24h` | `unique_merchants_24h` | `unique_countries_24h` | `decline_rate_24h` |
| 7 days | `txn_count_7d` | `amount_sum_7d` | - | - | - |
| 30 days | - | - | - | - | `chargeback_rate_30d` |

**Statistical Features**:
- `avg_amount`, `std_amount`, `max_amount`, `min_amount`
- `median_amount`, `amount_skewness`
- `preferred_mcc` - Most frequent merchant category
- `preferred_currency` - Most used currency

---

### 5. Device
**Purpose**: Device intelligence for behavioral biometrics and anomaly detection.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_fingerprint` | String(64) | Yes | Hashed fingerprint (SHA-256) |
| `first_seen` | DateTime | Yes | First observation timestamp |
| `last_seen` | DateTime | Yes | Most recent observation |
| `user_id` | UUID | No | Associated user (if linked) |
| `device_type` | Enum | No | `MOBILE`, `DESKTOP`, `TABLET`, `BOT`, `UNKNOWN` |
| `os` | String(50) | No | Operating system |
| `os_version` | String(20) | No | OS version |
| `browser` | String(50) | No | Browser name |
| `browser_version` | String(20) | No | Browser version |
| `screen_resolution` | String(20) | No | Width x Height |
| `timezone` | String(50) | No | IANA timezone |
| `language` | String(10) | No | Accept-Language header |
| `is_vpn` | Boolean | No | VPN/proxy detected |
| `is_proxy` | Boolean | No | Proxy detected |
| `is_tor` | Boolean | No | Tor exit node detected |
| `is_emulator` | Boolean | No | Emulator/virtual machine detected |
| `is_rooted` | Boolean | No | Rooted/jailbroken device |
| `battery_level` | Integer | No | Battery percentage (mobile) |
| `is_charging` | Boolean | No | Charging status (mobile) |
| `accelerometer_data` | Boolean | No | Motion sensors available |
| `cookie_enabled` | Boolean | No | Cookies enabled |
| `local_storage` | Boolean | No | LocalStorage available |
| `session_count` | Integer | No | Total sessions observed |
| `txn_count` | Integer | No | Transactions from this device |
| `fraud_reports` | Integer | No | Confirmed fraud reports |

---

### 6. Address
**Purpose**: Geographic location for distance calculations and risk scoring.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `street` | String(200) | No | Street address |
| `city` | String(100) | No | City |
| `state` | String(100) | No | State/Province |
| `postal_code` | String(20) | No | ZIP/Postal code |
| `country` | String(2) | Yes | ISO 3166-1 alpha-2 |
| `latitude` | Decimal(9,6) | No | GPS latitude |
| `longitude` | Decimal(9,6) | No | GPS longitude |
| `address_type` | Enum | No | `BILLING`, `SHIPPING`, `IP_GEOLOCATION` |

---

### 7. FraudAlert / Case
**Purpose**: Human review queue for suspicious transactions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `alert_id` | UUID | Yes | Unique alert identifier |
| `transaction_id` | UUID | Yes | Reference to scored transaction |
| `risk_score` | Float | Yes | 0-1 probability of fraud |
| `risk_level` | Enum | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `rule_triggers` | List<RuleTrigger> | Yes | Which rules fired |
| `model_scores` | Dict<String, Float> | No | ML model scores by model name |
| `status` | Enum | Yes | `OPEN`, `IN_REVIEW`, `CONFIRMED_FRAUD`, `FALSE_POSITIVE`, `CLOSED` |
| `assigned_to` | String(100) | No | Analyst identifier |
| `created_at` | DateTime | Yes | Alert creation time |
| `updated_at` | DateTime | Yes | Last modification |
| `reviewed_at` | DateTime | No | Review completion time |
| `reviewer_notes` | Text | No | Analyst notes |
| `resolution` | Enum | No | `FRAUD`, `LEGITIMATE`, `UNABLE_TO_DETERMINE` |
| `chargeback_received` | Boolean | No | Later chargeback confirmation |
| `chargeback_date` | DateTime | No | Chargeback received date |

---

### 8. RuleTrigger
**Purpose**: Individual rule firing details within an alert.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rule_id` | String(50) | Yes | Rule identifier |
| `rule_name` | String(100) | Yes | Human-readable name |
| `rule_category` | Enum | Yes | `VELOCITY`, `GEOGRAPHY`, `AMOUNT`, `MERCHANT`, `DEVICE`, `CARD_TESTING` |
| `triggered_value` | Float | Yes | Value that exceeded threshold |
| `threshold` | Float | Yes | Configured threshold |
| `severity` | Enum | Yes | `INFO`, `WARNING`, `CRITICAL` |
| `description` | String(500) | No | Human-readable explanation |

---

### 9. RiskScore
**Purpose**: Scoring service output for a transaction.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transaction_id` | UUID | Yes | Scored transaction |
| `score` | Float | Yes | 0-1 fraud probability |
| `risk_level` | Enum | Yes | `LOW` (<0.1), `MEDIUM` (0.1-0.5), `HIGH` (0.5-0.9), `CRITICAL` (>0.9) |
| `recommendation` | Enum | Yes | `APPROVE`, `REVIEW`, `DECLINE` |
| `rule_engine_score` | Float | No | Rule-based score (0-1) |
| `ml_model_score` | Float | No | ML model score (0-1) |
| `model_version` | String(50) | No | Model version used |
| `contributing_factors` | List<Factor> | Yes | Top factors driving score |
| `feature_values` | Dict<String, Float> | No | Key feature values at scoring time |
| `latency_ms` | Integer | Yes | Scoring latency |
| `scored_at` | DateTime | Yes | Scoring timestamp |

---

### 10. Factor
**Purpose**: Explainable AI - individual feature contribution to risk score.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `feature_name` | String(100) | Yes | Feature identifier |
| `feature_value` | Float | Yes | Actual value |
| `contribution` | Float | Yes | SHAP/weight value (-1 to 1) |
| `direction` | Enum | Yes | `INCREASES_RISK`, `DECREASES_RISK` |
| `description` | String(200) | No | Human-readable explanation |

---

### 11. Rule / RuleSet
**Purpose**: Configurable rule engine for baseline fraud detection.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rule_id` | String(50) | Yes | Unique rule identifier |
| `name` | String(100) | Yes | Human-readable name |
| `description` | String(500) | No | Detailed description |
| `category` | Enum | Yes | `VELOCITY`, `GEOGRAPHY`, `AMOUNT`, `MERCHANT`, `DEVICE`, `CARD_TESTING`, `CUSTOM` |
| `condition` | String | Yes | Expression (e.g., "txn_count_1h > 10") |
| `threshold` | Float | Yes | Numeric threshold |
| `operator` | Enum | Yes | `GT`, `LT`, `EQ`, `GTE`, `LTE`, `IN`, `NOT_IN` |
| `action` | Enum | Yes | `ALLOW`, `REVIEW`, `BLOCK`, `CHALLENGE_3DS` |
| `severity` | Enum | Yes | `INFO`, `WARNING`, `CRITICAL` |
| `priority` | Integer | Yes | Execution order (lower = first) |
| `enabled` | Boolean | Yes | Active flag |
| `tags` | List<String> | No | Categorization tags |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last modification |
| `created_by` | String(100) | No | Author |
| `performance_stats` | RulePerformance | No | Historical performance |

**RulePerformance** (computed):
- `trigger_count_24h` - Times fired last 24h
- `true_positive_rate` - Confirmed fraud / total triggers
- `false_positive_rate` - False alarms / total triggers
- `avg_risk_score_when_triggered` - Average ML score when rule fires

---

## Enumerations

### EntryMode
- `CNP` - Card Not Present (e-commerce, MOTO)
- `CHIP` - EMV chip contact
- `CONTACTLESS` - NFC/tap
- `MAGSTRIPE` - Magnetic stripe
- `FALLBACK` - Chip fallback to magstripe

### ThreeDSResult
- `ATTEMPTED` - 3DS attempted but not completed
- `AUTHENTICATED` - Successful authentication
- `FAILED` - Authentication failed
- `NOT_ATTEMPTED` - 3DS not offered
- `UNAVAILABLE` - 3DS not supported by issuer

### CardType
- `VISA`
- `MASTERCARD`
- `AMEX`
- `DISCOVER`
- `JCB`
- `DINERS`
- `UNIONPAY`
- `OTHER`

### CardLevel
- `STANDARD`
- `GOLD`
- `PLATINUM`
- `INFINITE` / `SIGNATURE` / `WORLD_ELITE`
- `BUSINESS` / `CORPORATE` / `PURCHASING`
- `PREPAID`
- `UNKNOWN`

### DeviceType
- `MOBILE`
- `DESKTOP`
- `TABLET`
- `BOT` / `CRAWLER`
- `SMART_TV`
- `GAME_CONSOLE`
- `IOT`
- `UNKNOWN`

### AlertStatus
- `OPEN` - Newly created, awaiting review
- `IN_REVIEW` - Analyst assigned
- `CONFIRMED_FRAUD` - Confirmed as fraudulent
- `FALSE_POSITIVE` - Legitimate transaction
- `CLOSED` - Resolved without determination

### RiskLevel
- `LOW` - Score < 0.1
- `MEDIUM` - Score 0.1 - 0.5
- `HIGH` - Score 0.5 - 0.9
- `CRITICAL` - Score > 0.9

### Recommendation
- `APPROVE` - Process normally
- `REVIEW` - Queue for manual review
- `DECLINE` - Reject transaction
- `CHALLENGE_3DS` - Require step-up authentication

### RuleCategory
- `VELOCITY` - Frequency/velocity checks
- `GEOGRAPHY` - Location-based rules
- `AMOUNT` - Amount anomaly rules
- `MERCHANT` - Merchant risk rules
- `DEVICE` - Device fingerprint rules
- `CARD_TESTING` - Card validation patterns
- `CUSTOM` - User-defined rules

### RuleOperator
- `GT` - Greater than
- `GTE` - Greater than or equal
- `LT` - Less than
- `LTE` - Less than or equal
- `EQ` - Equal
- `NEQ` - Not equal
- `IN` - In list
- `NOT_IN` - Not in list
- `BETWEEN` - Range
- `CONTAINS` - String contains

### RuleAction
- `ALLOW` - Pass through
- `REVIEW` - Queue for manual review
- `BLOCK` - Decline transaction
- `CHALLENGE_3DS` - Require 3DS authentication
- `REQUIRE_OTP` - Require one-time password
- `REDUCE_LIMIT` - Temporary limit reduction

---

## Relationships

```
User (1) ─────< (N) CreditCard
User (1) ─────< (N) Device
User (1) ─────< (N) Transaction
User (1) ─────< (N) Address

Merchant (1) ─────< (N) Transaction

Transaction (1) ───── (1) CreditCard
Transaction (1) ───── (1) Merchant
Transaction (1) ───── (1) Device (via fingerprint)
Transaction (1) ───── (1) RiskScore
Transaction (1) ─────< (1) FraudAlert

FraudAlert (1) ─────< (N) RuleTrigger

RuleSet (1) ─────< (N) Rule
```

---

## Implementation Notes

### Storage
- **PostgreSQL** (Supabase): Transactions, Users, Merchants, Alerts, Rules
- **Redis**: Rolling window aggregates, feature store, session cache
- **Object Storage**: Model artifacts, large feature arrays

### API Contracts
All entities should have corresponding Pydantic schemas in `app/domain/schemas.py`:
- `TransactionCreate` - Input for scoring
- `TransactionResponse` - Scored transaction with risk score
- `AlertCreate` / `AlertUpdate` - Review queue operations
- `RuleCreate` / `RuleUpdate` - Rule management

### Indexing Strategy
```sql
-- Critical query paths
CREATE INDEX idx_txn_user_timestamp ON transactions(user_id, timestamp DESC);
CREATE INDEX idx_txn_merchant_timestamp ON transactions(merchant_id, timestamp DESC);
CREATE INDEX idx_txn_card_timestamp ON transactions(card_token, timestamp DESC);
CREATE INDEX idx_txn_device_timestamp ON transactions(device_fingerprint, timestamp DESC);
CREATE INDEX idx_alert_status_created ON fraud_alerts(status, created_at DESC);
CREATE INDEX idx_alert_txn ON fraud_alerts(transaction_id);
```

### Privacy & Compliance
- **Never store**: Full PAN, CVV, untokenized card data
- **PII Handling**: Encrypt email, phone, addresses at rest
- **Retention**: Transaction data 13 months (PCI), Alerts 7 years
- **Right to Delete**: Implement user data purge endpoint

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-18 | Initial domain model from PLAN.md |