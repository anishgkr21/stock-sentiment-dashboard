from database import Base, engine, SessionLocal
from datetime import datetime

print("Testing database connection...")

# Create tables
Base.metadata.create_all(bind=engine)

# Test database connection
db = SessionLocal()
print("✅ Database connection successful!")
print("✅ Tables created successfully!")
db.close()
