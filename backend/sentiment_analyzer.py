import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
from database import SessionLocal, SentimentData, Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text, symbol, source="manual"):
        """Analyze sentiment of text and store in database"""
        scores = self.analyzer.polarity_scores(text)
        compound_score = scores['compound']  # Overall sentiment (-1 to 1)
        
        # Store in database
        db = SessionLocal()
        try:
            sentiment_data = SentimentData(
                symbol=symbol,
                text=text,
                sentiment_score=compound_score,
                source=source,
                timestamp=datetime.now()
            )
            db.add(sentiment_data)
            db.commit()
            print(f"Stored sentiment for {symbol}: {compound_score:.3f} - {text[:50]}...")
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            db.close()
        
        return compound_score

if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # Test with sample texts
    test_texts = [
        ("AAPL", "Apple stock is performing amazing! Great earnings report."),
        ("AAPL", "Apple disappointed with weak iPhone sales this quarter."),
        ("GOOGL", "Google's AI advancements are revolutionary and impressive."),
    ]
    
    for symbol, text in test_texts:
        score = analyzer.analyze_text(text, symbol)
        print(f"{symbol}: {score:.3f}")