# DataPrep.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class BitcoinDataLoader:
    def __init__(self, symbol="BTC-USD"):
        self.symbol = symbol
        self.data = None
        self.ticker = yf.Ticker(symbol)
        
    def fetch_data(self, period="max", interval="1d"):
        try:
            df = self.ticker.history(period=period, interval=interval)
            
            if df.empty:
                print(f"No data returned for {self.symbol}")
                return None
            
            # Calculate metrics
            df['Returns'] = df['Close'].pct_change()
            df['Log_Returns'] = np.log(df['Close']/df['Close'].shift(1))
            df['Volatility'] = df['Returns'].rolling(window=30).std() * np.sqrt(252)
            df['Rolling_Max'] = df['Close'].expanding().max()
            df['Drawdown'] = (df['Close'] - df['Rolling_Max']) / df['Rolling_Max']
            df['Volume_MA'] = df['Volume'].rolling(window=30).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
            
            self.data = df
            return df
            
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return None
    
    def save_data_and_report(self):
        """Save raw data to CSV and analysis to text file"""
        if self.data is None or self.data.empty:
            print("No data available to save.")
            return
            
        try:
            # Create output directory if it doesn't exist
            if not os.path.exists('output'):
                os.makedirs('output')
            
            # Save raw data to CSV
            csv_path = 'output/btc_raw_data.csv'
            self.data.to_csv(csv_path)
            print(f"Raw data saved to {csv_path}")
            
            # Generate and save report
            report_path = 'output/btc_analysis_report.txt'
            with open(report_path, 'w') as f:
                # Write report header
                f.write("Bitcoin Analysis Report\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                # Write price metrics
                f.write("PRICE METRICS\n")
                f.write("-" * 20 + "\n")
                f.write(f"Current Price: ${self.data['Close'].iloc[-1]:,.2f}\n")
                f.write(f"All-Time High: ${self.data['High'].max():,.2f}\n")
                f.write(f"All-Time Low: ${self.data['Low'].min():,.2f}\n")
                f.write(f"30-Day Average: ${self.data['Close'].rolling(30).mean().iloc[-1]:,.2f}\n\n")
                
                # Write return metrics
                f.write("RETURN METRICS\n")
                f.write("-" * 20 + "\n")
                f.write(f"Daily Returns Mean: {self.data['Returns'].mean():.4%}\n")
                f.write(f"Daily Returns Std: {self.data['Returns'].std():.4%}\n")
                f.write(f"Annualized Return: {self.data['Returns'].mean() * 252:.2%}\n")
                f.write(f"Annualized Volatility: {self.data['Returns'].std() * np.sqrt(252):.2%}\n\n")
                
                # Write risk metrics
                f.write("RISK METRICS\n")
                f.write("-" * 20 + "\n")
                f.write(f"Maximum Drawdown: {self.data['Drawdown'].min():.2%}\n")
                f.write(f"Current Drawdown: {self.data['Drawdown'].iloc[-1]:.2%}\n")
                f.write(f"Value at Risk (95%): {self.data['Returns'].quantile(0.05):.2%}\n")
                f.write(f"Value at Risk (99%): {self.data['Returns'].quantile(0.01):.2%}\n\n")
                
                # Write volume metrics
                f.write("VOLUME METRICS\n")
                f.write("-" * 20 + "\n")
                f.write(f"Average Daily Volume: ${self.data['Volume'].mean():,.0f}\n")
                f.write(f"Current Volume: ${self.data['Volume'].iloc[-1]:,.0f}\n")
                f.write(f"Volume Ratio: {self.data['Volume_Ratio'].iloc[-1]:.2f}x\n\n")
                
                # Write recent performance
                f.write("RECENT PERFORMANCE\n")
                f.write("-" * 20 + "\n")
                f.write(f"1-Day Return: {self.data['Returns'].iloc[-1]:.2%}\n")
                f.write(f"7-Day Return: {(self.data['Close'].iloc[-1]/self.data['Close'].iloc[-7] - 1):.2%}\n")
                f.write(f"30-Day Return: {(self.data['Close'].iloc[-1]/self.data['Close'].iloc[-30] - 1):.2%}\n")
            
            print(f"Analysis report saved to {report_path}")
            
        except Exception as e:
            print(f"Error saving data and report: {str(e)}")

def main():
    # Initialize and fetch data
    loader = BitcoinDataLoader()
    data = loader.fetch_data(period="max")
    
    if data is not None:
        # Save data and report
        loader.save_data_and_report()

if __name__ == "__main__":
    main()