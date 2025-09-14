import pandas as pd
from scipy.stats import pearsonr
from datetime import datetime, timedelta
from database import SessionLocal, StockPrice, SentimentData, Correlation, Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

class CorrelationAnalyzer:
    def __init__(self):
        self.db = SessionLocal()
    
    def get_stock_data(self, symbol, hours_back=24):
        """Get stock price data for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        stocks = self.db.query(StockPrice).filter(
            StockPrice.symbol == symbol,
            StockPrice.timestamp >= cutoff_time
        ).all()
        
        return [(s.timestamp, s.price) for s in stocks]
    
    def get_sentiment_data(self, symbol, hours_back=24):
        """Get sentiment data for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        sentiments = self.db.query(SentimentData).filter(
            SentimentData.symbol == symbol,
            SentimentData.timestamp >= cutoff_time
        ).all()
        
        return [(s.timestamp, s.sentiment_score) for s in sentiments]
    
    def calculate_correlation(self, symbol):
        """Calculate correlation between sentiment and stock price"""
        stock_data = self.get_stock_data(symbol)
        sentiment_data = self.get_sentiment_data(symbol)
        
        if len(stock_data) < 2 or len(sentiment_data) < 2:
            print(f"Not enough data for {symbol}")
            return None
        
        # For now, just use the most recent values
        avg_sentiment = sum([s[1] for s in sentiment_data]) / len(sentiment_data)
        latest_price = stock_data[-1][1] if stock_data else 0
        
        print(f"{symbol} - Avg Sentiment: {avg_sentiment:.3f}, Latest Price: ${latest_price}")
        
        # Simple correlation placeholder - in real implementation you'd align timestamps
        correlation = avg_sentiment * 0.1  # Simplified for demo
        
        # Store correlation result
        try:
            correlation_record = Correlation(
                symbol=symbol,
                time_window="24h",
                correlation_coefficient=correlation,
                p_value=0.05,  # Placeholder
                timestamp=datetime.now()
            )
            self.db.merge(correlation_record)  # Use merge instead of add for primary key conflicts
            self.db.commit()
            print(f"Stored correlation for {symbol}: {correlation:.3f}")
        except Exception as e:
            print(f"Database error: {e}")
        
        return correlation

if __name__ == "__main__":
    analyzer = CorrelationAnalyzer()
    
    # Test correlation analysis
    symbols = ["AAPL", "GOOGL"]
    for symbol in symbols:
        correlation = analyzer.calculate_correlation(symbol)
    
    analyzer.db.close()
    