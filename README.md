# Yala Protocol - Bitcoin Risk Analysis System

## Table of Contents

- [About Yala Protocol](#about-yala-protocol)
- [Installation](#installation)
- [Usage](#usage)
- [System Architecture](#system-architecture)
- [API Reference](#api-reference)
- [Contributing](#contributing)

## About Yala Protocol

Yala is a decentralized Bitcoin-backed stablecoin lending protocol that allows users to obtain stablecoin loans using BTC as collateral. The protocol features advanced risk management and a flexible liquidation system.

### Key Features

* **Bitcoin-Backed Loans**
  - Use BTC as collateral
  - Borrow stablecoins against your BTC
  - Flexible loan terms

* **Risk Management**
  - Dynamic LTV ratios
  - Multi-stage liquidation process
  - Real-time risk monitoring

* **Protocol Parameters**
  - Initial LTV: Up to 80%
  - Liquidation Threshold: 90%
  - Repayment Window: 5 days
  - Minimum Collateral: 0.1 BTC

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/yala-risk.git
cd yala-risk
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Data Preparation
```bash
python DataPrep.py
```

### Risk Analysis
```bash
python RiskAnalysis.py
```

### Visualization
```bash
python RiskVisualization.py
```

### Start API Service
```bash
python api_service.py
```

## System Architecture

### Risk Assessment Flow

1. **Data Collection**
   - Bitcoin price feeds
   - Market indicators
   - Volume analysis

2. **Risk Analysis**
   - Volatility calculation
   - Machine learning predictions
   - Market regime detection

3. **Protocol Actions**
   - LTV adjustments
   - Interest rate updates
   - Liquidation triggers

### Liquidation Process

| Stage | LTV Threshold | Action | Time Window |
|-------|--------------|---------|-------------|
| Warning | 80% | Notification | Immediate |
| Margin Call | 85% | Partial Liquidation | 5 days |
| Liquidation | 90% | Full Liquidation | Immediate |

## API Reference

### Risk Prediction Endpoint

```http
POST /api/v1/predict/risk
```

#### Request Body
```json
{
    "timestamp": "2024-01-16T10:00:00",
    "btc_price": 45000.0,
    "collateral": 1.5,
    "loan_amount": 50000
}
```

#### Response
```json
{
    "risk_level": "medium",
    "recommended_ltv": 0.75,
    "liquidation_price": 42000.0,
    "warnings": []
}
```

### Model Info Endpoint

```http
GET /api/v1/model/info
```

## Contact

Your Name - [@vickyfu09](https://x.com/VickyFu09)


## Acknowledgements

* Bitcoin price data from Yahoo Finance