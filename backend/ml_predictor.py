import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime, timedelta
from database import SessionLocal, StockPrice, SentimentData
import pickle

class StockPredictor:
    def __init__(self):
        self.db = SessionLocal()
        self.model = None
        
    def prepare_features(self, symbol, days_back=30):
        """Create features for ML model"""
        cutoff = datetime.now() - timedelta(days=days_back)
        
        # Get stock data
        stocks = self.db.query(StockPrice).filter(
            StockPrice.symbol == symbol,
            StockPrice.timestamp >= cutoff
        ).order_by(StockPrice.timestamp).all()
        
        # Get sentiment data
        sentiments = self.db.query(SentimentData).filter(
            SentimentData.symbol == symbol,
            SentimentData.timestamp >= cutoff
        ).order_by(SentimentData.timestamp).all()
        
        if len(stocks) < 5 or len(sentiments) < 3:
            return None, None
        
        features = []
        targets = []
        
        for i, stock in enumerate(stocks[:-1]):  # Exclude last one for target
            # Price-based features
            price = stock.price
            next_price = stocks[i + 1].price
            price_change = 1 if next_price > price else 0  # Binary: up/down
            
            # Sentiment features (average sentiment in window)
            recent_sentiments = [s.sentiment_score for s in sentiments 
                               if s.timestamp <= stock.timestamp]
            avg_sentiment = np.mean(recent_sentiments[-5:]) if recent_sentiments else 0
            
            # Technical indicators
            volume = stock.volume
            price_momentum = price / stocks[max(0, i-2)].price if i > 2 else 1
            
            features.append([price, avg_sentiment, volume, price_momentum])
            targets.append(price_change)
        
        return np.array(features), np.array(targets)
    
    def train_model(self, symbol):
        """Train prediction model"""
        X, y = self.prepare_features(symbol)
        
        if X is None or len(X) < 10:
            print(f"Not enough data to train model for {symbol}")
            return False
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        
        print(f"Model trained for {symbol}")
        print(f"Accuracy: {accuracy:.3f}")
        print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        
        return True
    
    def predict_direction(self, symbol):
        """Predict if stock will go up or down"""
        if self.model is None:
            print("Model not trained yet")
            return None
        
        # Get latest features
        X, _ = self.prepare_features(symbol, days_back=7)
        if X is None or len(X) == 0:
            return None
        
        # Use most recent data point
        latest_features = X[-1].reshape(1, -1)
        prediction = self.model.predict(latest_features)[0]
        probability = self.model.predict_proba(latest_features)[0]
        
        direction = "UP" if prediction == 1 else "DOWN"
        confidence = max(probability)
        
        return {
            'direction': direction,
            'confidence': confidence,
            'prediction': int(prediction)
        }

if __name__ == "__main__":
    predictor = StockPredictor()
    
    # Train model
    symbol = "AAPL"
    if predictor.train_model(symbol):
        # Make prediction
        result = predictor.predict_direction(symbol)
        if result:
            print(f"\nPrediction for {symbol}:")
            print(f"Direction: {result['direction']}")
            print(f"Confidence: {result['confidence']:.3f}")
    
    predictor.db.close()
    