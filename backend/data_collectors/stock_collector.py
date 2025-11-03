import requests
import sqlite3
import json
import time
import logging
from datetime import datetime, timezone
import os
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedStockCollector:
    def __init__(self):
        self.db_path = 'stockdb.db'
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        
        # Expanded stock list (matching Twitter collector)
        self.HIGH_VOLUME_STOCKS = [
            'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 
            'META', 'NFLX', 'GME', 'AMC', 'SPY', 'QQQ'
        ]
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize enhanced database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced stock prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                change_percent REAL,
                volume INTEGER,
                timestamp TEXT NOT NULL,
                source TEXT DEFAULT 'api',
                UNIQUE(symbol, timestamp)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
            ON stock_prices(symbol, timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def get_stock_price_finnhub(self, symbol: str) -> Dict:
        """Get real-time stock price from Finnhub"""
        if not self.finnhub_key:
            return None
            
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.finnhub_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'price': data['c'],  # current price
                    'change_percent': data['dp'],  # percent change
                    'volume': data.get('v', 0),  # volume
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source': 'finnhub'
                }
        except Exception as e:
            logger.error(f"Finnhub API error for {symbol}: {e}")
        
        return None
    
    def get_stock_price_alpha_vantage(self, symbol: str) -> Dict:
        """Get stock price from Alpha Vantage (fallback)"""
        if not self.alpha_vantage_key:
            return None
            
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                quote = data.get('Global Quote', {})
                
                if quote:
                    return {
                        'symbol': symbol,
                        'price': float(quote.get('05. price', 0)),
                        'change_percent': float(quote.get('10. change percent', '0%').replace('%', '')),
                        'volume': int(quote.get('06. volume', 0)),
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'source': 'alpha_vantage'
                    }
        except Exception as e:
            logger.error(f"Alpha Vantage API error for {symbol}: {e}")
        
        return None
    
    def get_stock_price_yahoo_fallback(self, symbol: str) -> Dict:
        """Yahoo Finance fallback (free but unofficial)"""
        try:
            # Simple Yahoo Finance scraping as last resort
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                volume = hist['Volume'].iloc[-1]
                
                return {
                    'symbol': symbol,
                    'price': float(current_price),
                    'change_percent': 0,  # Calculate if needed
                    'volume': int(volume),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source': 'yahoo_fallback'
                }
        except Exception as e:
            logger.error(f"Yahoo fallback error for {symbol}: {e}")
        
        return None
    
    def collect_stock_price(self, symbol: str) -> Dict:
        """Collect stock price with multiple API fallbacks"""
        # Try Finnhub first (most reliable for real-time)
        price_data = self.get_stock_price_finnhub(symbol)
        
        # Fallback to Alpha Vantage
        if not price_data:
            price_data = self.get_stock_price_alpha_vantage(symbol)
        
        # Last resort: Yahoo Finance
        if not price_data:
            price_data = self.get_stock_price_yahoo_fallback(symbol)
        
        return price_data
    
    def store_price_data(self, price_data: Dict):
        """Store price data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO stock_prices 
                (symbol, price, change_percent, volume, timestamp, source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                price_data['symbol'],
                price_data['price'],
                price_data.get('change_percent', 0),
                price_data.get('volume', 0),
                price_data['timestamp'],
                price_data['source']
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored {price_data['symbol']}: ${price_data['price']}")
            
        except Exception as e:
            logger.error(f"Database storage error: {e}")
    
    def collect_all_stocks(self):
        """Collect prices for all tracked stocks"""
        successful_collections = 0
        
        for symbol in self.HIGH_VOLUME_STOCKS:
            try:
                price_data = self.collect_stock_price(symbol)
                
                if price_data:
                    self.store_price_data(price_data)
                    successful_collections += 1
                
                # Small delay between requests to be respectful
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error collecting {symbol}: {e}")
        
        logger.info(f"Successfully collected {successful_collections}/{len(self.HIGH_VOLUME_STOCKS)} stocks")
        return successful_collections
    
    def start_continuous_collection(self, interval_minutes=1):
        """Start continuous stock price collection"""
        logger.info(f"Starting continuous stock collection every {interval_minutes} minutes...")
        
        while True:
            try:
                start_time = time.time()
                count = self.collect_all_stocks()
                
                collection_time = time.time() - start_time
                logger.info(f"Collection cycle completed in {collection_time:.2f}s, collected {count} stocks")
                
                # Wait for the remaining time in the interval
                wait_time = max(0, (interval_minutes * 60) - collection_time)
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("Stopping stock collection...")
                break
            except Exception as e:
                logger.error(f"Collection cycle error: {e}")
                time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    collector = EnhancedStockCollector()
    collector.start_continuous_collection(interval_minutes=1)  # Collect every minute