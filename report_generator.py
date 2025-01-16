# report_generator.py
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import os
from RiskVisualization import RiskVisualizer
from MLModel import BitcoinRiskModel
from RiskAnalysis import LendingRiskAnalyzer

class ReportGenerator:
    def __init__(self, data_path='output/btc_raw_data.csv'):
        """Initialize report generator with data and analysis tools"""
        self.data_path = data_path
        self.output_dir = 'output/report/'
        self.figures_dir = os.path.join(self.output_dir, 'figures')
        
        # Create output directories
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize analysis components
        self.visualizer = RiskVisualizer(data_path)
        self.risk_analyzer = LendingRiskAnalyzer(data_path)
        self.ml_model = BitcoinRiskModel(data_path)
        
        # Load data
        self.data = pd.read_csv(data_path, index_col='Date', parse_dates=True)
    
    def generate_market_analysis(self):
        """Generate market analysis section"""
        # Calculate key metrics
        current_price = self.data['Close'].iloc[-1]
        all_time_high = self.data['High'].max()
        daily_returns = self.data['Close'].pct_change()
        volatility = daily_returns.std() * np.sqrt(252)
        
        # Generate volatility analysis
        vol_analysis = self.risk_analyzer.analyze_volatility_regimes()
        
        market_analysis = f"""## 1. Market Analysis

### 1.1 Current Market State
- Current BTC Price: ${current_price:,.2f}
- Distance from ATH: {((current_price/all_time_high - 1) * 100):.2f}%
- 30-Day Volatility: {volatility:.2%}

### 1.2 Volatility Regimes
{vol_analysis}

![Volatility Analysis](figures/volatility_regimes.png)
"""
        return market_analysis

    def generate_risk_metrics(self):
        """Generate risk metrics section"""
        risk_metrics = self.risk_analyzer.calculate_risk_metrics()
        
        risk_section = f"""## 2. Risk Metrics

### 2.1 Value at Risk Analysis
- Daily VaR (95%): {risk_metrics['var_95']:.2%}
- Daily VaR (99%): {risk_metrics['var_99']:.2%}
- Expected Shortfall: {risk_metrics['cvar_95']:.2%}

### 2.2 Drawdown Analysis
- Maximum Drawdown: {risk_metrics['max_drawdown']:.2%}
- Average Recovery Time: {risk_metrics['avg_recovery_days']:.1f} days

![Drawdown Analysis](figures/drawdown_analysis.png)
"""
        return risk_section

    def generate_ml_insights(self):
        """Generate machine learning insights section"""
        # Train models and get predictions
        self.ml_model.train_models()
        predictions = self.ml_model.analyze_risk_parameters()
        
        ml_section = f"""## 3. Machine Learning Insights

### 3.1 Risk Classification
- Model Accuracy: {predictions['model_metrics']['accuracy']:.2%}
- Precision (High Risk): {predictions['model_metrics']['precision']:.2%}
- Recall (High Risk): {predictions['model_metrics']['recall']:.2%}

### 3.2 Key Risk Indicators
{predictions['risk_indicators']}

![Return Distribution](figures/return_distribution.png)
"""
        return ml_section

    def generate_protocol_recommendations(self):
        """Generate protocol recommendations section"""
        params = self.risk_analyzer.analyze_liquidation_parameters()
        
        recommendations = f"""## 4. Protocol Recommendations

### 4.1 Recommended Parameters
- Initial LTV: {params['recommended_initial_ltv']:.2%}
- Liquidation Threshold: {params['liquidation_threshold']:.2%}
- Grace Period: {params['recommended_grace_period']} days

### 4.2 Interest Rate Model
- Base Rate: {params['base_rate']:.2%}
- Optimal Utilization: {params['optimal_utilization']:.2%}
- Maximum Rate: {params['max_rate']:.2%}

![Interest Rate Model](figures/interest_rate_model.png)
"""
        return recommendations

    def generate_report(self):
        """Generate complete analysis report"""
        print("Generating report...")
        
        # Generate visualizations
        print("Creating visualizations...")
        self.visualizer.generate_all_plots()
        
        # Compile report sections
        report_content = f"""# Bitcoin Risk Analysis Report for Yala Protocol
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{self.generate_market_analysis()}

{self.generate_risk_metrics()}

{self.generate_ml_insights()}

{self.generate_protocol_recommendations()}
"""
        
        # Save report
        report_path = os.path.join(self.output_dir, 'risk_analysis_report.md')
        with open(report_path, 'w') as f:
            f.write(report_content)
            
        print(f"Report saved to {report_path}")
        
        # Also save as HTML for better visualization
        try:
            import markdown
            html_content = markdown.markdown(report_content)
            html_path = os.path.join(self.output_dir, 'risk_analysis_report.html')
            
            with open(html_path, 'w') as f:
                f.write(f"""
                <html>
                <head>
                    <title>Bitcoin Risk Analysis Report</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        img {{ max-width: 100%; height: auto; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """)
            print(f"HTML report saved to {html_path}")
            
        except ImportError:
            print("markdown package not installed. Skipping HTML generation.")

def main():
    generator = ReportGenerator()
    generator.generate_report()

if __name__ == "__main__":
    main()