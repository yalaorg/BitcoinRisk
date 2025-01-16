# MLModel.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import pickle
import os

class BitcoinRiskModel:
    def __init__(self, csv_path='output/btc_raw_data.csv'):
        """Initialize the ML model"""
        self.data = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
        self.classifiers = {}
        self.regressors = {}
        self.scalers = {}
        
    def create_features(self):
        """Create features for the model"""
        df = self.data.copy()
        
        # Price-based features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close']/df['Close'].shift(1))
        df['Volatility'] = df['Returns'].rolling(window=30).std() * np.sqrt(252)
        
        # Technical indicators
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = self.calculate_rsi(df['Close'])
        
        # Volume features
        df['Volume_MA'] = df['Volume'].rolling(window=30).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        # Price momentum
        df['Price_Momentum'] = df['Close'] / df['Close'].shift(10) - 1
        
        # Volatility features
        for window in [5, 10, 30]:
            df[f'Volatility_{window}d'] = df['Returns'].rolling(window=window).std()
        
        # Create target variables
        df['Risk_Level'] = pd.qcut(df['Volatility'], q=3, labels=['Low', 'Medium', 'High'])
        df['Price_Direction'] = np.where(df['Returns'].shift(-1) > 0, 1, 0)
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def prepare_data(self, df, target_col):
        """Prepare data for modeling"""
        feature_columns = ['Returns', 'Log_Returns', 'Volatility', 
                         'MA5', 'MA20', 'MA50', 'RSI',
                         'Volume_Ratio', 'Price_Momentum',
                         'Volatility_5d', 'Volatility_10d', 'Volatility_30d']
        
        X = df[feature_columns]
        y = df[target_col]
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled, y, scaler, feature_columns
    
    def train_models(self):
        """Train classification and regression models"""
        print("Training models...")
        
        # Prepare data
        df = self.create_features()
        
        # Train Risk Level Classifier
        print("\nTraining Risk Level Classifier...")
        X_risk, y_risk, risk_scaler, risk_features = self.prepare_data(df, 'Risk_Level')
        risk_clf = RandomForestClassifier(n_estimators=100, random_state=42)
        risk_clf.fit(X_risk, y_risk)
        self.classifiers['risk_level'] = risk_clf
        self.scalers['risk_level'] = risk_scaler
        
        # Print feature importance for risk classifier
        risk_importance = pd.DataFrame({
            'feature': risk_features,
            'importance': risk_clf.feature_importances_
        }).sort_values('importance', ascending=False)
        print("\nRisk Level Feature Importance:")
        print(risk_importance)
        
        # Train Price Direction Classifier
        print("\nTraining Price Direction Classifier...")
        X_dir, y_dir, dir_scaler, dir_features = self.prepare_data(df, 'Price_Direction')
        dir_clf = RandomForestClassifier(n_estimators=100, random_state=42)
        dir_clf.fit(X_dir, y_dir)
        self.classifiers['price_direction'] = dir_clf
        self.scalers['price_direction'] = dir_scaler
        
        # Train Volatility Regressor
        print("\nTraining Volatility Regressor...")
        X_vol, y_vol, vol_scaler, vol_features = self.prepare_data(df, 'Volatility')
        vol_reg = GradientBoostingRegressor(n_estimators=100, random_state=42)
        vol_reg.fit(X_vol, y_vol)
        self.regressors['volatility'] = vol_reg
        self.scalers['volatility'] = vol_scaler
        
        # Save models and scalers
        self.save_models()
        
    def save_models(self):
        """Save trained models and scalers to pickle files"""
        if not os.path.exists('output/models'):
            os.makedirs('output/models')
            
        # Save classifiers
        for name, model in self.classifiers.items():
            with open(f'output/models/{name}_classifier.pkl', 'wb') as f:
                pickle.dump(model, f)
            with open(f'output/models/{name}_scaler.pkl', 'wb') as f:
                pickle.dump(self.scalers[name], f)
                
        # Save regressors
        for name, model in self.regressors.items():
            with open(f'output/models/{name}_regressor.pkl', 'wb') as f:
                pickle.dump(model, f)
            with open(f'output/models/{name}_scaler.pkl', 'wb') as f:
                pickle.dump(self.scalers[name], f)
                
        print("\nModels saved in output/models/")
    
    def load_models(self):
        """Load trained models from pickle files"""
        model_dir = 'output/models/'
        
        # Load classifiers
        for name in ['risk_level', 'price_direction']:
            with open(f'{model_dir}{name}_classifier.pkl', 'rb') as f:
                self.classifiers[name] = pickle.load(f)
            with open(f'{model_dir}{name}_scaler.pkl', 'rb') as f:
                self.scalers[name] = pickle.load(f)
                
        # Load regressors
        with open(f'{model_dir}volatility_regressor.pkl', 'rb') as f:
            self.regressors['volatility'] = pickle.load(f)
        with open(f'{model_dir}volatility_scaler.pkl', 'rb') as f:
            self.scalers['volatility'] = pickle.load(f)
    
    def predict(self, input_data):
        """Make predictions using trained models"""
        # Prepare input data
        feature_columns = ['Returns', 'Log_Returns', 'Volatility', 
                         'MA5', 'MA20', 'MA50', 'RSI',
                         'Volume_Ratio', 'Price_Momentum',
                         'Volatility_5d', 'Volatility_10d', 'Volatility_30d']
        
        predictions = {}
        
        # Risk level prediction
        X_risk = self.scalers['risk_level'].transform(input_data[feature_columns])
        predictions['risk_level'] = self.classifiers['risk_level'].predict(X_risk)
        
        # Price direction prediction
        X_dir = self.scalers['price_direction'].transform(input_data[feature_columns])
        predictions['price_direction'] = self.classifiers['price_direction'].predict(X_dir)
        
        # Volatility prediction
        X_vol = self.scalers['volatility'].transform(input_data[feature_columns])
        predictions['volatility'] = self.regressors['volatility'].predict(X_vol)
        
        return predictions

def main():
    # Initialize and train models
    model = BitcoinRiskModel()
    model.train_models()
    
    # Make example prediction
    print("\nMaking example prediction...")
    recent_data = model.create_features().tail(1)
    predictions = model.predict(recent_data)
    
    print("\nPredictions for latest data:")
    print(f"Risk Level: {predictions['risk_level'][0]}")
    print(f"Price Direction: {'Up' if predictions['price_direction'][0] == 1 else 'Down'}")
    print(f"Predicted Volatility: {predictions['volatility'][0]:.2%}")

if __name__ == "__main__":
    main()