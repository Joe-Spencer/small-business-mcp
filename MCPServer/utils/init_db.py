from sqlalchemy import create_engine
from ..models.database import Base
from ..config.database import DATABASE_URL

def init_db():
    """Initialize the database by creating all tables"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 