# report_generator.py
import pandas as pd
import numpy as np
from datetime import datetime
import os
from pathlib import Path
from RiskVisualization import RiskVisualizer

class ReportGenerator:
    def __init__(self, data_path='output/btc_raw_data.csv'):
        """Initialize report generator"""
        self.output_dir = 'output/report/'
        self.figures_dir = 'output/figures/'
        
        # Create output directories
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.visualizer = RiskVisualizer(data_path)
        self.data = pd.read_csv(data_path)
    
    def generate_report(self):
        """Generate analysis report with visualizations"""
        print("Generating visualizations...")
        self.visualizer.generate_all_plots()
        
        # Calculate metrics
        returns = pd.Series(self.data['Returns']).dropna()
        volatility = returns.std() * np.sqrt(252)
        var_95 = returns.quantile(0.05)
        var_99 = returns.quantile(0.01)
        
        print("Generating report...")
        markdown_content = f"""# Bitcoin Risk Analysis Report for Yala Protocol
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Market Analysis

### Price and Volatility Trends
![Price and Volatility](../figures/price_and_volatility.png)

The above graph shows Bitcoin's price history and its 30-day rolling volatility. Key observations:
- Current annualized volatility: {volatility:.2%}
- Historical price patterns show cyclical volatility regimes

### Volatility Regime Analysis
![Volatility Regimes](../figures/volatility_regimes.png)

The volatility regime analysis identifies three distinct market states:
- Low volatility: < {volatility*0.7:.2%}
- Medium volatility: {volatility*0.7:.2%} - {volatility*1.3:.2%}
- High volatility: > {volatility*1.3:.2%}

## 2. Risk Analysis

### Return Distribution
![Return Distribution](../figures/return_distribution.png)

Key risk metrics:
- Value at Risk (95%): {var_95:.2%}
- Value at Risk (99%): {var_99:.2%}
- Annualized Volatility: {volatility:.2%}

### Drawdown Analysis
![Drawdown Analysis](../figures/drawdown_analysis.png)

### Recovery Patterns
![Recovery Patterns](../figures/recovery_patterns.png)

The analysis of recovery patterns shows:
- Median recovery time after significant drops
- Pattern of price rebounds
- Typical recovery trajectories

## 3. Protocol Parameters

### Interest Rate Model
![Interest Rate Model](../figures/interest_rate_model.png)

Recommended protocol parameters:
- Initial LTV: {min(0.8, 1/(1 + volatility)):.2%}
- Liquidation threshold: {min(0.85, 1/(1 + volatility * 0.8)):.2%}
- Base interest rate: {max(0.03, volatility * 0.5):.2%}

## 4. Risk Management Recommendations

1. Dynamic Parameters
   - Adjust LTV based on volatility regimes
   - Implement graduated liquidation thresholds
   - Use adaptive interest rates

2. Risk Monitoring
   - Track volatility regime changes
   - Monitor drawdown patterns
   - Analyze recovery metrics

3. Safety Measures
   - Multi-stage liquidation process
   - Grace period for margin calls
   - Emergency circuit breakers
"""
        
        # Save report
        report_path = os.path.join(self.output_dir, 'risk_analysis_report.md')
        with open(report_path, 'w') as f:
            f.write(markdown_content)
        print(f"Report saved to {report_path}")

def main():
    generator = ReportGenerator()
    generator.generate_report()

if __name__ == "__main__":
    main()