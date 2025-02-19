import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # For date formatting
from datetime import datetime, timezone

class BTCDataProcessor:
    def __init__(self, csv_path='output/btc_raw_data.csv'):
        self.csv_path = csv_path
        self.data = self.load_data()
        if self.data is not None:
            self.preprocess_data()
            self.calculate_ahr999_index()

    def load_data(self):
        """Load BTC data from the CSV file."""
        try:
            data = pd.read_csv(self.csv_path)
            print("Data loaded successfully.")
            return data
        except FileNotFoundError:
            print(f"File not found at {self.csv_path}. Please check the path.")
            return None
        except Exception as e:
            print(f"An error occurred while loading the data: {e}")
            return None

    def preprocess_data(self):
        """Preprocess the BTC data."""
        # Convert 'Date' column to datetime
        if 'Date' in self.data.columns:
            self.data['Date'] = pd.to_datetime(self.data['Date'])
        
        # Check if 'Date' is timezone-aware
        is_tz_aware = self.data['Date'].dt.tz is not None
        
        # Calculate Bitcoin age in days (since 2009-01-03)
        if is_tz_aware:
            # If 'Date' is timezone-aware, make bitcoin_birthday timezone-aware
            bitcoin_birthday = datetime(2009, 1, 3, tzinfo=timezone.utc)
        else:
            # If 'Date' is timezone-naive, make bitcoin_birthday timezone-naive
            bitcoin_birthday = datetime(2009, 1, 3)
        
        self.data['Bitcoin_Age'] = (self.data['Date'] - bitcoin_birthday).dt.days
        
        # Fill missing values
        self.data.fillna(method='ffill', inplace=True)
        print("Data preprocessing completed.")

    def calculate_exponential_growth(self):
        """Calculate the exponential growth valuation of Bitcoin."""
        # Formula: price = 10^(5.84 * log10(bitcoin_age) - 17.01)
        self.data['Exponential_Growth'] = 10 ** (5.84 * np.log10(self.data['Bitcoin_Age']) - 17.01)

    def calculate_200d_sma_cost(self):
        """Calculate the 200-day simple moving average (SMA) cost."""
        self.data['200d_SMA_Cost'] = self.data['Close'].rolling(window=200).mean()

    def calculate_ahr999_index(self):
        """Calculate the ahr999 index."""
        # Calculate exponential growth valuation
        self.calculate_exponential_growth()
        
        # Calculate 200-day SMA cost
        self.calculate_200d_sma_cost()
        
        # Calculate ahr999 index
        self.data['ahr999_Index'] = (self.data['Close'] / self.data['200d_SMA_Cost']) * \
                                    (self.data['Close'] / self.data['Exponential_Growth'])
        print("ahr999 index calculation completed.")

    def plot_ahr999_index(self):
        """Plot Bitcoin price and ahr999 index on the same graph with dual y-axis."""
        if 'ahr999_Index' not in self.data.columns:
            print("ahr999 index not calculated. Please run calculate_ahr999_index() first.")
            return
        
        # Create a figure and primary axis
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Plot Bitcoin price on the primary y-axis
        ax1.plot(self.data['Date'], self.data['Close'], label='Bitcoin Price', color='red')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Bitcoin Price (USD)', color='red')
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.legend(loc='upper left')
        
        # Create a secondary y-axis for the ahr999 index
        ax2 = ax1.twinx()
        ax2.plot(self.data['Date'], self.data['ahr999_Index'], label='ahr999 Index', color='blue')
        ax2.set_ylabel('ahr999 Index', color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        
        # Add horizontal lines for ahr999 index zones
        ax2.axhline(y=0.45, color='green', linestyle='--', label='Buy Zone (ahr999 < 0.45)')
        ax2.axhline(y=1.2, color='orange', linestyle='--', label='Accumulation Zone (0.45 < ahr999 < 1.2)')
        ax2.axhline(y=5, color='purple', linestyle='--', label='Waiting Zone (1.2 < ahr999 < 5)')
        ax2.legend(loc='upper right')
        
        # Customize x-axis to show yearly ticks
        ax1.xaxis.set_major_locator(mdates.YearLocator())  # Show ticks for each year
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Format as 'YYYY'
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        
        # Title
        plt.title('Bitcoin Price and ahr999 Index')
        
        # Show the plot
        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == "__main__":
    btc_processor = BTCDataProcessor(csv_path='output/btc_raw_data.csv')
    btc_processor.plot_ahr999_index()