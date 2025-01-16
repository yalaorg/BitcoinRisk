# api_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from MLModel import BitcoinRiskModel
import uvicorn
from typing import List, Dict
from datetime import datetime

app = FastAPI(
    title="Bitcoin Risk Analysis API",
    description="API for Bitcoin risk prediction and analysis",
    version="1.0.0"
)

# Initialize the model
model = BitcoinRiskModel()
try:
    model.load_models()
    print("Models loaded successfully")
except Exception as e:
    print(f"Error loading models: {str(e)}")
    print("Training new models...")
    model.train_models()

class PriceData(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class RiskPredictionResponse(BaseModel):
    timestamp: str
    risk_level: str
    price_direction: str
    predicted_volatility: float
    confidence_scores: Dict[str, float]

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Bitcoin Risk Analysis API",
        "version": "1.0.0",
        "status": "active"
    }

@app.post("/predict/risk", response_model=RiskPredictionResponse)
async def predict_risk(data: PriceData):
    """
    Predict risk metrics for given price data
    
    Args:
        data: Price data including OHLCV values
    
    Returns:
        Risk predictions including risk level, price direction, and volatility
    """
    try:
        # Convert input data to DataFrame
        df = pd.DataFrame([{
            'Open': data.open,
            'High': data.high,
            'Low': data.low,
            'Close': data.close,
            'Volume': data.volume
        }], index=[pd.to_datetime(data.timestamp)])
        
        # Create features
        features_df = model.create_features()
        
        # Get predictions
        predictions = model.predict(features_df.tail(1))
        
        # Get confidence scores
        confidence_scores = {
            'risk_level': float(model.classifiers['risk_level'].predict_proba(
                model.scalers['risk_level'].transform(features_df.tail(1)[model.feature_columns])
            ).max()),
            'price_direction': float(model.classifiers['price_direction'].predict_proba(
                model.scalers['price_direction'].transform(features_df.tail(1)[model.feature_columns])
            ).max())
        }
        
        return RiskPredictionResponse(
            timestamp=data.timestamp,
            risk_level=predictions['risk_level'][0],
            price_direction='Up' if predictions['price_direction'][0] == 1 else 'Down',
            predicted_volatility=float(predictions['volatility'][0]),
            confidence_scores=confidence_scores
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info")
async def model_info():
    """Get information about the trained models"""
    try:
        # Get feature importances
        risk_importance = pd.DataFrame({
            'feature': model.feature_columns,
            'importance': model.classifiers['risk_level'].feature_importances_
        }).sort_values('importance', ascending=False)
        
        return {
            "models": {
                "risk_level": {
                    "type": str(type(model.classifiers['risk_level']).__name__),
                    "n_features": len(model.feature_columns),
                    "feature_importance": risk_importance.to_dict(orient='records')
                },
                "price_direction": {
                    "type": str(type(model.classifiers['price_direction']).__name__),
                    "n_features": len(model.feature_columns)
                },
                "volatility": {
                    "type": str(type(model.regressors['volatility']).__name__),
                    "n_features": len(model.feature_columns)
                }
            },
            "features": model.feature_columns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/model/retrain")
async def retrain_model():
    """Retrain the models with latest data"""
    try:
        model.train_models()
        return {"message": "Models retrained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start():
    """Start the API server"""
    uvicorn.run("api_service:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()