# RiskAnalysis.py
import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class LendingRiskAnalyzer:
    def __init__(self, csv_path='output/btc_raw_data.csv'):
        """Initialize risk analyzer with historical data"""
        self.data = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
        self.analysis_results = {}
        
    def analyze_liquidation_parameters(self, confidence_level=0.99):
        """Determine optimal liquidation parameters"""
        # Calculate returns for different time windows
        windows = [1, 3, 5, 7, 14, 30]
        moves_by_window = {}
        
        for window in windows:
            rolling_returns = self.data['Close'].pct_change(window).dropna()
            moves_by_window[window] = {
                'max_drop': rolling_returns.min(),
                'var': rolling_returns.quantile(1 - confidence_level),
                'std': rolling_returns.std()
            }
        
        # Calculate optimal initial LTV
        daily_returns = self.data['Close'].pct_change().dropna()
        worst_daily_move = daily_returns.min()
        var_daily = daily_returns.quantile(1 - confidence_level)
        
        # Determine initial LTV with safety buffer
        recommended_ltv = 1 / (1 - worst_daily_move) * 0.8  # 20% safety buffer
        recommended_ltv = min(recommended_ltv, 0.8)  # Cap at 80%
        liquidation_threshold = recommended_ltv * 0.9  # 10% buffer from initial LTV
        
        self.analysis_results['liquidation_params'] = {
            'recommended_initial_ltv': recommended_ltv,
            'liquidation_threshold': liquidation_threshold,
            'max_daily_drop': worst_daily_move,
            'var_daily': var_daily,
            'moves_by_window': moves_by_window
        }
        
        return self.analysis_results['liquidation_params']
    
    def analyze_repayment_windows(self, default_window=5):
        """Analyze optimal repayment windows"""
        returns = self.data['Returns'].dropna()
        significant_drops = returns < returns.quantile(0.05)
        recovery_periods = []
        
        # Convert index to numeric for easier calculation
        numeric_index = pd.Series(range(len(self.data)), index=self.data.index)
        
        for i in range(len(self.data) - 30):
            if significant_drops.iloc[i]:
                initial_price = self.data['Close'].iloc[i]
                recovery_slice = self.data['Close'].iloc[i:i+30]
                recovery_series = recovery_slice / initial_price - 1
                
                if (recovery_series > 0).any():
                    first_recovery = recovery_series[recovery_series > 0].index[0]
                    days_to_recover = (numeric_index[first_recovery] - 
                                     numeric_index[recovery_series.index[0]])
                else:
                    days_to_recover = 30
                    
                recovery_periods.append(days_to_recover)
        
        recovery_periods = pd.Series(recovery_periods)
        
        self.analysis_results['repayment_windows'] = {
            'recommended_window': min(default_window, int(recovery_periods.median())),
            'median_recovery': recovery_periods.median(),
            'p90_recovery': recovery_periods.quantile(0.9),
            'max_recovery': recovery_periods.max()
        }
        
        return self.analysis_results['repayment_windows']
    
    def analyze_interest_rates(self, risk_free_rate=0.03):
        """Determine optimal interest rate parameters"""
        annual_vol = self.data['Returns'].std() * np.sqrt(252)
        base_rate = risk_free_rate + annual_vol * 0.5
        optimal_utilization = 0.8
        max_rate = base_rate * 3
        
        self.analysis_results['interest_params'] = {
            'base_rate': base_rate,
            'optimal_utilization': optimal_utilization,
            'max_rate': max_rate,
            'slope_1': (base_rate * 2) / optimal_utilization,
            'slope_2': (max_rate - base_rate * 2) / (1 - optimal_utilization)
        }
        
        return self.analysis_results['interest_params']
    
    def analyze_risk_parameters(self):
        """Analyze all risk parameters and generate recommendations"""
        liquidation_params = self.analyze_liquidation_parameters()
        repayment_windows = self.analyze_repayment_windows()
        interest_params = self.analyze_interest_rates()
        
        self.generate_report()
        
        return {
            'liquidation_params': liquidation_params,
            'repayment_windows': repayment_windows,
            'interest_params': interest_params
        }
    
    def generate_report(self):
        """Generate and save detailed risk analysis report"""
        try:
            with open('output/lending_risk_analysis.txt', 'w') as f:
                f.write("Lending Protocol Risk Analysis Report\n")
                f.write(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                # Liquidation Parameters
                f.write("LIQUIDATION PARAMETERS\n")
                f.write("-" * 30 + "\n")
                liq_params = self.analysis_results['liquidation_params']
                f.write(f"Recommended Initial LTV: {liq_params['recommended_initial_ltv']:.2%}\n")
                f.write(f"Liquidation Threshold: {liq_params['liquidation_threshold']:.2%}\n")
                f.write(f"Maximum Daily Drop: {liq_params['max_daily_drop']:.2%}\n")
                f.write(f"Daily VaR (99%): {liq_params['var_daily']:.2%}\n\n")
                
                # Time Windows Analysis
                f.write("PRICE MOVEMENT BY TIME WINDOW\n")
                f.write("-" * 30 + "\n")
                for window, metrics in liq_params['moves_by_window'].items():
                    f.write(f"{window}-Day Window:\n")
                    f.write(f"  Max Drop: {metrics['max_drop']:.2%}\n")
                    f.write(f"  VaR (99%): {metrics['var']:.2%}\n")
                    f.write(f"  Std Dev: {metrics['std']:.2%}\n\n")
                
                # Repayment Windows
                f.write("REPAYMENT WINDOWS\n")
                f.write("-" * 30 + "\n")
                rep_windows = self.analysis_results['repayment_windows']
                f.write(f"Recommended Window: {rep_windows['recommended_window']} days\n")
                f.write(f"Median Recovery Time: {rep_windows['median_recovery']:.1f} days\n")
                f.write(f"90th Percentile Recovery: {rep_windows['p90_recovery']:.1f} days\n")
                f.write(f"Maximum Recovery Time: {rep_windows['max_recovery']:.1f} days\n\n")
                
                # Interest Rate Parameters
                f.write("INTEREST RATE PARAMETERS\n")
                f.write("-" * 30 + "\n")
                int_params = self.analysis_results['interest_params']
                f.write(f"Base Rate: {int_params['base_rate']:.2%}\n")
                f.write(f"Optimal Utilization: {int_params['optimal_utilization']:.2%}\n")
                f.write(f"Maximum Rate: {int_params['max_rate']:.2%}\n")
                f.write(f"Slope 1 (0 to optimal): {int_params['slope_1']:.4f}\n")
                f.write(f"Slope 2 (optimal to max): {int_params['slope_2']:.4f}\n")
                
            print("Risk analysis report saved to output/lending_risk_analysis.txt")
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")

def main():
    # Initialize analyzer
    analyzer = LendingRiskAnalyzer()
    
    # Run analysis
    results = analyzer.analyze_risk_parameters()
    
    # Print key recommendations
    print("\nKey Protocol Parameters:")
    print("-" * 30)
    print(f"Initial LTV: {results['liquidation_params']['recommended_initial_ltv']:.2%}")
    print(f"Liquidation Threshold: {results['liquidation_params']['liquidation_threshold']:.2%}")
    print(f"Recommended Repayment Window: {results['repayment_windows']['recommended_window']} days")
    print(f"Base Interest Rate: {results['interest_params']['base_rate']:.2%}")

if __name__ == "__main__":
    main()