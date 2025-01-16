import pandas as pd
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
import json

class CryptoRiskManagementModel:
    def __init__(self, lookback_years=7, confidence_level=0.99,
                 max_drawdown_threshold=-0.20,  # Adjusted for crypto volatility
                 min_liquidity_ratio=2.0,       # Increased for crypto
                 margin_call_threshold=0.75):    # More conservative for crypto
        """
        Initialize risk management model with crypto-specific parameters
        
        Parameters:
        - lookback_years: Historical data period for model training
        - confidence_level: VaR confidence level
        - max_drawdown_threshold: Maximum allowed drawdown
        - min_liquidity_ratio: Minimum required liquidity ratio
        - margin_call_threshold: Threshold for margin calls
        """
        self.lookback_years = lookback_years
        self.confidence_level = confidence_level
        self.max_drawdown_threshold = max_drawdown_threshold
        self.min_liquidity_ratio = min_liquidity_ratio
        self.margin_call_threshold = margin_call_threshold
        
        # Crypto-specific parameters
        self.btc_volatility_multiplier = 1.5  # Additional safety factor for BTC
        self.max_leverage = 5.0               # Maximum allowed leverage
        self.min_collateral_btc = 0.1        # Minimum BTC collateral
        
        # Model state variables
        self.historical_data = self.load_bitcoin_history()
        self.var_model = None
        self.volatility_model = None
    
    def load_bitcoin_history(self):
        """Load historical Bitcoin price data"""
        # Example of loading historical data - in practice, you'd fetch from an API
        # This simulates 7 years of daily data
        dates = pd.date_range(end=datetime.now(), periods=365*7, freq='D')
        np.random.seed(42)  # For reproducibility
        
        # Simulate Bitcoin's historical volatility and trend
        returns = np.random.normal(0.0005, 0.03, len(dates))  # Daily returns
        price = 1000 * np.exp(np.cumsum(returns))  # Starting from $1000
        
        return pd.DataFrame({
            'price': price,
            'volume': np.random.lognormal(10, 1, len(dates)),
            'returns': returns
        }, index=dates)
    
    def calculate_crypto_var(self, portfolio_value, btc_position):
        """Calculate Value at Risk specifically for crypto positions"""
        returns = self.historical_data['returns'].dropna()
        # Use longer left tail for crypto VaR
        var = np.percentile(returns, (1 - self.confidence_level) * 100) * self.btc_volatility_multiplier
        return portfolio_value * var
    
    def calculate_margin_requirements(self, btc_position_value, current_volatility):
        """Calculate required margin based on BTC position value and current volatility"""
        # Higher base margin for crypto
        base_margin = btc_position_value * 0.2  
        volatility_adjustment = current_volatility * btc_position_value * self.btc_volatility_multiplier
        
        # Ensure margin doesn't exceed position value
        return min(base_margin + volatility_adjustment, btc_position_value)
    
    def check_liquidation_risk(self, account_value, margin_used, 
                             available_credit, time_to_repay,
                             current_btc_price):
        """
        Check if BTC position faces liquidation risk
        Returns: (risk_level, required_action)
        """
        liquidity_ratio = (account_value + available_credit) / margin_used
        
        # Calculate additional metrics for crypto
        leverage = margin_used / account_value
        btc_exposure = margin_used / current_btc_price
        
        if leverage > self.max_leverage:
            return "CRITICAL", "Leverage exceeds maximum allowed"
            
        if liquidity_ratio < self.margin_call_threshold:
            if time_to_repay > 2:  # More than 2 days to repay
                return "HIGH", f"Margin call issued - {time_to_repay:.1f} days to repay"
            else:
                return "CRITICAL", "Immediate liquidation risk - add collateral"
        
        elif liquidity_ratio < self.min_liquidity_ratio:
            return "MEDIUM", "Increase collateral or reduce exposure"
            
        return "LOW", "Position within risk limits"
    
    def backtest_strategy(self, initial_capital, btc_position, start_date, end_date):
        """
        Backtest risk management strategy with Bitcoin positions
        Returns performance metrics and risk events
        """
        portfolio = pd.DataFrame(index=self.historical_data.loc[start_date:end_date].index)
        portfolio['value'] = initial_capital
        portfolio['btc_exposure'] = btc_position
        
        risk_events = []
        
        for date in portfolio.index[1:]:
            # Daily mark-to-market
            btc_return = self.historical_data.loc[date, 'returns']
            portfolio_return = btc_return * (portfolio.loc[date-1, 'btc_exposure'])
            portfolio.loc[date, 'value'] = portfolio.loc[date-1, 'value'] * (1 + portfolio_return)
            
            # Check for risk events
            drawdown = (portfolio.loc[date, 'value'] - initial_capital) / initial_capital
            if drawdown < self.max_drawdown_threshold:
                risk_events.append({
                    'date': date,
                    'type': 'Max Drawdown Exceeded',
                    'value': drawdown
                })
        
        return {
            'final_value': portfolio.iloc[-1]['value'],
            'max_drawdown': (portfolio['value'] / portfolio['value'].cummax() - 1).min(),
            'sharpe_ratio': portfolio['value'].pct_change().mean() / 
                           portfolio['value'].pct_change().std() * np.sqrt(252),
            'risk_events': risk_events
        }
    
    def get_repayment_schedule(self, margin_call_amount, account_value, 
                             daily_income, max_days=5):
        """Calculate optimal repayment schedule to avoid liquidation"""
        # More conservative repayment schedule for crypto
        available_daily = daily_income * 0.6  # Reduced from 0.7 for additional safety
        min_days_required = np.ceil(margin_call_amount / available_daily)
        
        if min_days_required > max_days:
            return None  # Cannot generate viable repayment schedule
            
        # Add buffer for crypto volatility
        buffer_amount = margin_call_amount * 0.1
        
        return {
            'daily_payment': (margin_call_amount + buffer_amount) / min_days_required,
            'days_required': min_days_required,
            'total_amount': margin_call_amount + buffer_amount,
            'buffer_included': buffer_amount
        }

    def stress_test_crypto(self, btc_position, scenarios):
        """Run stress tests under different crypto market scenarios"""
        results = []
        current_price = self.historical_data['price'].iloc[-1]
        
        for scenario in scenarios:
            price_shock = scenario['price_shock']
            vol_shock = scenario.get('volatility_shock', 0)
            
            shocked_value = btc_position * (1 + price_shock)
            shocked_volatility = self.historical_data['returns'].std() * (1 + vol_shock)
            
            margin_call_prob = self.estimate_margin_call_probability(
                shocked_value, shocked_volatility)
            
            results.append({
                'scenario': scenario['name'],
                'portfolio_impact': (shocked_value - btc_position) / btc_position,
                'margin_call_probability': margin_call_prob,
                'required_additional_margin': self.calculate_margin_requirements(
                    shocked_value, shocked_volatility) - btc_position
            })
        return results
    
    def estimate_margin_call_probability(self, position_value, current_volatility):
        """Estimate probability of margin call under current conditions"""
        # Adjusted for crypto's fat-tailed distribution
        var_99 = self.calculate_crypto_var(position_value, position_value)
        return norm.cdf(-self.margin_call_threshold, 
                       loc=position_value * current_volatility * np.sqrt(252),
                       scale=abs(var_99))

