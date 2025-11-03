import tweepy
import json
import redis
import sqlite3
from datetime import datetime, timezone
import os
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterCollector:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        # Twitter API setup
        
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not self.bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN environment variable not set")
        
        self.client = tweepy.Client(bearer_token=self.bearer_token)
        
        # Redis setup for message queue
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True
            )
        except:
            logger.warning("Redis not available, using SQLite for queuing")
            self.redis_client = None
        
        # SQLite fallback
        self.db_path = 'stockdb.db'
        
        # Sentiment analyzer
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Expanded stock list
        self.HIGH_VOLUME_STOCKS = [
            'TSLA', 'AAPL', 'GME', 'AMC', 'MSFT', 'NVDA', 
            'GOOGL', 'AMZN', 'META', 'NFLX', 'SPY', 'QQQ'
        ]
        
        self.COMPANY_MAPPINGS = {
            'Tesla': 'TSLA',
            'Apple': 'AAPL',
            'GameStop': 'GME',
            'Microsoft': 'MSFT',
            'Nvidia': 'NVDA',
            'Google': 'GOOGL',
            'Amazon': 'AMZN',
            'Meta': 'META',
            'Netflix': 'NFLX'
        }
    
    def build_search_query(self):
        """Build Twitter search query without cashtags (for basic API access)"""
    
        # Use only company names and stock symbols (no $ prefix)
        search_terms = [
            "Apple stock", "AAPL", 
            "Tesla stock", "TSLA",
            "Microsoft stock", "MSFT",
            "Google stock", "GOOGL", 
            "Amazon stock", "AMZN",
            "GameStop stock", "GME",
            "Nvidia stock", "NVDA"
        ]
        
        # Join with OR and add filters for quality
        query = " OR ".join(search_terms)
        query += " -is:retweet lang:en"
        
        # Keep under 512 character limit
        if len(query) > 500:
            # Use only top stocks if query too long
            priority_terms = ["Apple stock", "Tesla stock", "Microsoft stock", "TSLA", "AAPL", "MSFT"]
            query = " OR ".join(priority_terms) + " -is:retweet lang:en"
        
        return query
    
    def extract_stock_symbols(self, tweet_text):
        """Extract stock symbols mentioned in tweet"""
        symbols = []
        tweet_upper = tweet_text.upper()
        
        # Check for cashtags
        for symbol in self.HIGH_VOLUME_STOCKS:
            if f"${symbol}" in tweet_text or symbol in tweet_upper:
                symbols.append(symbol)
        
        # Check for company names
        for company, symbol in self.COMPANY_MAPPINGS.items():
            if company.lower() in tweet_text.lower():
                symbols.append(symbol)
        
        return list(set(symbols))  # Remove duplicates
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of tweet text"""
        scores = self.analyzer.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'neutral': scores['neu'],
            'negative': scores['neg']
        }
    
    def process_tweet(self, tweet):
        """Process a single tweet for sentiment and symbols"""
        tweet_data = {
            'tweet_id': tweet.id,
            'text': tweet.text,
            'created_at': tweet.created_at.isoformat(),
            'author_id': tweet.author_id,
            'public_metrics': tweet.public_metrics
        }
        
        # Extract stock symbols
        symbols = self.extract_stock_symbols(tweet.text)
        
        if not symbols:
            return None
        
        # Analyze sentiment
        sentiment = self.analyze_sentiment(tweet.text)
        
        # Create processed data for each symbol
        processed_tweets = []
        for symbol in symbols:
            processed_data = {
                'symbol': symbol,
                'sentiment_score': sentiment['compound'],
                'sentiment_breakdown': sentiment,
                'tweet_data': tweet_data,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
            processed_tweets.append(processed_data)
        
        return processed_tweets
    
    def queue_sentiment_data(self, processed_tweets):
        """Queue processed sentiment data"""
        for tweet_data in processed_tweets:
            symbol = tweet_data['symbol']
            
            if self.redis_client:
                # Use Redis if available
                try:
                    self.redis_client.lpush(
                        f"sentiment:{symbol}", 
                        json.dumps(tweet_data)
                    )
                    # Keep only last 1000 items per symbol
                    self.redis_client.ltrim(f"sentiment:{symbol}", 0, 999)
                except Exception as e:
                    logger.error(f"Redis error: {e}")
                    self._store_in_sqlite(tweet_data)
            else:
                # Fallback to SQLite
                self._store_in_sqlite(tweet_data)
    
    def _store_in_sqlite(self, tweet_data):
        """Store sentiment data in SQLite as fallback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sentiment_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    sentiment_score REAL NOT NULL,
                    tweet_data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    processed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                INSERT INTO sentiment_queue 
                (symbol, sentiment_score, tweet_data, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                tweet_data['symbol'],
                tweet_data['sentiment_score'],
                json.dumps(tweet_data),
                tweet_data['timestamp']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"SQLite storage error: {e}")
    
    def collect_recent_tweets(self, max_results=100):
        """Collect recent tweets mentioning our stocks"""
        query = self.build_search_query()
        logger.info(f"Searching tweets with query: {query}")
        
        try:
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics'],
                max_results=max_results
            ).flatten(limit=max_results)
            
            processed_count = 0
            for tweet in tweets:
                processed_tweets = self.process_tweet(tweet)
                if processed_tweets:
                    self.queue_sentiment_data(processed_tweets)
                    processed_count += len(processed_tweets)
            
            logger.info(f"Processed {processed_count} sentiment data points")
            return processed_count
            
        except tweepy.TooManyRequests:
            logger.warning("Twitter API rate limit reached")
            return 0
        except Exception as e:
            logger.error(f"Twitter collection error: {e}")
            return 0
    
    def start_streaming(self):
        """Start continuous tweet collection"""
        logger.info("Starting Twitter sentiment collection...")
        
        while True:
            try:
                count = self.collect_recent_tweets(100)
                logger.info(f"Collected batch of {count} sentiment points")
                
                # Wait 15 minutes between batches to respect rate limits
                import time
                time.sleep(900)  # 15 minutes
                
            except KeyboardInterrupt:
                logger.info("Stopping Twitter collection...")
                break
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                import time
                time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    collector = TwitterCollector()
    collector.start_streaming()
