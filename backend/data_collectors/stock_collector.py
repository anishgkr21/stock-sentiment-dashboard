import requests
import time
from datetime import datetime
import sys
import os
# Add parent directory to path so we can import database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal, StockPrice, Base, enginepython simple_stock_test.py

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

class StockDataCollector:
    def __init__(self):
        # Using demo API key for now
        self.api_key = "demo"
        self.base_url = "https://www.alphavantage.co/query"
        self.symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    def fetch_stock_price(self, symbol):
        """Fetch current stock price for a symbol"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "Global Quote" in data:
                quote = data["Global Quote"]
                return {
                    'symbol': symbol,
                    'price': float(quote["05. price"]),
                    'volume': int(quote["06. volume"]),
                    'timestamp': datetime.now()
                }
            else:
                print(f"API response for {symbol}: {data}")
                return None
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def store_stock_data(self, stock_data):
        """Store stock data in database"""
        db = SessionLocal()
        try:
            stock_price = StockPrice(
                symbol=stock_data['symbol'],
                price=stock_data['price'],
                volume=stock_data['volume'],
                timestamp=stock_data['timestamp']
            )
            db.add(stock_price)
            db.commit()
            print(f"Stored {stock_data['symbol']}: ${stock_data['price']}")
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            db.close()
    
    def collect_all_stocks(self):
        """Collect data for all tracked symbols"""
        for symbol in self.symbols:
            stock_data = self.fetch_stock_price(symbol)
            if stock_data:
                self.store_stock_data(stock_data)
            time.sleep(12)  # API rate limiting

if __name__ == "__main__":
    collector = StockDataCollector()
    print("Testing stock data collection...")
    collector.collect_all_stocks()
    print("Test complete!")