def main():
    # Initialize model with crypto-specific parameters
    model = CryptoRiskManagementModel(
        lookback_years=7,
        confidence_level=0.99,
        max_drawdown_threshold=-0.20,
        min_liquidity_ratio=2.0,
        margin_call_threshold=0.75
    )
    
    # Example usage with Bitcoin position
    btc_position = 10.0  # BTC
    current_btc_price = 42000  # USD
    position_value = btc_position * current_btc_price
    
    # Run crypto-specific stress tests
    scenarios = [
        {
            'name': 'Major Crash',
            'price_shock': -0.40,
            'volatility_shock': 2.0
        },
        {
            'name': 'Moderate Correction',
            'price_shock': -0.20,
            'volatility_shock': 1.5
        },
        {
            'name': 'Bull Run',
            'price_shock': 0.30,
            'volatility_shock': 1.0
        }
    ]
    
    stress_test_results = model.stress_test_crypto(position_value, scenarios)
    
    # Check liquidation risk
    risk_level, action = model.check_liquidation_risk(
        account_value=position_value,
        margin_used=position_value * 0.5,  # 50% margin used
        available_credit=position_value * 0.2,
        time_to_repay=3,
        current_btc_price=current_btc_price
    )
    
    # Calculate repayment schedule if needed
    if risk_level in ['HIGH', 'CRITICAL']:
        repayment_schedule = model.get_repayment_schedule(
            margin_call_amount=position_value * 0.1,  # 10% margin call
            account_value=position_value,
            daily_income=position_value * 0.02  # Assuming 2% daily income
        )
        print(f"Repayment Schedule: {repayment_schedule}")

if __name__ == "__main__":
    main()