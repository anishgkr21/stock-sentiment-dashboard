from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for now (easier setup)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stockdb.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class StockPrice(Base):
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    price = Column(Float)  # Changed from Decimal to Float
    volume = Column(BigInteger)
    timestamp = Column(DateTime)

class SentimentData(Base):
    __tablename__ = "sentiment_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    text = Column(Text)
    sentiment_score = Column(Float)  # Changed from Decimal to Float
    source = Column(String(20))
    timestamp = Column(DateTime)

class Correlation(Base):
    __tablename__ = "correlations"
    
    symbol = Column(String(10), primary_key=True)
    time_window = Column(String(10), primary_key=True)
    correlation_coefficient = Column(Float)  # Changed from Decimal to Float
    p_value = Column(Float)  # Changed from Decimal to Float
    timestamp = Column(DateTime)
    