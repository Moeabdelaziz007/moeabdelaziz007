# Zakat Calculator Skill Specification

## Skill Metadata
- **Name**: Zakat Calculator
- **Slug**: `zakat-calculator`
- **Version**: 1.0.0
- **Category**: Finance / Islamic Finance
- **Language**: Arabic (primary) / English (secondary)
- **Tags**: [zakat, islamic-finance, hijri, finance, calculator, ramadan]
- **Author**: PAI Universe
- **License**: MIT

## Skill Description
A comprehensive Zakat calculator that computes obligatory alms (Zakat) according to Islamic law. Supports multiple schools of thought (Hanafi, Shafi'i, Maliki, Hanbali), handles multiple asset types (gold, silver, cash, stocks, crypto, business inventory), integrates with Hijri calendar for Nisab calculation, and supports Pi Network payments for Zakat distribution.

## Features

### Core Calculation Engine
- **Nisab Calculation**: Dynamic Nisab based on current gold/silver prices (configurable API)
- **Madhhab Support**: Hanafi (gold standard), Shafi'i/Maliki/Hanbali (silver standard)
- **Asset Categories**:
  - Cash & Bank Balances
  - Gold & Silver (jewelry, bullion, coins)
  - Investment Assets (stocks, ETFs, mutual funds)
  - Cryptocurrency holdings
  - Business Inventory/Stock
  - Agricultural Produce
  - Livestock
  - Debts Receivable (money owed to you)
- **Liability Deduction**: Debts owed, immediate expenses
- **Hawl (Lunar Year) Tracking**: Hijri calendar integration

### Arabic-Native Features
- **RTL UI** with full Arabic localization
- **Hijri Calendar Integration**: Nisab dates, Zakat due dates on Hijri calendar
- **Arabic Numerals**: Display amounts in Eastern Arabic numerals (٠١٢٣٤٥٦٧٨٩)
- **Hijri Date Picker**: Select dates via Hijri calendar
- **Arabic Number Formatting**: Indian numerals (٠١٢٣٤٥٦٧٨٩), proper currency formatting
- **RTL UI Layout**: Full RTL support for Arabic interface

### Islamic Finance Compliance
- **Madhhab Selector**: Hanafi (default), Shafi'i, Maliki, Hanbali
- **Nisab Source**: Gold (85g) / Silver (595g) - configurable
- **Price Feeds**: Gold/Silver price API integration (configurable)
- **Scholar Review Mode**: Flag for scholar review before distribution

### Pi Network Integration
- **Pi Payment**: Pay Zakat directly in Pi
- **Pi KYC Verification**: Recipient verification via Pi KYC
- **ACP Marketplace Listing**: Publish as paid/free skill on Virtuals ACP
- **Pi Payment Flow**: User pays Zakat in Pi → ACP settles in USDC → Distributed to verified recipients

### Advanced Features
- **Multi-Currency Support**: SAR, AED, EGP, USD, EUR, etc.
- **Portfolio Tracking**: Track Zakat-eligible assets year-round
- **Hawl Reminders**: Hijri calendar notifications when Hawl completes
- **Scholar Review Workflow**: Optional scholar approval before distribution
- **Distribution Channels**: Direct transfer, charity orgs, local mosques
- **Audit Trail**: Full calculation history with TrustChain logging

## Technical Specification

### Input Schema
```json
{
  "assets": {
    "cash": {"amount": 10000, "currency": "SAR"},
    "gold": {"grams": 100, "purity": 24},
    "silver": {"grams": 500, "purity": 925},
    "crypto": [{"symbol": "BTC", "amount": 0.5, "currency": "USD"}],
    "stocks": [{"symbol": "2222.SR", "shares": 100, "price": 45.50}],
    "business_inventory": {"value": 50000, "currency": "SAR"},
    "receivables": {"amount": 5000, "currency": "SAR"}
  },
  "liabilities": {
    "debts": 5000,
    "immediate_expenses": 2000
  },
  "settings": {
    "madhhab": "hanafi",
    "nisab_basis": "gold",
    "gold_price_per_gram": 280.50,
    "silver_price_per_gram": 3.20,
    "hijri_year": 1446
  }
}
```

### Output Schema
```json
{
  "zakat_due": 2850.75,
  "currency": "SAR",
  "breakdown": {
    "cash": 250.00,
    "gold": 2520.00,
    "silver": 48.75,
    "crypto": 45.00,
    "stocks": 37.50,
    "business_inventory": 0
  },
  "nisab_threshold": 85.0,
  "total_assets": 114030.00,
  "total_liabilities": 7000.00,
  "net_zakatable": 107030.00,
  "hijri_due_date": "1447-09-15",
  "gregorian_due_date": "2025-03-15",
  "hijri_year": 1446,
  "calculation_timestamp": "2025-01-15T10:30:00Z",
  "madhhab": "hanafi",
  "nisab_used": "gold_85g",
  "gold_price_per_gram": 280.50,
  "scholar_review_required": false
}
```

## Skill Manifest (clawHub-AR Format)
```yaml
---
name: "Zakat Calculator"
slug: "zakat-calculator"
version: "1.0.0"
description: "Comprehensive Zakat calculator with multi-madhhab support, Hijri calendar, and Pi Network payments"
author: "PAI Universe"
license: "MIT"
category: "finance/islamic-finance"
tags: [zakat, islamic-finance, hijri, calculator, finance, ramadan]
languages: ["ar", "en"]
rtl: true
languages_primary: "ar"
models:
  - "jais-30b"
  - "allam-7b"
  - "acegpt-13b"
capabilities:
  - "zakat-calculation"
  - "hijri-calendar"
  - "arabic-numerals"
  - "pi-payments"
  - "islamic-finance"
requirements:
  - "gold-price-api"
  - "silver-price-api"
  - "hijri-calendar"
  - "pi-network-sdk"
pricing:
  model: "freemium"
  free_tier: "basic_calculation"
  paid_tiers:
    - name: "pro"
      price: "10 PI/month"
      features: ["multi-portfolio", "hawl-tracking", "scholar-review", "pi-payments"]
    - name: "enterprise"
      price: "100 PI/month"
      features: ["api-access", "white-label", "scholar-review", "api-access"]
acp_listing:
  enabled: true
  price_pi: 5
  category: "finance"
  tags: ["zakat", "islamic-finance", "arabic", "hijri"]
---
```

## API Endpoints (for ACP Deployment)
```
POST   /api/v1/zakat/calculate     # Calculate Zakat
GET    /api/v1/zakat/nisaab        # Current Nisab values
GET    /api/v1/zakat/hijri-date    # Current Hijri date
POST   /api/v1/zakat/portfolio     # Portfolio analysis
POST   /api/v1/zakat/pay           # Initiate Pi payment
GET    /api/v1/zakat/history       # Calculation history
POST   /api/v1/zakat/scholar-review Request scholar review
```

## Deployment Checklist
- [ ] Skill manifest created
- [ ] Arabic UI/RTL implemented
- [ ] Hijri calendar integration
- [ ] Jais/ALLaM model integration for Arabic responses
- [ ] Gold/Silver price API integration
- [ ] Hijri calendar integration
- [ ] Pi Network SDK integration
- [ ] ClawHub-AR skill manifest created
- [ ] ACP marketplace listing created
- [ ] Pi payment flow tested
- [ ] Documentation (Arabic/English)
- [ ] Schema validation tests
- [ ] Unit tests for calculation engine
- [ ] E2E tests for payment flow

---

## Next Steps
1. **Implement calculation engine** (TypeScript/Rust)
2. **Build Arabic UI** (React/Next.js with RTL)
3. **Integrate Jais/ALLaM for Arabic responses**
4. **Deploy to ClawHub-AR registry**
5. **List on Virtuals ACP**
6. **Test Pi payment flow**

---

## Ready to start implementation. Which component first?
1. Calculation engine (core logic)
2. Arabic UI (React/Next.js with RTL)
3. API endpoints (FastAPI/Next.js)
4. ClawHub-AR manifest
5. ACP deployment config