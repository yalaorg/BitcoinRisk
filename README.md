# Yala Protocol - Bitcoin Risk Analysis System

## Table of Contents

- [About Yala Protocol](#about-yala-protocol)
- [Installation](#installation)
- [Machine Learning](#Machine-Learning-Models)
- [System Architecture](#system-architecture)

## About Yala Protocol

Yala is a decentralized Bitcoin-backed stablecoin lending protocol that allows users to obtain stablecoin loans using BTC as collateral. The protocol features advanced risk management and a flexible liquidation system.

### Key Features

* **Bitcoin-Backed Loans**
  - Use BTC as collateral
  - Borrow stablecoins against BTC
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


## Machine Learning Models

### Risk Classification Model
- Type: Random Forest Classifier
- Features: 
  * Price momentum indicators
  * Volatility metrics
  * Volume indicators
  * Technical analysis signals
- Target Variables:
  * Risk level (Low/Medium/High)
  * Price direction prediction
  * Volatility regime classification

### Volatility Prediction Model
- Type: Gradient Boosting Regressor
- Features:
  * Historical volatility patterns
  * Market regime indicators
  * Trading volume metrics
- Predictions:
  * Forward-looking volatility
  * Risk regime transitions
  * Market stress indicators

### Model Training
```bash
python MLModel.py train --data-path data/bitcoin_history.csv
```

### Model Inference
```bash
python MLModel.py predict --input-data current_market.csv
```

## Risk Analysis

### Visualization Tools
```bash
python RiskVisualization.py
```
Generates the following plots:
- Price and volatility trends
- Drawdown analysis
- Return distribution
- Recovery patterns
- Interest rate model
- Volatility regimes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yalaorg/BitcoinRisk.git
cd BitcoinRisk
```

2. Install dependencies:
```bash
pip install -r requirements.txt
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
    "btc_price": 90000.0,
    "collateral": 1.5,
    "loan_amount": 60000
}
```

#### Response
```json
{
    "risk_level": "medium",
    "recommended_ltv": 0.75,
    "liquidation_price": 67500.0,
    "warnings": []
}
```

### Model Info Endpoint

```http
GET /api/v1/model/info
```

## Contact

Dev - [@vickyfu09](https://x.com/VickyFu09)


## Acknowledgements

* Bitcoin price data from Yahoo Finance
