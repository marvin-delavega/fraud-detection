# Fraud Detection Backend - Credit Card CNP

## Domain: Credit Card Card-Not-Present Fraud Detection

### Transaction Flow
```
Customer → Merchant → Payment Gateway → Acquirer → Card Network → Issuer → Approve/Decline
                ↑
         Fraud checks happen HERE (or at issuer)
```

---

## Core Fraud Patterns to Detect

| Pattern | Description | Key Features |
|---------|-------------|--------------|
| **Velocity** | Too many transactions in short time | txn_count_1h, txn_count_24h, unique_merchants_1h |
| **Geography** | Impossible travel, high-risk countries | distance_from_last_txn, country_risk_score, ip_country_mismatch |
| **Amount** | Unusually high/low, round numbers | amount_zscore, amount_vs_user_avg, is_round_amount |
| **Merchant** | High-risk MCC, new merchant | mcc_risk_score, merchant_age_days, merchant_category |
| **Device/Behavior** | New device, emulator, VPN | device_fingerprint_match, is_vpn, is_emulator |
| **Card Testing** | Small amounts to validate cards | amount < $5, high decline rate, sequential amounts |

---

## Feature Categories

### Transaction-Level (Raw)
- `amount`, `currency`, `timestamp`, `mcc`
- `merchant_id`, `merchant_name`, `merchant_country`
- `card_bin`, `card_last4`, `card_type`
- `entry_mode`, `pos_condition_code`

### User-Level (Aggregated - Rolling Windows)
- `txn_count_1h/24h/7d`, `amount_sum_1h/24h/7d`
- `unique_merchants_1h/24h`, `unique_countries_24h`
- `avg_amount`, `std_amount`, `max_amount`
- `decline_rate_24h`, `chargeback_rate_30d`

### Cross-Entity (Derived)
- `distance_from_last_txn_km`, `time_since_last_txn_sec`
- `ip_country_vs_card_country`, `ip_distance_from_billing`
- `device_seen_before`, `email_age_days`

---

## ML Approach Roadmap

| Stage | Technique | Target |
|-------|-----------|--------|
| **Baseline** | Rule engine (velocity, geo, amount thresholds) | Quick wins, explainability |
| **v1 Model** | XGBoost/LightGBM on tabular features | AUC-PR > 0.7 |
| **v2 Model** | + Embeddings for merchant, device, BIN | Handle high-cardinality |
| **v3 Model** | + Sequence modeling (RNN/Transformer) | Temporal patterns |
| **Production** | Ensemble + online learning + review queue | Sub-100ms latency |

---

## Key Metrics
- **Precision @ top 1%** - minimize false positives
- **Recall @ 0.1% FPR** - catch fraud at low false alarm rate
- **AUC-ROC / AUC-PR** - overall ranking quality
- **Cost savings** = $ prevented - $ false positive ops cost

---

## Tech Stack
- **API**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase)
- **Cache/Features**: Redis
- **ML**: scikit-learn → XGBoost/LightGBM
- **Monitoring**: Prometheus + Grafana
- **Deployment**: Docker + Docker Compose

---

## Project Structure
```
fraud-detection/
├── app/
│   ├── api/           # FastAPI routes
│   ├── core/          # Config, security
│   ├── domain/        # Models, schemas
│   ├── features/      # Feature engineering
│   ├── ml/            # Model training/serving
│   ├── rules/         # Rule engine
│   └── services/      # Business logic
├── tests/
├── data/              # Sample data, schemas
├── notebooks/         # EDA, model experiments
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── PLAN.md
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Database schema (transactions, users, merchants, alerts)
- [ ] Feature store design (Redis + PostgreSQL)
- [ ] Basic API: ingest transaction, score transaction
- [ ] Rule engine with 5-10 core rules

### Phase 2: ML Pipeline (Week 2)
- [ ] Feature engineering pipeline
- [ ] Training pipeline (offline)
- [ ] Model serving (online, <100ms)
- [ ] A/B testing framework

### Phase 3: Production Hardening (Week 3)
- [ ] Monitoring/alerting (latency, drift, accuracy)
- [ ] Authentication + rate limiting
- [ ] Human review queue
- [ ] Load testing

### Phase 4: Portfolio Polish (Week 4)
- [ ] Documentation (API, architecture, decisions)
- [ ] Demo notebook with results
- [ ] README with architecture diagram
- [ ] CI/CD pipeline

---

## Datasets for Development
1. **Kaggle Credit Card Fraud** - 284k rows, 0.17% fraud (starter)
2. **IEEE-CIS Fraud Detection** - 590k rows, rich features (main)
3. **ULB Credit Card** - European, time-series (sequence models)
4. **Synthetic generator** - For testing edge cases

---

## Success Criteria
- [ ] API responds <50ms p99 for scoring
- [ ] Model AUC-PR > 0.7 on holdout
- [ ] Rule engine catches known patterns
- [ ] End-to-end demo with synthetic data
- [ ] Clean code, tests, documentation