# RiskVisualization.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime, timedelta

class RiskVisualizer:
    def __init__(self, csv_path='output/btc_raw_data.csv'):
        """Initialize visualizer with data"""
        self.data = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
        self.output_dir = 'output/figures/'
        import os
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def plot_price_and_volatility(self):
        """Plot price trend and volatility"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[2, 1])
        
        # Price plot
        ax1.plot(self.data.index, self.data['Close'], 'b-', label='BTC Price')
        ax1.set_title('Bitcoin Price History', fontsize=12)
        ax1.set_ylabel('Price (USD)', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=10)
        
        # Volatility plot
        rolling_vol = self.data['Returns'].rolling(window=30).std() * np.sqrt(252)
        ax2.plot(self.data.index, rolling_vol, 'r-', label='30-Day Volatility')
        ax2.set_title('Historical Volatility (30-Day)', fontsize=12)
        ax2.set_ylabel('Annualized Volatility', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}price_and_volatility.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_drawdown_analysis(self):
        """Plot drawdown patterns"""
        fig, ax = plt.subplots(figsize=(15, 7))
        
        # Calculate drawdown
        rolling_max = self.data['Close'].expanding().max()
        drawdown = (self.data['Close'] - rolling_max) / rolling_max
        
        ax.fill_between(self.data.index, drawdown, 0, color='red', alpha=0.3)
        ax.plot(self.data.index, drawdown, 'r-', label='Drawdown')
        
        ax.set_title('Bitcoin Historical Drawdown', fontsize=12)
        ax.set_ylabel('Drawdown %', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}drawdown_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_return_distribution(self):
        """Plot return distribution and VaR"""
        returns = self.data['Returns'].dropna()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Returns histogram
        ax1.hist(returns, bins=50, density=True, alpha=0.75, color='blue')
        ax1.axvline(returns.quantile(0.05), color='red', linestyle='--', 
                   label='VaR (95%)')
        ax1.axvline(returns.quantile(0.01), color='darkred', linestyle='--', 
                   label='VaR (99%)')
        ax1.set_title('Distribution of Daily Returns', fontsize=12)
        ax1.set_xlabel('Daily Return', fontsize=10)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # QQ plot
        stats.probplot(returns, dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot of Returns', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}return_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_recovery_patterns(self):
        """Plot recovery patterns after significant drops"""
        returns = self.data['Returns'].dropna()
        significant_drops = returns < returns.quantile(0.05)
        
        # Get recovery patterns
        recovery_paths = []
        window = 30
        
        for i in range(len(self.data) - window):
            if significant_drops.iloc[i]:
                initial_price = self.data['Close'].iloc[i]
                recovery_series = self.data['Close'].iloc[i:i+window] / initial_price - 1
                recovery_paths.append(recovery_series)
        
        if recovery_paths:
            fig, ax = plt.subplots(figsize=(15, 7))
            
            for path in recovery_paths[:20]:  # Plot first 20 patterns
                ax.plot(range(len(path)), path, alpha=0.2, color='gray')
                
            # Plot median recovery path
            median_path = pd.DataFrame(recovery_paths).median()
            ax.plot(range(len(median_path)), median_path, 'b-', 
                   linewidth=2, label='Median Recovery')
            
            ax.set_title('Price Recovery Patterns After Significant Drops', fontsize=12)
            ax.set_xlabel('Days After Drop', fontsize=10)
            ax.set_ylabel('Return from Bottom', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10)
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}recovery_patterns.png', dpi=300, bbox_inches='tight')
            plt.close()
            
    def plot_interest_rate_model(self):
        """Plot interest rate model based on utilization"""
        utilization = np.linspace(0, 1, 100)
        
        # Calculate interest rates
        optimal_utilization = 0.8
        base_rate = 0.03 + self.data['Returns'].std() * np.sqrt(252) * 0.5
        max_rate = base_rate * 3
        
        rates = []
        for u in utilization:
            if u <= optimal_utilization:
                rate = base_rate * u * 2 / optimal_utilization
            else:
                slope = (max_rate - base_rate * 2) / (1 - optimal_utilization)
                rate = base_rate * 2 + slope * (u - optimal_utilization)
            rates.append(rate)
            
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(utilization * 100, np.array(rates) * 100, 'b-')
        ax.axvline(optimal_utilization * 100, color='r', linestyle='--', 
                  label='Optimal Utilization')
        
        ax.set_title('Interest Rate Model', fontsize=12)
        ax.set_xlabel('Utilization (%)', fontsize=10)
        ax.set_ylabel('Interest Rate (%)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}interest_rate_model.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_volatility_regimes(self):
        """Plot volatility regimes"""
        vol = self.data['Returns'].rolling(window=30).std() * np.sqrt(252)
        vol_percentiles = vol.quantile([0.33, 0.67])
        
        fig, ax = plt.subplots(figsize=(15, 7))
        
        ax.plot(self.data.index, vol, 'b-', label='30-Day Volatility')
        ax.axhline(vol_percentiles[0.33], color='g', linestyle='--', label='Low/Medium Threshold')
        ax.axhline(vol_percentiles[0.67], color='r', linestyle='--', label='Medium/High Threshold')
        
        ax.set_title('Volatility Regimes', fontsize=12)
        ax.set_ylabel('Annualized Volatility', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}volatility_regimes.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def generate_all_plots(self):
        """Generate all visualization plots"""
        print("Generating visualizations...")
        self.plot_price_and_volatility()
        print("1. Price and Volatility plot generated")
        self.plot_drawdown_analysis()
        print("2. Drawdown Analysis plot generated")
        self.plot_return_distribution()
        print("3. Return Distribution plot generated")
        self.plot_recovery_patterns()
        print("4. Recovery Patterns plot generated")
        self.plot_interest_rate_model()
        print("5. Interest Rate Model plot generated")
        self.plot_volatility_regimes()
        print("6. Volatility Regimes plot generated")
        print(f"\nAll plots saved in {self.output_dir}")

def main():
    visualizer = RiskVisualizer()
    visualizer.generate_all_plots()

if __name__ == "__main__":
    main()